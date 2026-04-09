"""Agent 服务 —— 自由闲聊 + Function Calling 工具调用"""
import json
from typing import List, Dict, Any
from app.core.llm import LLMService
from app.core.rag import _clean
from app.tools import TOOL_DEFINITIONS, TOOL_REGISTRY
from loguru import logger

SYSTEM_PROMPT = (
    "你是一个友好的 AI 助手，具备天气查询和网页搜索能力。\n"
    "需要实时信息时主动调用对应工具，日常闲聊直接回答即可。"
)


class AgentService:
    """
    自由闲聊 Agent：
      1. 第一次调用 LLM（带工具定义）
      2. 若 LLM 决定调工具 → 执行 → 把结果喂回 LLM → 最终答案
      3. 若 LLM 不调工具 → 直接返回
    """

    def __init__(self):
        self.llm = LLMService()

    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in (conversation_history or [])[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": message})

            # 第一次调用：LLM 决定是否用工具
            logger.info(f"Agent chat first turn: {message!r}")
            choice = self.llm.generate_with_tools(messages, TOOL_DEFINITIONS)
            assistant_msg = choice.message

            # 不调工具 → 直接返回
            if not assistant_msg.tool_calls:
                logger.info("Agent: no tool call → direct reply")
                return _clean(assistant_msg.content or "")

            # 调了工具 → 执行并喂回
            tool_call = assistant_msg.tool_calls[0]
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            logger.info(f"Agent tool call: {tool_name}({args})")

            executor = TOOL_REGISTRY.get(tool_name)
            tool_result = executor(args) if executor else {"error": f"未知工具: {tool_name}"}

            # 追加 assistant 的 tool_calls 消息
            messages.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": [{
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_call.function.arguments
                    }
                }]
            })
            # 追加工具执行结果
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result, ensure_ascii=False)
            })

            # 第二次调用：生成最终答案
            logger.info(f"Agent second turn after {tool_name}")
            raw = self.llm.generate_with_messages(messages)
            return _clean(raw)

        except Exception as e:
            logger.error(f"Agent chat error: {e}")
            raise Exception(f"闲聊失败: {str(e)}")
