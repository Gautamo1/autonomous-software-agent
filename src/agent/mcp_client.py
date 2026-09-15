from agent.mcp_protocol import MCP, Tool, ToolResult
from typing import List
from fastmcp import Client
from contextlib import AsyncExitStack

class MCPClient(MCP):

    def __init__(self, config: dict):
        self.config = config
        self.client = Client(config)

        self._exit_stack = AsyncExitStack()
        self.is_connected = False

    async def connect(self):
        if self.is_connected:
            return

        try:
            await self._exit_stack.enter_async_context(self.client)
            self.is_connected = True

        except Exception as e:
            await self.disconnect()
            raise RuntimeError(f"failed to connect to FastMCP server: {e}")

    async def disconnect(self):
        self.is_connected = False

        await self._exit_stack.aclose()
        self._exit_stack = AsyncExitStack()



    async def list_tools(self):
        if not self.is_connected:
            raise RuntimeError("Client is not connected. Call connect() first.")
        
        response = await self.client.list_tools()

        tools: List[Tool] = []

        for tool in response:
            tools.append(
                Tool(
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.input_schema
                )
            )
        return tools

    async def call_tool(self, name: str, arguments):
        if not self.is_connected:
            raise RuntimeError("Client is not connected. Call connect() first.")
        try:
            response = await self.client.call_tool(name, arguments)
            return ToolResult(
                content=response.content[0].text,
                is_error=response.is_error
            )
        except Exception as e:
            return ToolResult(
                content= f"Error occurred: {e}",
                is_error=True
            )