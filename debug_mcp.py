#!/usr/bin/env python3
"""
Debug script to test MCP server responses
"""
import subprocess
import json
import sys

def test_mcp_server():
    """Test the MCP server with the exact command Goose uses"""
    cmd = [
        '/Users/lilei/.local/bin/uv', 'run', 
        '--directory', '/Users/lilei/Downloads/AI_browser_agent',
        'python', 'run_mcp_server.py'
    ]
    
    print("🧪 Testing MCP Server Communication")
    print("=" * 50)
    
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, text=True)
        
        # Test 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "debug-test", "version": "1.0"}
            }
        }
        
        print("1. Testing initialization...")
        stdout, stderr = proc.communicate(input=json.dumps(init_request) + "\n", timeout=10)
        
        if stderr:
            print(f"❌ STDERR: {stderr}")
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                print(f"✅ Initialization successful")
                print(f"   Server: {response['result']['serverInfo']['name']}")
                print(f"   Version: {response['result']['serverInfo']['version']}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw output: {stdout}")
        
        # Test 2: List tools
        proc2 = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, text=True)
        
        tools_request = {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list"
        }
        
        print("\n2. Testing tool listing...")
        stdout, stderr = proc2.communicate(input=json.dumps(tools_request) + "\n", timeout=10)
        
        if stderr:
            print(f"❌ STDERR: {stderr}")
            
        if stdout:
            try:
                response = json.loads(stdout.strip())
                if 'result' in response and 'tools' in response['result']:
                    tools = response['result']['tools']
                    print(f"✅ Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool['description']}")
                else:
                    print(f"❌ No tools found in response: {response}")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw output: {stdout}")
        
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        proc.kill()
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_mcp_server()
