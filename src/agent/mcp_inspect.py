from agent.mcp_client import MCPClient
import asyncio

async def main():

    config = {
    "mcpServers": {
        "filesystem": {
            "command": "npx.cmd",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "src/workspace",
            ],
            "shell": "cmd"
        }
    }
}

    

    client = MCPClient(config)
    
    try:
        print("Connecting to FastMCP server...")
        await client.connect()
        print(f"Connected: {client.is_connected}")
        
        print("\n--- Fetching Tools ---")
        tools = await client.list_tools()
        for tool in tools:
            print(f"Tool Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Schema: {tool.input_schema}\n")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        print("\nDisconnecting...")
        await client.disconnect()
        print(f"Connected: {client.is_connected}")

if __name__ == "__main__":
    asyncio.run(main())
