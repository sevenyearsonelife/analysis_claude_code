from mcp.server.fastmcp import FastMCP


mcp = FastMCP("weather-server", log_level="ERROR")

WEATHER_BY_CITY = {
    "北京": {"condition": "晴", "temperature": 26, "humidity": 42},
    "上海": {"condition": "多云", "temperature": 24, "humidity": 68},
    "深圳": {"condition": "阵雨", "temperature": 29, "humidity": 81},
}


@mcp.tool()
def get_weather(city: str) -> str:
    """获取指定城市的当前天气。"""
    weather = WEATHER_BY_CITY.get(city)
    if weather is None:
        return f"暂时没有 {city} 的天气数据"

    return (
        f"{city}: {weather['condition']}, "
        f"{weather['temperature']}°C, "
        f"湿度 {weather['humidity']}%"
    )


if __name__ == "__main__":
    mcp.run()
