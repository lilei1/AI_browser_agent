#!/usr/bin/env python3
"""
Example usage of Yahoo Finance MCP Server

This script demonstrates how to interact with the MCP server programmatically.
"""

import json
import subprocess
import sys
import asyncio
from typing import Dict, Any

class MCPClient:
    """Simple MCP client for demonstration"""
    
    def __init__(self):
        self.request_id = 0
        self.process = None
    
    async def start_server(self):
        """Start the MCP server"""
        self.process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Initialize the server
        await self.send_request({
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "example-client", "version": "1.0.0"}
            }
        })
    
    def get_next_id(self) -> int:
        self.request_id += 1
        return self.request_id
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server"""
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        response_line = self.process.stdout.readline()
        return json.loads(response_line.strip())
    
    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": "extract_stock_data",
                "arguments": {"symbol": symbol, "include_analysis": True}
            }
        }
        
        response = await self.send_request(request)
        if response.get('result'):
            return json.loads(response['result']['content'][0]['text'])
        return {}
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get quick stock price"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": "get_stock_price",
                "arguments": {"symbol": symbol}
            }
        }
        
        response = await self.send_request(request)
        if response.get('result'):
            return json.loads(response['result']['content'][0]['text'])
        return {}
    
    async def compare_stocks(self, symbols: list) -> Dict[str, Any]:
        """Compare multiple stocks"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": "compare_stocks",
                "arguments": {"symbols": symbols}
            }
        }
        
        response = await self.send_request(request)
        if response.get('result'):
            return json.loads(response['result']['content'][0]['text'])
        return {}
    
    async def analyze_sector(self, sector: str) -> Dict[str, Any]:
        """Analyze a market sector"""
        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {
                "name": "analyze_sector",
                "arguments": {"sector": sector}
            }
        }
        
        response = await self.send_request(request)
        if response.get('result'):
            return json.loads(response['result']['content'][0]['text'])
        return {}
    
    def close(self):
        """Close the MCP server"""
        if self.process:
            self.process.terminate()
            self.process.wait()

async def main():
    """Main example function"""
    print("🚀 Yahoo Finance MCP Server Example")
    print("=" * 50)
    
    client = MCPClient()
    
    try:
        # Start the server
        print("Starting MCP server...")
        await client.start_server()
        print("✅ Server started successfully")
        
        # Example 1: Get Apple stock data
        print("\n📊 Example 1: Getting Apple (AAPL) stock data")
        aapl_data = await client.get_stock_data("AAPL")
        if aapl_data.get('success'):
            print(f"Company: {aapl_data['company_name']}")
            
            price = aapl_data['current_price']
            if price is not None:
                print(f"Price: ${price:.2f}")
            else:
                print("Price: N/A")
            
            change_pct = aapl_data['price_change_percent']
            if change_pct is not None:
                print(f"Change: {change_pct:+.2f}%")
            else:
                print("Change: N/A")
            
            print(f"Market Cap: {aapl_data['market_cap'] or 'N/A'}")
            
            # Show analysis if available
            analysis = aapl_data.get('analysis', {})
            if analysis:
                print(f"Trend: {analysis['price_trend']}")
                print(f"Valuation: {analysis['valuation_note']}")
        
        # Example 2: Quick price lookup
        print("\n💰 Example 2: Quick price lookup for Google")
        googl_price = await client.get_stock_price("GOOGL")
        if googl_price.get('success'):
            price = googl_price['current_price']
            change_pct = googl_price['price_change_percent']
            
            price_str = f"${price:.2f}" if price is not None else "N/A"
            change_str = f"({change_pct:+.2f}%)" if change_pct is not None else "(N/A)"
            
            print(f"GOOGL: {price_str} {change_str}")
        
        # Example 3: Compare tech stocks
        print("\n🔄 Example 3: Comparing tech stocks")
        comparison = await client.compare_stocks(["AAPL", "GOOGL", "MSFT", "NVDA"])
        if comparison.get('success'):
            print("Stock Comparison:")
            for stock in comparison['stocks']:
                price = stock['current_price']
                change_pct = stock['price_change_percent']
                
                price_str = f"${price:.2f}" if price is not None else "N/A"
                change_str = f"({change_pct:+.2f}%)" if change_pct is not None else "(N/A)"
                
                print(f"  {stock['symbol']}: {price_str} {change_str}")
            
            insights = comparison.get('comparison_insights', {})
            if insights.get('best_performer'):
                best = insights['best_performer']
                change_pct = best.get('change_percent')
                if change_pct is not None:
                    print(f"\n🏆 Best performer: {best['symbol']} ({change_pct:+.2f}%)")
                else:
                    print(f"\n🏆 Best performer: {best['symbol']} (N/A%)")
        
        # Example 4: Sector analysis
        print("\n🏭 Example 4: Technology sector analysis")
        sector_data = await client.analyze_sector("technology")
        if sector_data.get('success'):
            analysis = sector_data.get('sector_analysis', {})
            print(f"Sector health: {analysis.get('sector_health', 'unknown')}")
            print(f"Average performance: {analysis.get('average_performance', 0):+.2f}%")
            print(f"Top performer: {analysis.get('top_performer', 'unknown')}")
            print(f"Stocks analyzed: {analysis.get('stocks_analyzed', 0)}")
        
        print("\n" + "=" * 50)
        print("🎉 Examples completed successfully!")
        print("\nThis demonstrates how to:")
        print("- Extract comprehensive stock data")
        print("- Get quick price lookups") 
        print("- Compare multiple stocks")
        print("- Analyze market sectors")
        print("\nYou can now integrate this with Goose or other MCP clients!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
