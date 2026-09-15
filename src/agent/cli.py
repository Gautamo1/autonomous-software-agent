from agent.mcp_client import MCPClient
from agent.llm import OllamaLLM
from agent.agent_script import Agent, AgentRuntime, build_agent_graph
import asyncio
import argparse
from agent.config import load_config


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workspace",
        required=True,
        help="Path exposed to the MCP filesystem server",
    )
    return parser.parse_args()


async def run(workspace_path):
    config = load_config(workspace_path)

    llm = OllamaLLM('qwen3.5:4b')
    mcp = MCPClient(config)
    task = input("Task: ")

    try:
        await mcp.connect()

        agent = Agent(llm, mcp)
        graph = build_agent_graph(agent)
        runtime = AgentRuntime(agent, graph, mcp)

        result = await runtime.run(task)
        print(result)
    except Exception as e:
        print(f"Exception occurred: {e}")

    finally:
        await mcp.disconnect()

def main():
    args = parse_args()
    asyncio.run(run(args.workspace))


if __name__ == "__main__":
    main()