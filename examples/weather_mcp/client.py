import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    city = sys.argv[1] if len(sys.argv) > 1 else "北京"
    server_path = Path(__file__).with_name("server.py")

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_path)],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("可用工具:", ", ".join(tool.name for tool in tools.tools))

            result = await session.call_tool("get_weather", {"city": city})
            for item in result.content:
                if item.type == "text":
                    print(item.text)


if __name__ == "__main__":
    asyncio.run(main())

