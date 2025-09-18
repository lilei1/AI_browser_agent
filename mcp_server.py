#!/usr/bin/env python3
"""
Yahoo Finance MCP Server

This server exposes Yahoo Finance data extraction capabilities via the Model Context Protocol (MCP).
It provides tools for stock data extraction, price monitoring, and financial analysis that can be
used by AI agents like Goose for chatbot functionality.
"""

import json
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import traceback

# Import the existing Yahoo Finance functionality
from basic_demo import scrape_yahoo_finance_basic

# Configure logging - redirect to file to avoid interfering with MCP protocol
import tempfile
log_file = tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, prefix='mcp_server_')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file.name),
        # Only log to stderr if not running as MCP server
        logging.StreamHandler(sys.stderr) if '--debug' in sys.argv else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """Represents an MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]

@dataclass
class MCPResource:
    """Represents an MCP resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str

@dataclass
class MCPPrompt:
    """Represents an MCP prompt definition"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]

class YahooFinanceMCPServer:
    """
    MCP Server for Yahoo Finance data extraction
    
    Exposes the following capabilities:
    - Stock data extraction for any publicly traded company
    - Real-time price monitoring
    - Financial analysis and insights
    - Multi-company batch processing
    """
    
    def __init__(self):
        self.name = "yahoo-finance-agent"
        self.version = "1.0.0"
        
        # Define available tools
        self.tools = [
            MCPTool(
                name="extract_stock_data",
                description="Extract comprehensive stock data for a given symbol including price, volume, market cap, and financial ratios",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                        },
                        "include_analysis": {
                            "type": "boolean",
                            "description": "Whether to include basic financial analysis",
                            "default": True
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            MCPTool(
                name="get_stock_price",
                description="Get current stock price and basic information quickly",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                        }
                    },
                    "required": ["symbol"]
                }
            ),
            MCPTool(
                name="compare_stocks",
                description="Compare multiple stocks side by side",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of stock symbols to compare",
                            "minItems": 2,
                            "maxItems": 10
                        }
                    },
                    "required": ["symbols"]
                }
            ),
            MCPTool(
                name="analyze_sector",
                description="Analyze stocks within a specific sector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sector": {
                            "type": "string",
                            "enum": ["technology", "finance", "healthcare", "energy", "consumer", "automotive"],
                            "description": "Sector to analyze"
                        }
                    },
                    "required": ["sector"]
                }
            ),
            MCPTool(
                name="validate_symbol",
                description="Validate if a stock symbol exists and get basic company information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol to validate"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        ]
        
        # Define available resources
        self.resources = [
            MCPResource(
                uri="yahoo-finance://market-status",
                name="Market Status",
                description="Current market status and trading hours",
                mimeType="application/json"
            ),
            MCPResource(
                uri="yahoo-finance://supported-sectors",
                name="Supported Sectors",
                description="List of supported market sectors with example companies",
                mimeType="application/json"
            )
        ]
        
        # Define available prompts
        self.prompts = [
            MCPPrompt(
                name="analyze_stock_performance",
                description="Generate a comprehensive analysis of stock performance",
                arguments=[
                    {
                        "name": "symbol",
                        "description": "Stock symbol to analyze",
                        "required": True
                    },
                    {
                        "name": "timeframe",
                        "description": "Analysis timeframe (daily, weekly, monthly)",
                        "required": False
                    }
                ]
            ),
            MCPPrompt(
                name="investment_recommendation",
                description="Generate investment recommendations based on stock data",
                arguments=[
                    {
                        "name": "symbols",
                        "description": "List of stock symbols to analyze",
                        "required": True
                    },
                    {
                        "name": "risk_tolerance",
                        "description": "Risk tolerance level (low, medium, high)",
                        "required": False
                    }
                ]
            )
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                return await self.handle_initialize(params)
            elif method == "tools/list":
                return await self.handle_list_tools()
            elif method == "tools/call":
                return await self.handle_call_tool(params)
            elif method == "resources/list":
                return await self.handle_list_resources()
            elif method == "resources/read":
                return await self.handle_read_resource(params)
            elif method == "prompts/list":
                return await self.handle_list_prompts()
            elif method == "prompts/get":
                return await self.handle_get_prompt(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            logger.error(traceback.format_exc())
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        return {
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                }
            }
        }
    
    async def handle_list_tools(self) -> Dict[str, Any]:
        """Return list of available tools"""
        return {
            "result": {
                "tools": [asdict(tool) for tool in self.tools]
            }
        }
    
    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "extract_stock_data":
                result = await self.extract_stock_data(arguments)
            elif tool_name == "get_stock_price":
                result = await self.get_stock_price(arguments)
            elif tool_name == "compare_stocks":
                result = await self.compare_stocks(arguments)
            elif tool_name == "analyze_sector":
                result = await self.analyze_sector(arguments)
            elif tool_name == "validate_symbol":
                result = await self.validate_symbol(arguments)
            else:
                return {
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, default=str)
                        }
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    async def extract_stock_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive stock data"""
        symbol = arguments.get("symbol", "").upper()
        include_analysis = arguments.get("include_analysis", True)
        
        if not symbol:
            raise ValueError("Symbol is required")
        
        logger.info(f"Extracting stock data for {symbol}")
        
        # Use the existing scraping functionality
        data = scrape_yahoo_finance_basic(symbol)
        
        if not data or "error" in data:
            return {
                "success": False,
                "error": f"Failed to extract data for {symbol}",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
        
        result = {
            "success": True,
            "symbol": symbol,
            "company_name": data.get("company_name", symbol),
            "current_price": data.get("current_price"),
            "price_change": data.get("price_change"),
            "price_change_percent": data.get("price_change_percent"),
            "previous_close": data.get("previous_close"),
            "market_cap": data.get("market_cap"),
            "volume": data.get("volume"),
            "pe_ratio": data.get("pe_ratio"),
            "eps": data.get("eps"),
            "timestamp": datetime.now().isoformat()
        }
        
        if include_analysis:
            result["analysis"] = self._generate_basic_analysis(data)
        
        return result
    
    async def get_stock_price(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get current stock price quickly"""
        symbol = arguments.get("symbol", "").upper()
        
        if not symbol:
            raise ValueError("Symbol is required")
        
        logger.info(f"Getting price for {symbol}")
        
        data = scrape_yahoo_finance_basic(symbol)
        
        if not data or "error" in data:
            return {
                "success": False,
                "error": f"Failed to get price for {symbol}",
                "symbol": symbol
            }
        
        return {
            "success": True,
            "symbol": symbol,
            "company_name": data.get("company_name", symbol),
            "current_price": data.get("current_price"),
            "price_change": data.get("price_change"),
            "price_change_percent": data.get("price_change_percent"),
            "timestamp": datetime.now().isoformat()
        }
    
    async def compare_stocks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple stocks"""
        symbols = arguments.get("symbols", [])
        
        if not symbols or len(symbols) < 2:
            raise ValueError("At least 2 symbols are required for comparison")
        
        logger.info(f"Comparing stocks: {', '.join(symbols)}")
        
        results = []
        for symbol in symbols:
            data = scrape_yahoo_finance_basic(symbol.upper())
            if data and "error" not in data:
                results.append({
                    "symbol": symbol.upper(),
                    "company_name": data.get("company_name", symbol),
                    "current_price": data.get("current_price"),
                    "price_change_percent": data.get("price_change_percent"),
                    "market_cap": data.get("market_cap"),
                    "volume": data.get("volume"),
                    "pe_ratio": data.get("pe_ratio")
                })
        
        if not results:
            return {
                "success": False,
                "error": "No valid stock data found for comparison"
            }
        
        # Add comparison insights
        comparison = {
            "success": True,
            "stocks": results,
            "comparison_insights": self._generate_comparison_insights(results),
            "timestamp": datetime.now().isoformat()
        }
        
        return comparison
    
    async def analyze_sector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stocks within a specific sector"""
        sector = arguments.get("sector", "").lower()
        
        # Define sector symbols
        sector_symbols = {
            "technology": ["AAPL", "GOOGL", "MSFT", "NVDA", "META"],
            "finance": ["JPM", "BAC", "WFC", "GS"],
            "healthcare": ["JNJ", "PFE", "MRNA", "UNH"],
            "energy": ["XOM", "CVX", "BP"],
            "consumer": ["KO", "PEP", "PG", "WMT"],
            "automotive": ["TSLA", "GM", "F"]
        }
        
        if sector not in sector_symbols:
            raise ValueError(f"Unsupported sector: {sector}")
        
        symbols = sector_symbols[sector]
        logger.info(f"Analyzing {sector} sector with symbols: {', '.join(symbols)}")
        
        results = []
        for symbol in symbols:
            data = scrape_yahoo_finance_basic(symbol)
            if data and "error" not in data:
                results.append({
                    "symbol": symbol,
                    "company_name": data.get("company_name", symbol),
                    "current_price": data.get("current_price"),
                    "price_change_percent": data.get("price_change_percent"),
                    "market_cap": data.get("market_cap"),
                    "pe_ratio": data.get("pe_ratio")
                })
        
        return {
            "success": True,
            "sector": sector.title(),
            "stocks": results,
            "sector_analysis": self._generate_sector_analysis(results, sector),
            "timestamp": datetime.now().isoformat()
        }
    
    async def validate_symbol(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a stock symbol"""
        symbol = arguments.get("symbol", "").upper()
        
        if not symbol:
            raise ValueError("Symbol is required")
        
        logger.info(f"Validating symbol {symbol}")
        
        data = scrape_yahoo_finance_basic(symbol)
        
        if not data or "error" in data:
            return {
                "valid": False,
                "symbol": symbol,
                "error": "Symbol not found or data unavailable"
            }
        
        return {
            "valid": True,
            "symbol": symbol,
            "company_name": data.get("company_name", symbol),
            "has_price_data": data.get("current_price") is not None,
            "has_volume_data": data.get("volume") is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_basic_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic financial analysis"""
        analysis = {
            "price_trend": "neutral",
            "volume_assessment": "unknown",
            "valuation_note": "",
            "key_metrics": {}
        }
        
        # Price trend analysis
        if data.get("price_change_percent"):
            change_pct = data["price_change_percent"]
            if change_pct > 2:
                analysis["price_trend"] = "strongly_positive"
            elif change_pct > 0:
                analysis["price_trend"] = "positive"
            elif change_pct < -2:
                analysis["price_trend"] = "strongly_negative"
            elif change_pct < 0:
                analysis["price_trend"] = "negative"
        
        # P/E ratio assessment
        if data.get("pe_ratio"):
            pe = data["pe_ratio"]
            if pe < 15:
                analysis["valuation_note"] = "Potentially undervalued (low P/E)"
            elif pe > 30:
                analysis["valuation_note"] = "Potentially overvalued (high P/E)"
            else:
                analysis["valuation_note"] = "Reasonably valued"
        
        # Key metrics summary
        analysis["key_metrics"] = {
            "current_price": data.get("current_price"),
            "market_cap": data.get("market_cap"),
            "pe_ratio": data.get("pe_ratio"),
            "daily_change": data.get("price_change_percent")
        }
        
        return analysis
    
    def _generate_comparison_insights(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights from stock comparison"""
        if not stocks:
            return {}
        
        # Find best and worst performers
        valid_stocks = [s for s in stocks if s.get("price_change_percent") is not None]
        
        if not valid_stocks:
            return {"note": "No price change data available for comparison"}
        
        best_performer = max(valid_stocks, key=lambda x: x["price_change_percent"])
        worst_performer = min(valid_stocks, key=lambda x: x["price_change_percent"])
        
        # Calculate average performance
        avg_change = sum(s["price_change_percent"] for s in valid_stocks) / len(valid_stocks)
        
        return {
            "best_performer": {
                "symbol": best_performer["symbol"],
                "company": best_performer["company_name"],
                "change_percent": best_performer["price_change_percent"]
            },
            "worst_performer": {
                "symbol": worst_performer["symbol"],
                "company": worst_performer["company_name"],
                "change_percent": worst_performer["price_change_percent"]
            },
            "average_change": round(avg_change, 2),
            "total_stocks_analyzed": len(valid_stocks)
        }
    
    def _generate_sector_analysis(self, stocks: List[Dict[str, Any]], sector: str) -> Dict[str, Any]:
        """Generate sector-specific analysis"""
        if not stocks:
            return {}
        
        valid_stocks = [s for s in stocks if s.get("price_change_percent") is not None]
        
        if not valid_stocks:
            return {"note": f"No price data available for {sector} sector analysis"}
        
        avg_change = sum(s["price_change_percent"] for s in valid_stocks) / len(valid_stocks)
        
        # Sector health assessment
        if avg_change > 1:
            health = "strong"
        elif avg_change > 0:
            health = "positive"
        elif avg_change > -1:
            health = "mixed"
        else:
            health = "weak"
        
        return {
            "sector_health": health,
            "average_performance": round(avg_change, 2),
            "stocks_analyzed": len(valid_stocks),
            "top_performer": max(valid_stocks, key=lambda x: x["price_change_percent"])["symbol"],
            "sector_note": f"The {sector} sector is showing {health} performance today"
        }
    
    async def handle_list_resources(self) -> Dict[str, Any]:
        """Return list of available resources"""
        return {
            "result": {
                "resources": [asdict(resource) for resource in self.resources]
            }
        }
    
    async def handle_read_resource(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a specific resource"""
        uri = params.get("uri")
        
        if uri == "yahoo-finance://market-status":
            return {
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps({
                                "market_open": True,  # Simplified - would need real market hours logic
                                "trading_session": "regular",
                                "timezone": "EST",
                                "last_updated": datetime.now().isoformat()
                            })
                        }
                    ]
                }
            }
        elif uri == "yahoo-finance://supported-sectors":
            return {
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps({
                                "sectors": {
                                    "technology": ["AAPL", "GOOGL", "MSFT", "NVDA", "META"],
                                    "finance": ["JPM", "BAC", "WFC", "GS"],
                                    "healthcare": ["JNJ", "PFE", "MRNA", "UNH"],
                                    "energy": ["XOM", "CVX", "BP"],
                                    "consumer": ["KO", "PEP", "PG", "WMT"],
                                    "automotive": ["TSLA", "GM", "F"]
                                }
                            })
                        }
                    ]
                }
            }
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Resource not found: {uri}"
                }
            }
    
    async def handle_list_prompts(self) -> Dict[str, Any]:
        """Return list of available prompts"""
        return {
            "result": {
                "prompts": [asdict(prompt) for prompt in self.prompts]
            }
        }
    
    async def handle_get_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific prompt"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "analyze_stock_performance":
            symbol = arguments.get("symbol", "AAPL")
            timeframe = arguments.get("timeframe", "daily")
            
            return {
                "result": {
                    "description": f"Comprehensive analysis of {symbol} stock performance",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Please analyze the stock performance of {symbol} with a {timeframe} timeframe. Include price trends, volume analysis, and key financial metrics. Provide investment insights based on the data."
                            }
                        }
                    ]
                }
            }
        elif name == "investment_recommendation":
            symbols = arguments.get("symbols", ["AAPL"])
            risk_tolerance = arguments.get("risk_tolerance", "medium")
            
            symbols_str = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
            
            return {
                "result": {
                    "description": f"Investment recommendations for {symbols_str}",
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": f"Based on the financial data for {symbols_str}, provide investment recommendations suitable for a {risk_tolerance} risk tolerance investor. Include buy/hold/sell recommendations with reasoning."
                            }
                        }
                    ]
                }
            }
        else:
            return {
                "error": {
                    "code": -32602,
                    "message": f"Prompt not found: {name}"
                }
            }

async def main():
    """Main server loop"""
    server = YahooFinanceMCPServer()
    logger.info(f"Starting Yahoo Finance MCP Server v{server.version}")
    
    try:
        # Read from stdin and write to stdout (MCP protocol)
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    logger.info("EOF received, shutting down")
                    break
                
                line = line.strip()
                if not line:
                    continue
                    
                logger.debug(f"Received request: {line}")
                request = json.loads(line)
                response = await server.handle_request(request)
                
                # Add request ID if present
                if "id" in request:
                    response["id"] = request["id"]
                
                # Add jsonrpc version
                response["jsonrpc"] = "2.0"
                
                response_json = json.dumps(response)
                logger.debug(f"Sending response: {response_json}")
                print(response_json)
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                logger.error(traceback.format_exc())
                # Don't break on individual request errors
                continue
                
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
    finally:
        logger.info("MCP Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
