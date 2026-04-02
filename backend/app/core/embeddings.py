"""智谱 AI Embedding 封装"""
from zhipuai import ZhipuAI
from app.config import get_settings
from typing import List
from loguru import logger


class EmbeddingService:
    """Embedding 服务"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # 验证 API Key
        if not self.settings.zhipu_api_key or self.settings.zhipu_api_key == "your_zhipu_api_key_here":
            raise ValueError(
                "智谱 API Key 未配置！请在 .env 文件中设置 ZHIPU_API_KEY\n"
                "获取方式: https://open.bigmodel.cn/"
            )
        
        logger.info(f"Initializing ZhipuAI client with API key: {self.settings.zhipu_api_key[:10]}...")
        self.client = ZhipuAI(api_key=self.settings.zhipu_api_key)
        self.model = self.settings.embedding_model
        
    def embed_text(self, text: str) -> List[float]:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
            
        Returns:
            向量列表
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Embedded text (length: {len(text)}, dim: {len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise Exception(f"Embedding调用失败: {str(e)}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        批量将文本转换为向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表
        """
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        
        logger.info(f"Embedded {len(texts)} texts")
        return embeddings
