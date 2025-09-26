import os
import chromadb
from chromadb.config import Settings
import requests
import json
from typing import List, Dict, Optional
import logging
from Config import config
from openai import OpenAI
from embedding import EmbeddingClient
from pathlib import Path 
from langchain.text_splitter import RecursiveCharacterTextSplitter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self, collection_name: str = "rag_collection", corpus_path : str = None):
        self.embedding_client = EmbeddingClient()
        
        corpus_path = self.resolve_corpus_path(corpus_path)
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory = "./chroma_data"
        ))
        
        # 创建或获取collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
            logger.info(f"加载现有集合: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(name=collection_name)
            logger.info(f"创建新集合: {collection_name}")
            if(Path(corpus_path).exists()):
                self.build_database(corpus_path)
            else:
                #logger.info(f"DEBUG: corpus_path = {repr(corpus_path)}")
                logger.error(f"创建新集合时，提供的语料路径不存在:{corpus_path}")
                

    def resolve_corpus_path(self, corpus_path: str) -> str:
    
        p = Path(corpus_path)

        # 如果是绝对路径，直接解析
        if p.is_absolute():
            return str(p.resolve())
        else:
            # 如果是相对路径，相对于当前脚本所在目录
            script_dir = Path(__file__).parent.resolve()
            return str((script_dir / p).resolve())


    def read_txt_file(self, file_path: str) -> str:
        """读取txt文件内容"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    
    def split_text_with_langchain(self, text: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
        """使用LangChain的文本分割器"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
            length_function=len,
        )
        
        chunks = text_splitter.split_text(text)
        # 过滤掉太短的块
        chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 10]
        return chunks
    
    def build_database(self, txt_file_path: str, chunk_size: int = 512, chunk_overlap: int = 50):
        """构建RAG数据库"""
        logger.info("开始读取txt文件...")
        text_content = self.read_txt_file(txt_file_path)
        
        logger.info("开始分割文本...")
        chunks = self.split_text_with_langchain(text_content, chunk_size, chunk_overlap)
        
        logger.info(f"总共分割出 {len(chunks)} 个文本块")
        
        # 分批处理embedding（避免API限制）
        batch_size = 10  # 根据API限制调整
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            logger.info(f"处理批次 {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            try:
                embeddings = self.embedding_client.get_embeddings_batch(batch_chunks)
                
                # 添加到ChromaDB
                self.collection.add(
                    documents=batch_chunks,
                    embeddings=embeddings,
                    ids=[f"doc_{i*batch_size+j}" for j in range(len(batch_chunks))],
                    metadatas=[{
                        "source": txt_file_path, 
                        "chunk_id": i*batch_size+j,
                        "chunk_size": len(batch_chunks[j])
                    } for j in range(len(batch_chunks))]
                )
                
            except Exception as e:
                logger.error(f"处理批次时出错: {e}")
                continue
        
        logger.info("数据库构建完成！")
    
    def query(self, query_text: str, top_n: int = 3) -> List[Dict]:
        """查询相似文档"""
        # 获取查询文本的embedding
        query_embedding = self.embedding_client.get_embedding_single_string(query_text)
        
        # 在ChromaDB中搜索相似文档
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results['documents'][0])):
            result = {
                'document': results['documents'][0][i],
                'distance': results['distances'][0][i],
                #'metadata': results['metadatas'][0][i] if results['metadatas'] else None
            }
            formatted_results.append(result)
        
        return formatted_results