"""向量数据库服务"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from app.config import get_settings
from app.core.embeddings import EmbeddingService
from loguru import logger
import uuid
import os


class VectorDBService:
    """向量数据库服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        
        # 确保持久化目录存在
        os.makedirs(self.settings.chroma_persist_dir, exist_ok=True)
        
        # 初始化 Chroma 客户端（持久化模式）
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_persist_dir
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"VectorDB initialized: {self.settings.chroma_persist_dir}")
    
    def add_documents(
        self, 
        texts: List[str], 
        metadatas: List[Dict[str, Any]],
        document_id: str
    ) -> int:
        """
        添加文档到向量数据库
        
        Args:
            texts: 文本块列表
            metadatas: 元数据列表
            document_id: 文档ID
            
        Returns:
            添加的文档数量
        """
        try:
            # 生成唯一ID
            ids = [f"{document_id}_{i}" for i in range(len(texts))]
            
            # 生成向量
            embeddings = self.embedding_service.embed_texts(texts)
            
            # 添加到集合
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(texts)} chunks for document {document_id}")
            return len(texts)
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise Exception(f"向量数据库添加失败: {str(e)}")
    
    def search(
        self, 
        query: str, 
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            # 查询向量化
            query_embedding = self.embedding_service.embed_text(query)
            
            # 检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # 格式化结果
            documents = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    documents.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': 1 - results['distances'][0][i]  # 转换为相似度分数
                    })
            
            logger.info(f"Search returned {len(documents)} results")
            return documents
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise Exception(f"向量检索失败: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """
        删除文档
        
        Args:
            document_id: 文档ID
            
        Returns:
            是否成功
        """
        try:
            # 获取该文档的所有chunk ID
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted document {document_id} ({len(results['ids'])} chunks)")
                return True
            else:
                logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Delete error: {e}")
            raise Exception(f"文档删除失败: {str(e)}")
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        获取所有文档信息
        
        Returns:
            文档信息列表
        """
        try:
            results = self.collection.get()
            
            # 按 document_id 分组
            docs_map = {}
            for i, metadata in enumerate(results['metadatas']):
                doc_id = metadata.get('document_id')
                if doc_id not in docs_map:
                    docs_map[doc_id] = {
                        'document_id': doc_id,
                        'filename': metadata.get('filename', 'unknown'),
                        'file_size': metadata.get('file_size', 0),
                        'upload_time': metadata.get('upload_time', ''),
                        'chunks_count': 0
                    }
                docs_map[doc_id]['chunks_count'] += 1
            
            return list(docs_map.values())
            
        except Exception as e:
            logger.error(f"Get documents error: {e}")
            raise Exception(f"获取文档列表失败: {str(e)}")
    
    def get_collection_count(self) -> int:
        """获取集合中的文档数量"""
        try:
            return self.collection.count()
        except:
            return 0
