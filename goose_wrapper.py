#!/usr/bin/env python3
"""
Direct wrapper for Goose to call Yahoo Finance functions
This bypasses MCP protocol issues
"""

import sys
import os
import json
from pathlib import Path

# Add project directory to Python path
project_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_dir))
os.chdir(project_dir)

from basic_demo import scrape_yahoo_finance_basic

def get_stock_price(symbol):
    """Get stock price - direct function call"""
    try:
        data = scrape_yahoo_finance_basic(symbol.upper())
        if data and data.get('current_price') is not None:
            return {
                "success": True,
                "symbol": data['symbol'],
                "company_name": data['company_name'],
                "current_price": data['current_price'],
                "price_change": data.get('price_change'),
                "price_change_percent": data.get('price_change_percent'),
                "market_cap": data.get('market_cap')
            }
        else:
            return {
                "success": False,
                "symbol": symbol,
                "error": "No price data available for this symbol"
            }
    except Exception as e:
        return {
            "success": False,
            "symbol": symbol,
            "error": str(e)
        }

def compare_stocks(symbols):
    """Compare multiple stocks"""
    results = []
    for symbol in symbols:
        data = get_stock_price(symbol)
        if data['success']:
            results.append(data)
    
    if not results:
        return {"success": False, "error": "No valid stock data found"}
    
    # Find best performer
    valid_stocks = [s for s in results if s.get('price_change_percent') is not None]
    if valid_stocks:
        best = max(valid_stocks, key=lambda x: x['price_change_percent'])
        worst = min(valid_stocks, key=lambda x: x['price_change_percent'])
        
        return {
            "success": True,
            "stocks": results,
            "best_performer": best,
            "worst_performer": worst
        }
    else:
        return {
            "success": True,
            "stocks": results,
            "note": "No price change data available for comparison"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python goose_wrapper.py <command> [args...]")
        print("Commands:")
        print("  price <symbol>          - Get stock price")
        print("  compare <symbol1> <symbol2> ... - Compare stocks")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "price" and len(sys.argv) == 3:
        symbol = sys.argv[2]
        result = get_stock_price(symbol)
        print(json.dumps(result, indent=2))
        
    elif command == "compare" and len(sys.argv) > 3:
        symbols = sys.argv[2:]
        result = compare_stocks(symbols)
        print(json.dumps(result, indent=2))
        
    else:
        print("Invalid command or arguments")
        sys.exit(1)
