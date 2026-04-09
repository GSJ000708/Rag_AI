"""工具注册表：统一管理所有可供 LLM 调用的工具"""
from app.tools import weather, search

# LLM 工具定义列表（传给 generate_with_tools）
TOOL_DEFINITIONS = [
    weather.DEFINITION,
    search.DEFINITION,
]

# 工具名 → 执行函数的映射
TOOL_REGISTRY = {
    "get_weather": lambda args: weather.run(**args),
    "web_search": lambda args: search.run(**args),
}
