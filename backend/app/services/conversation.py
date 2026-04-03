"""会话服务层"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.db_models import Conversation, Message
from app.models.schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    ConversationDetailResponse, MessageResponse, ConversationListResponse
)
from typing import List, Optional
from datetime import datetime
from loguru import logger


class ConversationService:
    """会话管理服务"""
    
    @staticmethod
    def create_conversation(db: Session, data: ConversationCreate) -> Conversation:
        """
        创建新会话
        
        Args:
            db: 数据库会话
            data: 会话创建数据
            
        Returns:
            创建的会话对象
        """
        title = data.title if data.title else "新对话"
        
        conversation = Conversation(title=title)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Created conversation: {conversation.id} - {conversation.title}")
        return conversation
    
    @staticmethod
    def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
        """
        获取会话（含消息）
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            
        Returns:
            会话对象，不存在返回 None
        """
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.is_deleted == False
        ).first()
        
        return conversation
    
    @staticmethod
    def get_conversations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> ConversationListResponse:
        """
        获取会话列表
        
        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 返回数量
            user_id: 用户ID（预留）
            
        Returns:
            会话列表响应
        """
        query = db.query(Conversation).filter(Conversation.is_deleted == False)
        
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        
        # 按更新时间倒序
        query = query.order_by(desc(Conversation.updated_at))
        
        total = query.count()
        conversations_db = query.offset(skip).limit(limit).all()
        
        # 构建响应
        conversations = []
        for conv in conversations_db:
            # 获取消息数量
            message_count = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).count()
            
            # 获取最后一条消息预览
            last_message = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(desc(Message.created_at)).first()
            
            last_message_preview = None
            if last_message:
                preview_text = last_message.content[:50]
                if len(last_message.content) > 50:
                    preview_text += "..."
                last_message_preview = preview_text
            
            conversations.append(ConversationResponse(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=message_count,
                last_message_preview=last_message_preview
            ))
        
        return ConversationListResponse(
            conversations=conversations,
            total=total
        )
    
    @staticmethod
    def update_conversation(
        db: Session,
        conversation_id: str,
        data: ConversationUpdate
    ) -> Optional[Conversation]:
        """
        更新会话
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            data: 更新数据
            
        Returns:
            更新后的会话对象，不存在返回 None
        """
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.is_deleted == False
        ).first()
        
        if not conversation:
            return None
        
        conversation.title = data.title
        conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Updated conversation: {conversation.id} - {conversation.title}")
        return conversation
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: str) -> bool:
        """
        删除会话（软删除）
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            
        Returns:
            是否成功删除
        """
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.is_deleted == False
        ).first()
        
        if not conversation:
            return False
        
        conversation.is_deleted = True
        db.commit()
        
        logger.info(f"Deleted conversation: {conversation_id}")
        return True
    
    @staticmethod
    def add_message(
        db: Session,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[dict]] = None
    ) -> Message:
        """
        添加消息到会话
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            role: 角色 ('user' or 'assistant')
            content: 消息内容
            sources: 来源文档（仅 assistant 消息有）
            
        Returns:
            创建的消息对象
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources
        )
        
        db.add(message)
        
        # 更新会话的 updated_at
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(message)
        
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message
    
    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: str,
        limit: int = 100
    ) -> List[Message]:
        """
        获取会话的所有消息
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            limit: 最大消息数
            
        Returns:
            消息列表
        """
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).limit(limit).all()
        
        return messages
    
    @staticmethod
    def get_recent_messages(
        db: Session,
        conversation_id: str,
        count: int = 10
    ) -> List[Message]:
        """
        获取最近的 N 条消息（用于构建上下文）
        
        Args:
            db: 数据库会话
            conversation_id: 会话ID
            count: 消息数量
            
        Returns:
            最近的消息列表（按时间正序）
        """
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(count).all()
        
        # 反转顺序（最旧的在前）
        return list(reversed(messages))
    
    @staticmethod
    def auto_generate_title(question: str) -> str:
        """
        基于第一个问题自动生成会话标题
        
        Args:
            question: 用户问题
            
        Returns:
            生成的标题
        """
        # 简单截取前 30 个字符作为标题
        if len(question) <= 30:
            return question
        return question[:30] + "..."
