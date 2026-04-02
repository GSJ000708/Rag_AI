"""Pydantic 数据模型"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str
    filename: str
    file_size: int
    chunks_count: int
    message: str


class QueryRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="检索文档数量")


class SourceDocument(BaseModel):
    """来源文档"""
    content: str
    filename: str
    page: Optional[int] = None
    score: float


class QueryResponse(BaseModel):
    """问答响应"""
    answer: str
    sources: List[SourceDocument]
    question: str


class DocumentInfo(BaseModel):
    """文档信息"""
    document_id: str
    filename: str
    file_size: int
    upload_time: datetime
    chunks_count: int


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    documents: List[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    """删除响应"""
    message: str
    document_id: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    vectordb_status: str
    documents_count: int
