"""API 路由"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import (
    DocumentUploadResponse,
    QueryRequest,
    QueryResponse,
    DocumentListResponse,
    DeleteResponse,
    HealthResponse
)
from app.services.document import DocumentService
from app.services.vectordb import VectorDBService
from app.core.rag import RAGService
from app.config import get_settings
from loguru import logger
import os
import uuid
import shutil

router = APIRouter(prefix="/api")
settings = get_settings()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档
    
    支持格式: PDF, Word, TXT
    最大文件大小: 10MB
    """
    try:
        # 检查文件类型
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(allowed_extensions)}"
            )
        
        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开头
        
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件太大。最大允许: {settings.max_file_size / 1024 / 1024}MB"
            )
        
        # 保存文件
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{file_id}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # 处理文档
        doc_service = DocumentService()
        document_id, chunks_count = doc_service.process_document(
            file_path=file_path,
            filename=file.filename,
            file_size=file_size
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_size,
            chunks_count=chunks_count,
            message="文档上传并处理成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query_knowledge(request: QueryRequest):
    """
    知识库问答
    
    基于 RAG 返回答案和来源文档
    """
    try:
        rag_service = RAGService()
        result = rag_service.query(
            question=request.question,
            top_k=request.top_k or settings.top_k
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    获取所有文档列表
    """
    try:
        vectordb = VectorDBService()
        documents = vectordb.get_all_documents()
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
async def delete_document(document_id: str):
    """
    删除指定文档
    """
    try:
        vectordb = VectorDBService()
        success = vectordb.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="文档未找到")
        
        return DeleteResponse(
            message="文档删除成功",
            document_id=document_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查
    """
    try:
        vectordb = VectorDBService()
        doc_count = vectordb.get_collection_count()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            vectordb_status="connected",
            documents_count=doc_count
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            vectordb_status="error",
            documents_count=0
        )
