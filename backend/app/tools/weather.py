"""天气查询工具"""
import requests
from typing import Dict, Any

# 工具定义（交给 LLM）
DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": (
            "查询指定城市的实时天气，包括温度、天气状况、湿度、风速。"
            "当用户询问天气、气温、是否下雨、要不要带伞时调用。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，支持中文或英文，如：北京、Shanghai"
                }
            },
            "required": ["city"]
        }
    }
}


def run(city: str) -> Dict[str, Any]:
    """调用 wttr.in 查询天气（免费，无需 API Key）"""
    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        current = data["current_condition"][0]
        area = data["nearest_area"][0]

        return {
            "city": f"{area['areaName'][0]['value']}, {area['country'][0]['value']}",
            "temp_c": current["temp_C"],
            "feels_like_c": current["FeelsLikeC"],
            "humidity": current["humidity"],
            "wind_speed_kmph": current["windspeedKmph"],
            "description": current["weatherDesc"][0]["value"],
        }
    except requests.exceptions.Timeout:
        return {"error": "天气查询超时，请稍后重试"}
    except Exception as e:
        return {"error": f"天气查询失败: {str(e)}"}
