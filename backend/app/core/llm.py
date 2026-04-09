"""智谱 AI LLM 封装"""
from zhipuai import ZhipuAI
from typing import List, Dict, Any, Optional
from app.config import get_settings
from loguru import logger


class LLMService:
    """LLM 服务"""

    def __init__(self):
        self.settings = get_settings()

        if not self.settings.zhipu_api_key or self.settings.zhipu_api_key == "your_zhipu_api_key_here":
            raise ValueError(
                "智谱 API Key 未配置！请在 .env 文件中设置 ZHIPU_API_KEY\n"
                "获取方式: https://open.bigmodel.cn/"
            )

        logger.info(f"Initializing ZhipuAI client with API key: {self.settings.zhipu_api_key[:10]}...")
        self.client = ZhipuAI(api_key=self.settings.zhipu_api_key)
        self.model = self.settings.llm_model

    def generate(self, prompt: str, temperature: float = None) -> str:
        """普通文本生成"""
        try:
            if temperature is None:
                temperature = self.settings.temperature

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            answer = response.choices[0].message.content
            logger.info(f"LLM generated response (length: {len(answer)})")
            return answer

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")

    def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = None,
    ) -> Any:
        """
        带工具定义的生成（Function Calling 第一步）。
        返回原始 response，调用方根据 tool_calls 决定后续逻辑。
        """
        try:
            if temperature is None:
                temperature = self.settings.temperature

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
            )
            choice = response.choices[0]
            logger.info(
                f"LLM tool call response: finish_reason={choice.finish_reason}, "
                f"tool_calls={bool(choice.message.tool_calls)}"
            )
            return choice

        except Exception as e:
            logger.error(f"LLM tool call error: {e}")
            raise Exception(f"LLM工具调用失败: {str(e)}")

    def generate_with_messages(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = None,
    ) -> str:
        """
        多轮消息列表生成（Function Calling 第二步，把工具结果喂回 LLM）。
        """
        try:
            if temperature is None:
                temperature = self.settings.temperature

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            answer = response.choices[0].message.content
            logger.info(f"LLM final response (length: {len(answer)})")
            return answer

        except Exception as e:
            logger.error(f"LLM messages generation error: {e}")
            raise Exception(f"LLM调用失败: {str(e)}")
