"""智谱 AI LLM 封装"""
from zhipuai import ZhipuAI
from app.config import get_settings
from loguru import logger


class LLMService:
    """LLM 服务"""
    
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
        self.model = self.settings.llm_model
        
    def generate(self, prompt: str, temperature: float = None) -> str:
        """
        生成回答
        
        Args:
            prompt: 输入提示
            temperature: 温度参数
            
        Returns:
            生成的文本
        """
        try:
            if temperature is None:
                temperature = self.settings.temperature
                
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            
            answer = response.choices[0].message.content
            logger.info(f"LLM generated response (length: {len(answer)})")
            return answer
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")
