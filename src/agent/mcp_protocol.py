from abc import ABC, abstractmethod
from pydantic import BaseModel

class Tool(BaseModel):
    name: str
    description: str
    input_schema: dict

class ToolResult(BaseModel):
    content: str
    is_error: bool

class MCP(ABC):

    @abstractmethod
    async def list_tools(self):
        pass

    @abstractmethod
    async def call_tool(self, name: str, arguments):
        pass