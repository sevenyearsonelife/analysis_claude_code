# 最小天气 MCP 示例

这个示例包含一个 MCP server 和一个 MCP client：

- `server.py`：暴露 `get_weather` 工具。
- `client.py`：通过 stdio 启动 server，发现工具并调用 `get_weather`。

示例使用 mock 天气数据，不依赖真实天气 API 或 API key。

## 运行

> 当前 MCP Python SDK 需要 Python 3.10+。

```sh
cd examples/weather_mcp
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python client.py 北京
```

这里不需要单独执行 `python server.py`。`client.py` 会通过 stdio transport 自动启动 server：

```python
params = StdioServerParameters(
    command=sys.executable,
    args=[str(server_path)],
)
```

这段代码等价于让 MCP client 启动当前 Python 解释器，并执行同目录下的 `server.py`。随后 `stdio_client(params)` 会连接到这个子进程的 stdin/stdout。

预期输出类似：

```text
可用工具: get_weather
北京: 晴, 26°C, 湿度 42%
```

## 配置到 Claude Code

先确保示例依赖已经装到虚拟环境：

```sh
cd /Users/linus/Desktop/2025/newborn/analysis_claude_code/examples/weather_mcp
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

然后在仓库根目录添加 project-scoped MCP server：

```sh
cd /Users/linus/Desktop/2025/newborn/analysis_claude_code
claude mcp add --transport stdio --scope project weather \
  -- /Users/linus/Desktop/2025/newborn/analysis_claude_code/examples/weather_mcp/.venv/bin/python \
     /Users/linus/Desktop/2025/newborn/analysis_claude_code/examples/weather_mcp/server.py
```

这会在项目根目录生成或更新 `.mcp.json`。也可以手写成下面这样：

```json
{
  "mcpServers": {
    "weather": {
      "type": "stdio",
      "command": "/Users/linus/Desktop/2025/newborn/analysis_claude_code/examples/weather_mcp/.venv/bin/python",
      "args": [
        "/Users/linus/Desktop/2025/newborn/analysis_claude_code/examples/weather_mcp/server.py"
      ]
    }
  }
}
```

检查配置：

```sh
claude mcp list
claude mcp get weather
```

进入 Claude Code 后执行：

```text
/mcp
```

首次加载 project-scoped server 时，Claude Code 可能会要求你确认信任这个 `.mcp.json`。
