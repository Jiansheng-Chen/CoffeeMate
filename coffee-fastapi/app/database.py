from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
import logging
from .Config import config
class CoffeeDB:
    def __init__(self):
        self.connection_string = config.get("MongoDB_URI")
        self.client: AsyncIOMotorClient = None
        self.db = None
        self.db_name = config.get("MongoDB_db_name")
    
    async def connect(self):
        if not self.client:
            try:
                self.client = AsyncIOMotorClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,  
                    connectTimeoutMS=5000,
                    maxPoolSize = 100,
                    socketTimeoutMS=30000
                )
                self.db = self.client[self.db_name]
                #print(self.connection_string)
                await self.db.command('ping')
                logging.info("MongoDB连接成功")
                print(("MongoDB连接成功"))
            except Exception as e:
                
                logging.error(f"MongoDB连接失败：{e}")
                raise
    
    async def disconnection(self):
        if self.client:
            self.client.close()
            self.client=None
            self.db = None
            logging.info("MongoDB连接已关闭")
