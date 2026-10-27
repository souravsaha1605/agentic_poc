# Purpose: Connect an MCP client to a local tool server
# Learn: Discover and invoke a tool over stdio; offline fixtures do not prove the MCP protocol works.
# Run: Import databricks/labs/21_mcp_server_and_client.py as a Databricks source notebook. Start live=false; read labs/21_mcp_server_and_client/RUNBOOK.md.

"""Lab 21: MCP server and client. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import run_async
import asyncio,sys,os
from pathlib import Path
from academy.common import args,save,ROOT
opts=args('Discover and invoke a local MCP tool')
if not opts.live:
    save('21_mcp.json',{'mode':'contract preview only','next':'Install requirements/mcp.txt; use --live to run the local protocol (no Azure calls)'})
else:
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    async def call():
        # MCP filters inherited environment variables; pass the package path explicitly.
        server=StdioServerParameters(command=sys.executable,
            args=[str(Path(__file__).with_name('server.py'))],
            env={'PYTHONPATH':str(ROOT/'src')})
        async with stdio_client(server) as (read,write):
            async with ClientSession(read,write) as session:
                await session.initialize()
                tools=await session.list_tools()
                result=await session.call_tool('public_policy',{'query':'returns'})
                if result.isError:
                    raise RuntimeError('MCP tool reported an error')
                return {'tools':[t.name for t in tools.tools],'result':result.model_dump()}
    save('21_mcp.json',run_async(call()))
