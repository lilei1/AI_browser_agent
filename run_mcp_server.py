#!/usr/bin/env python3
"""
MCP Server Runner Script

This script ensures the MCP server runs with the correct Python path and environment.
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_dir))

# Change to project directory
os.chdir(project_dir)

# Ensure we have a clean environment for MCP protocol
os.environ['PYTHONUNBUFFERED'] = '1'

# Import and run the MCP server
if __name__ == "__main__":
    try:
        from mcp_server import main
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Log errors to a file instead of stderr to avoid interfering with MCP protocol
        with open('/tmp/mcp_server_error.log', 'a') as f:
            import traceback
            f.write(f"MCP Server Error: {e}\n")
            f.write(traceback.format_exc())
            f.write("\n---\n")
        sys.exit(1)
