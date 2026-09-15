from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ollama import chat
from agent.mcp_protocol import Tool
from langchain_core.messages import BaseMessage



class ToolCall(BaseModel):

    name: str
    arguments: Dict[str, Any]

class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)

class LLM(ABC):

    @abstractmethod
    def chat(self, messages: list[BaseMessage], tools: list[Tool]):
        pass

class OllamaLLM(LLM):

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name=model_name

    def create_tool(self, tool: Tool):
        schema_data = dict(tool.input_schema)

        params = {
            "type": "object",
            "properties": schema_data.get("properties", {}),
            "required": schema_data.get("required", [])
        }

        return {
            'type': 'function',
            'function': {
                'name': tool.name,
                'description': tool.description,
                'parameters': params
            }
        }
    def create_tools(self, tools: List[Tool]):

        result = []

        for tool in tools:
            result.append(self.create_tool(tool=tool))

        return result

    def serialize_message(self, message: BaseMessage)-> dict:
        role_map= {
            "human": "user",
            "ai": "assistant",
            "tool": "tool",
            "system": "system",
        }
        serialized = {
            "role": role_map[message.type],
            "content": message.content or "",
        }

        if message.type == "ai" and message.tool_calls:
            serialized['tool_calls'] = [
                {
                    "function": {
                        "name": tool_call['name'],
                        "arguments": tool_call['args']
                    }
                }
                for tool_call in message.tool_calls
            ]
        return serialized
    
    def chat(self, messages: list[BaseMessage], tools: List[Tool]):
        tool_definitions = self.create_tools(tools)

        ollama_messages = [
            self.serialize_message(message)
            for message in messages
        ]

        response = chat(
            model=self.model_name,
            messages=ollama_messages,
            tools=tool_definitions,
        )

        print("LLM Response Full:")
        print(response.message)

        tool_calls: List[ToolCall] = []

        if response.message.tool_calls:
            for native_call in response.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        name=native_call.function.name,
                        arguments=native_call.function.arguments
                    )
                )

        return LLMResponse(
            content=response.message.content,
            tool_calls=tool_calls
        )
    