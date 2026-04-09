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


class ChatRequest(BaseModel):
    """闲聊请求"""
    message: str = Field(..., min_length=1, description="用户消息")
    history: list = Field(default_factory=list, description="对话历史")


class ChatResponse(BaseModel):
    """闲聊响应"""
    answer: str
    message: str


# ============ 会话管理相关模型 ============

class ConversationCreate(BaseModel):
    """创建会话请求"""
    title: Optional[str] = None  # 如果为空，自动生成


class ConversationUpdate(BaseModel):
    """更新会话请求"""
    title: str = Field(..., min_length=1, max_length=255, description="会话标题")


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    conversation_id: str
    role: str
    content: str
    sources: Optional[List[SourceDocument]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """会话响应"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """会话详情响应"""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """会话列表响应"""
    conversations: List[ConversationResponse]
    total: int


class ConversationQueryRequest(BaseModel):
    """会话中提问请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="检索文档数量")


class ConversationQueryResponse(BaseModel):
    """会话中提问响应"""
    message_id: str
    conversation_id: str
    answer: str
    sources: List[SourceDocument]
    question: str
