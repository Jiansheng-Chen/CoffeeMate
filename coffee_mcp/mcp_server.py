from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from typing import Annotated
from pydantic import Field
from rag_client import RAGSystem
from embedding import EmbeddingClient
from Config import config
mcp=FastMCP(name=config.get("MCP_NAME"), host=config.get("MCP_HOST"), port=config.get("MCP_PORT"))
rag_client_coffee_beans_global = RAGSystem("coffee-beans-global", "./rag_corpus/coffee-beans-global.txt")
rag_client_coffee_baking_health = RAGSystem("coffee-baking-health", "./rag_corpus/coffee-baking-health.txt")
rag_client_coffee_history_cultral = RAGSystem("coffee-history-cultral", "./rag_corpus/coffee-history-cultural.txt")
rag_client_coffee_flavor_chemical = RAGSystem("chemical-explanation-of-coffee-flavor", "./rag_corpus/chemical-explanation-of-coffee-flavor.txt")

embedding_client = EmbeddingClient()

@mcp.tool(description="查询向量数据库，该数据库包含全世界某个地区的主要的咖啡品种和风味")
async def get_coffee_beans_info_in_certain_area(query: str, topn : int = 3) -> str:
    
    result = rag_client_coffee_beans_global.query(query, topn)
    return result

@mcp.tool(description="查询向量数据库，该数据库包含咖啡烘焙入门以及咖啡对健康的好处")
async def get_coffee_baking_health_info(query : str, topn : int = 3) -> str:
    
    result = rag_client_coffee_baking_health.query(query, topn)
    return result

@mcp.tool(description="查询向量数据库，该数据库包含咖啡历史和文化相关信息")
async def get_coffee_history_cultral(query : str, topn : int =3) -> str:
    result = rag_client_coffee_history_cultral.query(query, topn)
    return result

@mcp.tool(description="查询向量数据库，该数据库包含咖啡风味的化学解释")
async def get_chemical_explanation_of_coffee_flavor(query : str, topn : int =3) -> str:
    result = rag_client_coffee_flavor_chemical.query(query, topn)
    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http")