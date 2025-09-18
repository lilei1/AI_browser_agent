#!/bin/bash
# MCP Server Startup Script

cd "/Users/lilei/Downloads/AI_browser_agent"
export PYTHONPATH="/Users/lilei/Downloads/AI_browser_agent:$PYTHONPATH"
python mcp_server.py
