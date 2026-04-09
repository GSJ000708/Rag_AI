"""会话管理 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.conversation import ConversationService
from app.services.vectordb import VectorDBService
from app.core.rag import RAGService
from app.models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
    ConversationDetailResponse,
    MessageResponse,
    ConversationQueryRequest,
    ConversationQueryResponse,
    DeleteResponse,
    SourceDocument
)
from typing import List
from loguru import logger

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# 懒加载：避免启动时阻塞
_vectordb_service = None
_rag_service = None

def get_rag_service() -> RAGService:
    global _vectordb_service, _rag_service
    if _rag_service is None:
        _vectordb_service = VectorDBService()
        _rag_service = RAGService(_vectordb_service)
    return _rag_service


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    创建新会话
    
    - **title**: 会话标题（可选，默认为"新对话"）
    """
    try:
        conversation = ConversationService.create_conversation(db, data)
        
        # 构建响应
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=0,
            last_message_preview=None
        )
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ConversationListResponse)
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取会话列表
    
    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数
    """
    try:
        return ConversationService.get_conversations(db, skip=skip, limit=limit)
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话详情（含所有消息）
    
    - **conversation_id**: 会话ID
    """
    try:
        conversation = ConversationService.get_conversation(db, conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取消息
        messages = ConversationService.get_messages(db, conversation_id)
        
        # 构建响应
        message_responses = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                sources=[SourceDocument(**src) for src in msg.sources] if msg.sources else None,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        return ConversationDetailResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=message_responses
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新会话（目前仅支持更新标题）
    
    - **conversation_id**: 会话ID
    - **title**: 新的会话标题
    """
    try:
        conversation = ConversationService.update_conversation(db, conversation_id, data)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取消息数量
        messages = ConversationService.get_messages(db, conversation_id)
        
        return ConversationResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(messages),
            last_message_preview=messages[-1].content[:50] if messages else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}", response_model=DeleteResponse)
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    删除会话（软删除）
    
    - **conversation_id**: 会话ID
    """
    try:
        success = ConversationService.delete_conversation(db, conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return DeleteResponse(
            message="会话已删除",
            document_id=conversation_id  # 复用字段
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """
    获取会话的所有消息
    
    - **conversation_id**: 会话ID
    """
    try:
        # 检查会话是否存在
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        messages = ConversationService.get_messages(db, conversation_id)
        
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                sources=[SourceDocument(**src) for src in msg.sources] if msg.sources else None,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{conversation_id}/query", response_model=ConversationQueryResponse)
async def query_in_conversation(
    conversation_id: str,
    request: ConversationQueryRequest,
    db: Session = Depends(get_db)
):
    """
    在会话中提问（带上下文的 RAG 查询）
    
    - **conversation_id**: 会话ID
    - **question**: 用户问题
    - **top_k**: 检索文档数量（默认3）
    """
    try:
        # 检查会话是否存在
        conversation = ConversationService.get_conversation(db, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        logger.info(f"Query in conversation {conversation_id}: {request.question}")
        
        # 保存用户消息
        user_message = ConversationService.add_message(
            db, conversation_id, "user", request.question
        )
        
        # 获取最近的对话历史（用于上下文）
        recent_messages = ConversationService.get_recent_messages(db, conversation_id, count=10)
        
        # 构建对话历史文本
        history_context = []
        for msg in recent_messages[:-1]:  # 排除刚添加的用户消息
            history_context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 执行 RAG 查询
        result = await get_rag_service().query(
            question=request.question,
            top_k=request.top_k,
            conversation_history=history_context  # 传入对话历史
        )
        
        # 保存助手回复
        sources_data = [
            {
                "content": src["content"],
                "filename": src["filename"],
                "page": src["page"],
                "score": src["score"]
            }
            for src in result["sources"]
        ]

        assistant_message = ConversationService.add_message(
            db, conversation_id, "assistant", result["answer"], sources_data
        )

        # 如果是第一个问题，自动生成会话标题
        if len(recent_messages) == 1:  # 只有刚添加的用户消息
            auto_title = ConversationService.auto_generate_title(request.question)
            ConversationService.update_conversation(
                db, conversation_id,
                ConversationUpdate(title=auto_title)
            )

        return ConversationQueryResponse(
            message_id=assistant_message.id,
            conversation_id=conversation_id,
            answer=result["answer"],
            sources=result["sources"],
            question=request.question
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying in conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
