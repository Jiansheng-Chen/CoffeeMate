import asyncio
from typing import Optional, Any
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from dotenv import load_dotenv
from openai import AsyncOpenAI
import os
import sys
import json

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )#使用异步openai，因为后面要流式输出，异步的话可以用异步迭代，不会阻塞，并发性能更好。
        self.model="qwen-plus"
        self._lock = asyncio.Lock()

    async def connect_to_server(self, server_url: str):
        
        stdio_transport = await self.exit_stack.enter_async_context(streamablehttp_client(server_url))
        self.read, self.write, _ = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))
        await self.session.initialize()
        response=None
        async with self._lock:
            response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])
    
    async def _convert_tool(self, mcp_tool: dict[str, Any]) -> dict[str, Any]:
        """将 MCP 工具格式转为 OpenAI tools 格式"""

        return {
            "type": "function",
            "function": {
                "name": mcp_tool.name,
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

    async def get_response(self, messages: list[dict]) -> list[dict]:
        mcp_tools = None
        async with self._lock:
            mcp_tools = await self.session.list_tools()
        openai_tools=[await self._convert_tool(mcp_tool) for mcp_tool in mcp_tools.tools]
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
                
                # for tc in delta.tool_calls:
                #     if tc.function and tc.function.name:
                #         tool_calls.append(tc)
                #     elif tc.function and tc.function.arguments:
                #         if tool_calls:
                #             tool_calls[-1].function.arguments += tc.function.arguments
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
                print(f"[Calling tool: {tool_name} with {tool_args}]")
                async with self._lock:
                    call_tool_response = await self.session.call_tool(tool_name, tool_args)
                    print(f"[Calling tool response: {call_tool_response}]")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": call_tool_response.model_dump_json(),
                    })
            async for content in self.get_response(messages):
                yield content
    
    async def cleanup(self):
        await self.exit_stack.aclose()

mcp_client=MCPClient()



# async def main():
#     if len(sys.argv) < 2:
#         print("Usage: python client.py <path_to_server_script>")
#         sys.exit(1)
#     else:
#         client = MCPClient()
#         try:
#             await client.connect_to_server(sys.argv[1])
#             await client.chat()
#         finally:
#             await client.cleanup()

