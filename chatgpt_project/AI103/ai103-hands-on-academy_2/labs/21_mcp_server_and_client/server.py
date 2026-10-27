# Purpose: Serve policy tools over MCP stdio
# Learn: Understand tool registration and the protocol server lifecycle.
# Run: Started by lab 21 live=true after installing requirements/mcp.txt. Do not run as an ordinary notebook cell; the server waits for client messages.

from mcp.server.fastmcp import FastMCP
from academy.domain import retrieve,ALICE
server=FastMCP('AI103 public policy')
@server.tool()
def public_policy(query:str)->list:
    """Search the synthetic public retail policies; no customer data or write tools."""
    return retrieve(query,ALICE)
if __name__=='__main__':
    server.run(transport='stdio')
