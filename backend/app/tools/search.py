"""网页搜索工具 —— 博查 API（主）/ DuckDuckGo（备用）"""
import requests
from typing import Dict, Any

# 工具定义（交给 LLM）
DEFINITION = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": (
            "搜索互联网上的实时信息，用于回答知识库中没有的最新资讯、新闻、热点事件等问题。"
            "当用户询问近期发生的事情、最新数据、或知识库无法覆盖的问题时调用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，应简洁精准地提炼用户问题"
                },
                "max_results": {
                    "type": "integer",
                    "description": "返回结果数量，默认 5，最多 10",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    }
}


def run(query: str, max_results: int = 5) -> Dict[str, Any]:
    """优先使用博查 API，无 Key 时回退到 DuckDuckGo"""
    from app.config import get_settings
    settings = get_settings()

    if settings.bocha_api_key:
        return _bocha_search(query, max_results, settings.bocha_api_key)
    return _ddg_search(query, max_results)


def _bocha_search(query: str, max_results: int, api_key: str) -> Dict[str, Any]:
    """博查 API（国内稳定，免费额度充足）"""
    try:
        resp = requests.post(
            "https://api.bochaai.com/v1/web-search",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"query": query, "count": min(max_results, 10), "freshness": "noLimit"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()

        items = data.get("data", {}).get("webPages", {}).get("value", [])
        if not items:
            return {"found": False, "results": []}

        return {
            "found": True,
            "query": query,
            "results": [
                {"title": r.get("name", ""), "url": r.get("url", ""), "snippet": r.get("snippet", "")}
                for r in items[:max_results]
            ]
        }
    except Exception as e:
        return {"error": f"博查搜索失败: {str(e)}"}


def _ddg_search(query: str, max_results: int) -> Dict[str, Any]:
    """DuckDuckGo 备用（无需 Key，但可能受网络限制）"""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=min(max_results, 10)):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        if not results:
            return {"found": False, "results": []}
        return {"found": True, "query": query, "results": results}
    except Exception as e:
        return {"error": f"搜索失败: {str(e)}"}
