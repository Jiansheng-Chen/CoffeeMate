import asyncio
from typing import Optional, Any, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import sys
import json
from .Config import config

class MCPClient:
    def __init__(self, server_dict : Dict):
        self.server_dict : Dict[str, str] = server_dict#{server_name : server_url, ...]这种形式的dict
        self.connections : Dict[str, Dict[str, Any]] = {}
        self.client = AsyncOpenAI(
            api_key=config.get("LLM_API_KEY"),
            base_url=config.get("Base_URL"),
        )#使用异步openai，因为后面要流式输出，异步的话可以用异步迭代，不会阻塞，并发性能更好。
        self.model=config.get("Model")

    async def connect_to_server(self, server_name: str, server_url: str):
        
        try:
            exit_stack = AsyncExitStack()
            stdio_transport = await exit_stack.enter_async_context(streamablehttp_client(server_url))
            read, write, _ = stdio_transport
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            lock = asyncio.Lock()
            response=None
            async with lock:
                response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to server ({server_name}, {server_url}) with tools:", [tool.name for tool in tools])
            tools_openai = [ await self._convert_tool(server_name, tool) for tool in tools]
            
            self.connections[server_name] = {
                "server_url" : server_url,
                "session" : session,
                "lock" : lock,
                "read" : read,
                "write" : write,
                "exit_stack" : exit_stack,
                "tools_openai" : tools_openai,
            }
        except Exception as e:
            # 出错时清理资源
            await exit_stack.__aexit__(type(e), e, e.__traceback__)
            raise

    async def connect_to_all_servers(self):
        for server_name, server_url in self.server_dict.items():
            await self.connect_to_server(server_name, server_url)
        print("successfully connect to all mcp_servers")


    async def _convert_tool(self, server_name : str, mcp_tool: dict[str, Any]) -> dict[str, Any]:
        """将 MCP 工具格式转为 OpenAI tools 格式"""

        return {
            "type": "function",
            "function": {
                "name": f"{server_name}::{mcp_tool.name}",#加个servername::前缀区分不同server同名tool
                "description": mcp_tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_key: {
                            "type": param_value.get("type", "string"),
                            "description": param_value.get("description", ""),
                        }
                        for param_key, param_value in mcp_tool.inputSchema.get("properties",{}).items()
                    },
                    "required": mcp_tool.inputSchema.get("required", []),
                }
            }
        }

    async def get_all_tools_in_openai_schema(self):
        tools_in_openai_schema = []
        for server_name, server_attr in self.connections.items():       
            tools_in_openai_schema.extend(self.connections["tools_opneai"])
        return tools_in_openai_schema
    
    async def call_tool(self, tool_name, tool_args, tool_call_id):
        server_name, ori_tool_name = tool_name.split("::")
        lock = self.connections[server_name]["lock"]
        session = self.connections[server_name]["session"]
        async with lock:
            print(f"[Calling tool {ori_tool_name} of server {server_name} with args : {tool_args}]")
            call_tool_response = await session.call_tool(ori_tool_name, tool_args)
            print(f"[Calling tool response: {call_tool_response}]")
            message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": call_tool_response.model_dump_json(),
            }
            return message


    async def get_response(self, messages: list[dict]) -> list[dict]:
        
        openai_tools = self.get_all_tools_in_openai_schema()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=openai_tools,
            tool_choice="auto",
            stream=True,
            parallel_tool_calls=True,
        )

        full_content = ""
        tool_calls = {}
        async for chunk in response:
            delta = chunk.choices[0].delta
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index not in tool_calls:
                        tool_calls[tc.index] = tc
                    else:
                        tool_calls[tc.index].function.arguments += tc.function.arguments
                
                
            elif delta.content:
                full_content += delta.content
                yield delta.content



        tool_calls_list=[]
        if tool_calls:
            tool_calls_list = [tool_calls[i] for i in sorted(tool_calls.keys())]
            messages.append({
                "content" : "",
                "role" : "assistant",
                "tool_calls" : tool_calls_list,
            })

            for tool_call in tool_calls_list:
                tool_name = tool_call.function.name
                try:
                    #print(f"tool_calls_test:{tool_call.function.arguments}")
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    tool_args = {}
                #print(f"[Calling tool: {tool_name} with {tool_args}]")
                result = await self.call_tool(tool_name, tool_args, tool_call.id)
                messages.append(result)
                
            async for content in self.get_response(messages):
                yield content
    
    async def cleanup_all(self):
        for server_name, server_attr in self.connections.items():
            await server_attr["exit_stack"].aclose()
            print(f"disconnect from {server_name} : {server_attr['server_url']}")
        print(f"disconnect from all mcp_server")
        self.connections=None
        self.server_dict=None
mcp_client=MCPClient(config.get("MCP_SERVER"))