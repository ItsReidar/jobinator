from pathlib import Path
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

def read_cv() -> str:
    """Reads the content of a user CV file. Formatted in Markdown.
    Returns content of a file as a string.
    """
    file_path = Path("user_data/cv_markdown.md")
    with file_path.open("r", encoding="utf-8") as file:
        text = file.read()
        return text  

def create_mcp_tools():
    filesystem_tools = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "-y", 
                    "@modelcontextprotocol/server-filesystem", 
                    "/Users/jelle.vanelburg/Git-repos",
                    "/Users/jelle.vanelburg/Downloads",
                    "/Users/jelle.vanelburg/Desktop",
                ],
            )
        )
    )

    # glean_tools = MCPToolset(
    #     connection_params=StdioConnectionParams(
    #         server_params=StdioServerParameters(
    #             command="npx",
    #             args=[
    #                 "-y",
    #                 "mcp-remote@0.1.29",
    #                 "https://coolblue-be.glean.com/mcp/default"
    #             ]
    #         )
    #     )
    # )

    return filesystem_tools #, glean_tools
