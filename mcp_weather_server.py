#!/usr/bin/env python3
"""
MCP Weather Server — 最小示例
提供两个工具：
  - get_weather(city: str) -> 返回城市天气
  - list_cities() -> 返回支持的城市列表

使用 stdio 作为 MCP 传输层。
"""

import sys
import json


# ── 模拟天气数据 ──

WEATHER_DB = {
    "beijing": {"city": "Beijing", "temperature": 26, "condition": "Sunny", "humidity": 30},
    "shanghai": {"city": "Shanghai", "temperature": 28, "condition": "Cloudy", "humidity": 65},
    "shenzhen": {"city": "Shenzhen", "temperature": 31, "condition": "Rainy", "humidity": 80},
    "tokyo": {"city": "Tokyo", "temperature": 22, "condition": "Overcast", "humidity": 55},
    "new york": {"city": "New York", "temperature": 18, "condition": "Windy", "humidity": 40},
}


def get_weather(city: str) -> dict:
    key = city.lower().strip()
    data = WEATHER_DB.get(key)
    if not data:
        return {"error": f"City '{city}' not found. Supported: {', '.join(WEATHER_DB.keys())}"}
    return data


def list_cities() -> list[str]:
    return [info["city"] for info in WEATHER_DB.values()]


# ── MCP Protocol (stdio) ──

def send_message(msg: dict):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle_request(req: dict) -> dict:
    method = req.get("method")
    params = req.get("params", {})
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "weather-server", "version": "1.0.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "get_weather",
                        "description": "Get current weather for a city.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "description": "City name (e.g. Beijing)"}
                            },
                            "required": ["city"],
                        },
                    },
                    {
                        "name": "list_cities",
                        "description": "List all supported cities.",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if tool_name == "get_weather":
            result = get_weather(arguments.get("city", ""))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                },
            }
        if tool_name == "list_cities":
            result = list_cities()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                },
            }
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"},
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Unknown method: {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send_message({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            })
            continue
        resp = handle_request(req)
        send_message(resp)


if __name__ == "__main__":
    main()
