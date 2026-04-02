"""文档处理服务"""
import os
import uuid
from datetime import datetime
from typing import Tuple
from app.config import get_settings
from app.utils.file_parser import FileParser, TextSplitter
from app.services.vectordb import VectorDBService
from loguru import logger


class DocumentService:
    """文档处理服务"""
    
    def __init__(self):
        self.settings = get_settings()
        self.file_parser = FileParser()
        self.text_splitter = TextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        self.vectordb = VectorDBService()
        
        # 确保上传目录存在
        os.makedirs(self.settings.upload_dir, exist_ok=True)
    
    def process_document(
        self, 
        file_path: str, 
        filename: str,
        file_size: int
    ) -> Tuple[str, int]:
        """
        处理文档：解析 -> 分块 -> 向量化 -> 存储
        
        Args:
            file_path: 文件路径
            filename: 文件名
            file_size: 文件大小
            
        Returns:
            (文档ID, 分块数量)
        """
        try:
            # 1. 解析文档
            logger.info(f"Parsing document: {filename}")
            text = self.file_parser.parse_file(file_path)
            
            if not text:
                raise ValueError("文档内容为空")
            
            # 2. 文本分块
            logger.info(f"Splitting text: {len(text)} chars")
            chunks = self.text_splitter.split_text(text)
            
            if not chunks:
                raise ValueError("文本分块失败")
            
            # 3. 生成文档ID
            document_id = str(uuid.uuid4())
            upload_time = datetime.now().isoformat()
            
            # 4. 准备元数据
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({
                    'document_id': document_id,
                    'filename': filename,
                    'file_size': file_size,
                    'upload_time': upload_time,
                    'chunk_index': i,
                    'total_chunks': len(chunks)
                })
            
            # 5. 存储到向量数据库
            logger.info(f"Storing {len(chunks)} chunks to vectordb")
            chunks_count = self.vectordb.add_documents(
                texts=chunks,
                metadatas=metadatas,
                document_id=document_id
            )
            
            logger.info(f"Document processed successfully: {document_id}")
            return document_id, chunks_count
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            raise Exception(f"文档处理失败: {str(e)}")
