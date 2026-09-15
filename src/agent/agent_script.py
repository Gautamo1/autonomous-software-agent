from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages
from agent.mcp_protocol import Tool
from langgraph.graph import StateGraph, END, START
from agent.llm import OllamaLLM
from agent.mcp_client import MCPClient


class AgentState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]
    tools: list[Tool]


class Agent:
    def __init__(self, llm, mcp_client):
        self.llm = llm
        self.mcp_client = mcp_client


    async def llm_node(self, state: AgentState):
        response = self.llm.chat(
            messages=state['messages'],
            tools=state['tools']
        )

        tool_calls = []
        
        if response.tool_calls:
            tool_calls.append(
                {
                    "name": response.tool_calls[0].name,
                    "args": response.tool_calls[0].arguments,
                    "id": f"call_{0}",
                }
                
            )
        message = AIMessage(
            content=response.content or "",
            tool_calls=tool_calls
        )

        return {
            "messages": [message]
        }
    
    async def tool_node(self, state: AgentState):
        last_message = state['messages'][-1]
        tool_calls = last_message.tool_calls
        latest_tool_call = tool_calls[0]
        result = await self.mcp_client.call_tool(name=latest_tool_call['name'], arguments=latest_tool_call['args'])

        message = ToolMessage(
            content=result.content,
            name=latest_tool_call['name'],
            tool_call_id=latest_tool_call['id']
        )

        return {
            "messages": [message]
        }





    async def router(self, state: AgentState):
        latest_message = state['messages'][-1]

        if latest_message.tool_calls:
            return "tool_node"

        return END





def build_agent_graph(agent: Agent):
    workflow = StateGraph(AgentState)
    workflow.add_node("llm_node", agent.llm_node)
    workflow.add_node("tool_node", agent.tool_node)
    workflow.add_edge(START, "llm_node")
    workflow.add_conditional_edges(
        "llm_node",
        agent.router,
        {
            "tool_node": "tool_node",
            END: END,
        },
    )
    workflow.add_edge("tool_node", "llm_node")
    return workflow.compile()


class AgentRuntime:
    def __init__(self, agent: Agent, graph, mcp: MCPClient):
        self.agent = agent
        self.graph = graph
        self.mcp = mcp

    async def run(self, query: str):
        message = HumanMessage(content=query)
        tools = await self.mcp.list_tools()

        state: AgentState = {
            "messages": [
                SystemMessage(
                    content=(
                        "After completing the requested file operation, respond with a "
                        "clear confirmation describing what changed. For example: "
                        "The file `hello.txt` has been successfully updated."
                    )
                ),
                message,
            ],
            "tools": tools
        }

        final_state = await self.graph.ainvoke(state)
        return final_state.get('messages')[-1].content