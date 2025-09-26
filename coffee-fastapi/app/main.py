from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import dialogue, user
from .dependencies import coffeedb
from .llm_multimcp import mcp_client
import os
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:10533"],  # 前端地址
    #allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有头部
)
app.include_router(dialogue.router)
app.include_router(user.router)

@app.on_event("startup")
async def startup():
    try:
        await coffeedb.connect()
        print("启动时MongoDB成功连接")
    except Exception as e:
        print(f"MongoDB在启动时连接失败:{e}")
        raise RuntimeError("启动时无法连接到MongoDB")
    
    try:
        await mcp_client.connect_to_all_servers()
        print("启动时mcp server成功连接")
    except Exception as e:
        print(f"启动时mcp server连接失败:{e}")
        raise RuntimeError("启动时无法连接到mcp server")

@app.on_event("shutdown")
async def shutdown():
    await coffeedb.disconnection()
    print("服务器关闭，MongoDB断开连接")
    await mcp_client.cleanup_all()
    print("服务器关闭，mcp server断开连接")