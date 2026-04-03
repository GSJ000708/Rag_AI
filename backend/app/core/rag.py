"""RAG 核心逻辑"""
from typing import List, Dict, Any
import re
from app.core.llm import LLMService
from app.services.vectordb import VectorDBService
from loguru import logger


class RAGService:
    """RAG (Retrieval-Augmented Generation) 服务"""
    
    def __init__(self, vectordb_service: VectorDBService = None):
        self.llm = LLMService()
        self.vectordb = vectordb_service if vectordb_service else VectorDBService()
    
    def clean_answer(self, text: str) -> str:
        """
        清理 AI 回答，去掉多余空行
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 替换多个连续空行为单个空行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # 去掉开头和结尾的空白
        text = text.strip()
        
        # 去掉每行末尾的空格
        lines = [line.rstrip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text
    
    def build_prompt(
        self, 
        question: str, 
        context_docs: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        构建 Prompt（支持对话历史）
        
        Args:
            question: 用户问题
            context_docs: 上下文文档列表
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            完整的 Prompt
        """
        # 组装对话历史
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-10:]:  # 最近 10 条消息
                role_name = "用户" if msg["role"] == "user" else "助手"
                history_text += f"\n{role_name}: {msg['content']}\n"
        
        # 组装上下文
        context_text = ""
        for i, doc in enumerate(context_docs, 1):
            content = doc['content']
            filename = doc['metadata'].get('filename', 'unknown')
            context_text += f"\n[文档{i}] {filename}\n{content}\n"
        
        # 构建 Prompt
        if history_text:
            prompt = f"""你是一个专业的知识库助手。请基于以下对话历史、文档内容简洁准确地回答用户的问题。

对话历史:
{history_text}

参考文档:
{context_text}

当前问题: {question}

回答要求:
1. 结合对话历史理解问题（如果有代词，根据历史推断其指代）
2. 严格根据文档内容回答，不要编造信息
3. 如果文档中没有相关信息，请明确告知
4. 回答要简洁、准确、有条理
5. 避免过多空行，保持格式紧凑
6. 可以使用简洁的列表或分点说明

请直接给出答案:"""
        else:
            prompt = f"""你是一个专业的知识库助手。请基于以下文档内容简洁准确地回答用户的问题。

参考文档:
{context_text}

用户问题: {question}

回答要求:
1. 严格根据文档内容回答，不要编造信息
2. 如果文档中没有相关信息，请明确告知
3. 回答要简洁、准确、有条理
4. 避免过多空行，保持格式紧凑
5. 可以使用简洁的列表或分点说明

请直接给出答案:"""
        
        return prompt
    
    async def query(
        self, 
        question: str, 
        top_k: int = 3,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        RAG 问答（支持对话历史）
        
        Args:
            question: 用户问题
            top_k: 检索文档数量
            conversation_history: 对话历史（可选）
            
        Returns:
            包含答案和来源的字典
        """
        try:
            # 1. 向量检索相关文档
            logger.info(f"Searching for question: {question}")
            retrieved_docs = self.vectordb.search(
                query=question,
                top_k=top_k
            )
            
            if not retrieved_docs:
                return {
                    'answer': '抱歉，我在知识库中没有找到相关信息来回答您的问题。',
                    'sources': [],
                    'question': question
                }
            
            # 2. 构建 Prompt（带对话历史）
            prompt = self.build_prompt(question, retrieved_docs, conversation_history)
            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            # 3. LLM 生成答案
            logger.info("Generating answer with LLM")
            raw_answer = self.llm.generate(prompt)
            
            # 清理答案格式
            answer = self.clean_answer(raw_answer)
            
            # 4. 格式化来源文档
            sources = []
            for doc in retrieved_docs:
                sources.append({
                    'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                    'filename': doc['metadata'].get('filename', 'unknown'),
                    'page': doc['metadata'].get('chunk_index'),
                    'score': round(doc['score'], 4)
                })
            
            result = {
                'answer': answer,
                'sources': sources,
                'question': question
            }
            
            logger.info("RAG query completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            raise Exception(f"问答失败: {str(e)}")
