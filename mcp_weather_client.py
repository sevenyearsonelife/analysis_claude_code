#!/usr/bin/env python3
"""
MCP Weather Client — 最小示例
通过 stdio 启动 MCP Weather Server，发现工具并调用。
"""

import subprocess
import json
import sys


class MCPClient:
    """通过 stdio 与 MCP Server 通信的客户端。"""

    def __init__(self, command: list[str]):
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._req_id = 0

    def _send(self, method: str, params: dict | None = None) -> dict:
        self._req_id += 1
        req = {
            "jsonrpc": "2.0",
            "id": self._req_id,
            "method": method,
            "params": params or {},
        }
        line = json.dumps(req) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        resp_line = self.proc.stdout.readline().strip()
        return json.loads(resp_line)

    def initialize(self) -> dict:
        return self._send("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "weather-client", "version": "1.0.0"}})

    def list_tools(self) -> list[dict]:
        resp = self._send("tools/list")
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name: str, arguments: dict) -> str:
        resp = self._send("tools/call", {"name": name, "arguments": arguments})
        result = resp.get("result", {})
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            return content[0]["text"]
        return json.dumps(result)

    def close(self):
        self.proc.terminate()
        self.proc.wait()


def main():
    # 启动 MCP Server（通过 stdio 通信）
    client = MCPClient([sys.executable, "mcp_weather_server.py"])

    # 1. 初始化连接
    init_result = client.initialize()
    print("[init]", init_result.get("result", {}).get("serverInfo", {}))

    # 2. 发现工具
    tools = client.list_tools()
    print(f"\n[discovered] {len(tools)} tools:")
    for t in tools:
        print(f"  - {t['name']}: {t['description']}")

    # 3. 调用 list_cities
    print("\n[call] list_cities()")
    cities = client.call_tool("list_cities", {})
    print("  result:", cities)

    # 4. 调用 get_weather
    print("\n[call] get_weather('Beijing')")
    weather = client.call_tool("get_weather", {"city": "Beijing"})
    print("  result:", weather)

    print("\n[call] get_weather('Shanghai')")
    weather = client.call_tool("get_weather", {"city": "Shanghai"})
    print("  result:", weather)

    print("\n[call] get_weather('UnknownCity')")
    weather = client.call_tool("get_weather", {"city": "UnknownCity"})
    print("  result:", weather)

    client.close()
    print("\n[done] Connection closed.")


if __name__ == "__main__":
    main()
