# Setup and Integration Guide

This guide provides step-by-step instructions on how to connect your local LLM client (such as Claude Desktop) to the PostgreSQL SRE MCP Server.

## Prerequisites

- Claude Desktop installed on your local machine.
- The `postgres-sre-mcp` repository cloned locally.
- Python 3.10+ installed.
- Required dependencies installed (`pip install -r mcp_app/requirements.txt`).

## Step 1: Locate your Configuration File

For Claude Desktop, the configuration file is typically located at:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

If the file does not exist, create it.

## Step 2: Configure the MCP Server

Edit your `claude_desktop_config.json` to include the `postgres-sre` server. You will need to specify the command to run the MCP server and point it to the correct working directory.

```json
{
  "mcpServers": {
    "postgres-sre": {
      "command": "python",
      "args": [
        "mcp_app/server.py"
      ],
      "env": {
        "API_BASE_URL": "http://localhost:8080/api/v1"
      },
      "cwd": "/path/to/your/clone/of/postgres-sre-mcp"
    }
  }
}
```

> [!IMPORTANT]
> - Ensure that the `cwd` path accurately points to the root of your `postgres-sre-mcp` directory.
> - Verify that the `API_BASE_URL` matches the address and port where your FastAPI layer is running.
> - On Windows, use double backslashes (`\\`) or forward slashes (`/`) in the `cwd` path.

## Step 3: Start the Backend API

Before using the tools in Claude Desktop, you must ensure the FastAPI backend is running, as the MCP server delegates all database operations to it.

```bash
cd /path/to/your/clone/of/postgres-sre-mcp
docker-compose up -d
```
*Note: Make sure the docker environment brings up both PostgreSQL and the FastAPI application successfully.*

## Step 4: Restart Claude Desktop

1. Fully close the Claude Desktop application.
2. Re-open Claude Desktop.
3. Open a new chat.

You should now see the `postgres-sre` tools available for use (often indicated by a "plug" or "tools" icon in the interface). Try prompting Claude with: *"Check for any active database sessions using the postgres-sre tools."*
