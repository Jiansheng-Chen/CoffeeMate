import os
import chromadb
from chromadb.config import Settings
import requests
import json
from typing import List, Dict, Optional
import logging
from Config import config
from openai import OpenAI
# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class EmbeddingClient:  
    def __init__(self):
        self.api_key = config.get("API_KEY")
        self.base_url = config.get("BASE_URL")
        self.model = config.get("EMBEDDING_MODEL")
        self.client = OpenAI(api_key = self.api_key, base_url = self.base_url)

    def get_embeddings_batch(self, chunks: list[str] ) -> List[List[float]]:
        completion = self.client.embeddings.create(
            model=self.model,
            input=chunks,
        )
        result = completion.model_dump()
        embeddings = [embedding["embedding"] for embedding in result['data']]
        return embeddings
    
    def get_embedding_single_string(self, text : str ) -> List[float]:
        completion = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        result = completion.model_dump()
        embedding = result["data"][0]["embedding"]
        return embedding