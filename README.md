# PostgreSQL SRE MCP Server

A production-grade Model Context Protocol (MCP) server for PostgreSQL Site Reliability Engineers.

## Architecture
1. **LLM**: Decides which tool to call based on the SRE's intent.
2. **MCP Server**: FastMCP application exposing 25 focused tools. Communicates only over HTTP.
3. **REST API**: FastAPI application containing hardcoded SQL, caching, and connection pooling.
4. **PostgreSQL**: The target database, accessed via restricted roles.

## Quick Start
1. Clone the repository.
2. Run `docker-compose up -d --build`. This starts PostgreSQL, the API, and the MCP Server.
### Connecting Clients

**1. Streamable HTTP (SSE) Clients**
The server is actively running an SSE endpoint at `http://localhost:8001/sse`. You can connect any modern HTTP/SSE MCP client or the MCP Inspector to this URL.

**2. Claude Desktop (Standard I/O)**
Claude Desktop currently only supports `stdio` connections natively and cannot connect directly to an `http://` URL without a custom bridge script. 
However, since the API handles all the heavy lifting, the cleanest solution is to let Claude Desktop spawn a dedicated `stdio` instance of the MCP server inside the existing Docker container!

Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "postgres-sre": {
      "command": "docker",
      "args": ["exec", "-i", "mcp-server", "python", "mcp_app/server.py"]
    }
  }
}
```
*(This starts a lightweight stdio process specifically for Claude, while your main SSE server remains running on port 8001 for other HTTP integrations).*

## Security
- No LLM-generated SQL. All SQL is hardcoded.
- Distinct `sre_read` and `sre_ops` roles.
- All POST actions are audit-logged.

## Testing
Run `pytest` in the `tests` directory to execute unit and integration tests.
