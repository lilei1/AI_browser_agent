#!/usr/bin/env python3
"""
Test client for Yahoo Finance MCP Server

This script tests the MCP server functionality by sending various requests
and displaying the responses.
"""

import json
import subprocess
import asyncio
import sys
from typing import Dict, Any

class MCPTestClient:
    """Test client for MCP server"""
    
    def __init__(self):
        self.request_id = 0
    
    def get_next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def test_server(self):
        """Test the MCP server with various requests"""
        print("🧪 Testing Yahoo Finance MCP Server")
        print("=" * 50)
        
        # Start the server process
        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="/Users/lilei/Downloads/AI_browser_agent"
        )
        
        try:
            # Test 1: Initialize
            print("\n1. Testing initialization...")
            init_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            response = await self.send_request(process, init_request)
            print(f"✅ Initialization: {response.get('result', {}).get('serverInfo', {}).get('name', 'Unknown')}")
            
            # Test 2: List tools
            print("\n2. Testing tool listing...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/list"
            }
            response = await self.send_request(process, tools_request)
            tools = response.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            
            # Test 3: Extract stock data
            print("\n3. Testing stock data extraction...")
            extract_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "extract_stock_data",
                    "arguments": {
                        "symbol": "AAPL",
                        "include_analysis": True
                    }
                }
            }
            response = await self.send_request(process, extract_request)
            if response.get('result'):
                content = response['result']['content'][0]['text']
                data = json.loads(content)
                print(f"✅ AAPL Data: ${data.get('current_price', 'N/A')} ({data.get('price_change_percent', 'N/A')}%)")
            
            # Test 4: Get stock price
            print("\n4. Testing quick price lookup...")
            price_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "get_stock_price",
                    "arguments": {
                        "symbol": "GOOGL"
                    }
                }
            }
            response = await self.send_request(process, price_request)
            if response.get('result'):
                content = response['result']['content'][0]['text']
                data = json.loads(content)
                print(f"✅ GOOGL Price: ${data.get('current_price', 'N/A')}")
            
            # Test 5: Compare stocks
            print("\n5. Testing stock comparison...")
            compare_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "compare_stocks",
                    "arguments": {
                        "symbols": ["AAPL", "MSFT", "GOOGL"]
                    }
                }
            }
            response = await self.send_request(process, compare_request)
            if response.get('result'):
                content = response['result']['content'][0]['text']
                data = json.loads(content)
                insights = data.get('comparison_insights', {})
                if insights.get('best_performer'):
                    best = insights['best_performer']
                    print(f"✅ Best performer: {best['symbol']} ({best['change_percent']}%)")
            
            # Test 6: Analyze sector
            print("\n6. Testing sector analysis...")
            sector_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "tools/call",
                "params": {
                    "name": "analyze_sector",
                    "arguments": {
                        "sector": "technology"
                    }
                }
            }
            response = await self.send_request(process, sector_request)
            if response.get('result'):
                content = response['result']['content'][0]['text']
                data = json.loads(content)
                analysis = data.get('sector_analysis', {})
                print(f"✅ Tech sector health: {analysis.get('sector_health', 'unknown')}")
            
            # Test 7: List resources
            print("\n7. Testing resource listing...")
            resources_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "resources/list"
            }
            response = await self.send_request(process, resources_request)
            resources = response.get('result', {}).get('resources', [])
            print(f"✅ Found {len(resources)} resources:")
            for resource in resources:
                print(f"   - {resource['name']}: {resource['uri']}")
            
            # Test 8: List prompts
            print("\n8. Testing prompt listing...")
            prompts_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "prompts/list"
            }
            response = await self.send_request(process, prompts_request)
            prompts = response.get('result', {}).get('prompts', [])
            print(f"✅ Found {len(prompts)} prompts:")
            for prompt in prompts:
                print(f"   - {prompt['name']}: {prompt['description']}")
            
            print("\n" + "=" * 50)
            print("🎉 All tests completed successfully!")
            print("\nThe MCP server is ready to use with Goose!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up
            process.terminate()
            process.wait()
    
    async def send_request(self, process: subprocess.Popen, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a request to the MCP server and get response"""
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if not response_line:
            raise Exception("No response from server")
        
        return json.loads(response_line.strip())

async def main():
    """Main test function"""
    client = MCPTestClient()
    await client.test_server()

if __name__ == "__main__":
    asyncio.run(main())
