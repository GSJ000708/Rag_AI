"""RAG 核心逻辑 —— 纯检索增强生成，不包含工具调用"""
import re
from typing import List, Dict, Any
from app.core.llm import LLMService
from app.services.vectordb import VectorDBService
from loguru import logger

SYSTEM_PROMPT = (
    "你是一个专业的知识库助手。请严格根据提供的参考文档回答用户问题，"
    "不要编造信息。如果文档中没有相关内容，请明确告知。"
    "回答要简洁、准确、有条理。"
)


class RAGService:
    """RAG 服务：检索 → 增强 Prompt → 生成答案"""

    def __init__(self, vectordb_service: VectorDBService = None):
        self.llm = LLMService()
        self.vectordb = vectordb_service if vectordb_service else VectorDBService()

    async def query(
        self,
        question: str,
        top_k: int = 3,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """混合检索 → 拼 Prompt → LLM 生成答案"""
        try:
            # 1. 混合检索（向量 + BM25 + RRF）
            logger.info(f"RAG search: {question!r}")
            docs = self.vectordb.search(query=question, top_k=top_k)

            if not docs:
                return {
                    "answer": "抱歉，知识库中没有找到相关信息。",
                    "sources": [],
                    "question": question,
                    "mode": "rag"
                }

            # 2. 构建消息（system 带检索内容 + 历史 + 当前问题）
            context = "\n".join(
                f"[文档{i}] {d['metadata'].get('filename', 'unknown')}\n{d['content']}"
                for i, d in enumerate(docs, 1)
            )
            messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\n参考文档：\n{context}"}]
            for msg in (conversation_history or [])[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": question})

            # 3. 生成答案
            logger.info("Generating RAG answer")
            raw = self.llm.generate_with_messages(messages)
            answer = _clean(raw)

            # 4. 格式化来源
            sources = [
                {
                    "content": d["content"][:200] + ("..." if len(d["content"]) > 200 else ""),
                    "filename": d["metadata"].get("filename", "unknown"),
                    "page": d["metadata"].get("chunk_index"),
                    "score": round(d["score"], 4)
                }
                for d in docs
            ]

            logger.info("RAG query completed")
            return {"answer": answer, "sources": sources, "question": question, "mode": "rag"}

        except Exception as e:
            logger.error(f"RAG query error: {e}")
            raise Exception(f"问答失败: {str(e)}")


def _clean(text: str) -> str:
    """去除多余空行和行尾空格"""
    if not text:
        return ""
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text).strip()
    return '\n'.join(line.rstrip() for line in text.split('\n'))
