#!/usr/bin/env python3
"""
Simple Yahoo Finance CLI (Python 3.7 compatible)
"""
import sys
import os
import click
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def clean_numeric_value(value):
    """Clean and convert string numeric values to float"""
    if not value or value in ['N/A', '--', '']:
        return None
    
    try:
        cleaned = str(value).strip()
        cleaned = re.sub(r'[,$%+\s]', '', cleaned)
        
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return float(cleaned)
        
    except (ValueError, TypeError, AttributeError):
        return None

def format_currency(value):
    """Format numeric value as currency"""
    if value is None:
        return "N/A"
    return f"${value:,.2f}"

def format_volume(volume):
    """Format volume with appropriate suffix"""
    if volume is None:
        return "N/A"
    
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return f"{volume:,}"

def scrape_yahoo_finance(symbol):
    """Scrape Yahoo Finance data using requests"""
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            'symbol': symbol,
            'company_name': symbol,
            'current_price': None,
            'price_change': None,
            'price_change_percent': None,
            'previous_close': None,
            'market_cap': None,
            'volume': None,
            'pe_ratio': None,
            'eps': None
        }
        
        # Find company name
        h1_elements = soup.find_all('h1')
        for h1 in h1_elements:
            if symbol in h1.text:
                data['company_name'] = h1.text.split('(')[0].strip()
                break
        
        # Look for price data
        price_elements = soup.find_all(attrs={"data-symbol": symbol})
        for element in price_elements:
            field = element.get("data-field", "")
            if field == "regularMarketPrice":
                data['current_price'] = clean_numeric_value(element.text)
            elif field == "regularMarketChange":
                data['price_change'] = clean_numeric_value(element.text)
            elif field == "regularMarketChangePercent":
                data['price_change_percent'] = clean_numeric_value(element.text.replace('%', ''))
        
        # Look for other data
        test_ids = {
            'PREV_CLOSE-value': 'previous_close',
            'MARKET_CAP-value': 'market_cap',
            'TD_VOLUME-value': 'volume',
            'PE_RATIO-value': 'pe_ratio',
            'EPS_RATIO-value': 'eps'
        }
        
        for test_id, field in test_ids.items():
            element = soup.find(attrs={"data-testid": test_id})
            if element:
                if field == 'volume':
                    volume_text = element.text
                    if 'K' in volume_text.upper():
                        base = clean_numeric_value(volume_text.replace('K', '').replace('k', ''))
                        data[field] = int(base * 1000) if base else None
                    elif 'M' in volume_text.upper():
                        base = clean_numeric_value(volume_text.replace('M', '').replace('m', ''))
                        data[field] = int(base * 1000000) if base else None
                    elif 'B' in volume_text.upper():
                        base = clean_numeric_value(volume_text.replace('B', '').replace('b', ''))
                        data[field] = int(base * 1000000000) if base else None
                    else:
                        data[field] = clean_numeric_value(volume_text)
                elif field == 'market_cap':
                    data[field] = element.text
                else:
                    data[field] = clean_numeric_value(element.text)
        
        return data
        
    except Exception as e:
        return {"error": str(e)}

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Simple Yahoo Finance CLI - Extract stock data without browser automation"""
    pass

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol to extract')
@click.option('--save-report', is_flag=True, help='Save report to file')
def extract(symbol: str, save_report: bool):
    """Extract stock data for a symbol"""
    
    console = Console()
    
    try:
        console.print(f"⏳ Extracting data for {symbol}...")
        
        start_time = datetime.now()
        data = scrape_yahoo_finance(symbol.upper())
        end_time = datetime.now()
        
        if "error" in data:
            console.print(f"❌ Error: {data['error']}")
            sys.exit(1)
        
        extraction_time = (end_time - start_time).total_seconds()
        
        # Display results
        table = Table(title=f"{data['company_name']} ({data['symbol']}) - Stock Information")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green", width=20)
        
        table.add_row("Current Price", format_currency(data['current_price']))
        
        if data['price_change'] is not None:
            change_color = "green" if data['price_change'] >= 0 else "red"
            change_text = f"{format_currency(data['price_change'])}"
            if data['price_change_percent'] is not None:
                change_text += f" ({data['price_change_percent']:+.2f}%)"
            table.add_row("Price Change", f"[{change_color}]{change_text}[/{change_color}]")
        
        table.add_row("Previous Close", format_currency(data['previous_close']))
        table.add_row("Market Cap", data['market_cap'] or "N/A")
        table.add_row("Volume", format_volume(data['volume']))
        
        if data['pe_ratio']:
            table.add_row("P/E Ratio", f"{data['pe_ratio']:.2f}")
        
        if data['eps']:
            table.add_row("EPS", format_currency(data['eps']))
        
        console.print(table)
        console.print(f"\n✅ Data extracted in {extraction_time:.2f}s")
        
        # Save report if requested
        if save_report:
            os.makedirs("data", exist_ok=True)
            
            report_lines = [
                f"STOCK REPORT: {data['company_name']} ({data['symbol']})",
                "=" * 50,
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "STOCK INFORMATION:",
                f"Current Price: {format_currency(data['current_price'])}",
                f"Price Change: {format_currency(data['price_change'])}",
                f"Price Change %: {data['price_change_percent']:+.2f}%" if data['price_change_percent'] else "Price Change %: N/A",
                f"Previous Close: {format_currency(data['previous_close'])}",
                f"Market Cap: {data['market_cap'] or 'N/A'}",
                f"Volume: {format_volume(data['volume'])}",
                f"P/E Ratio: {data['pe_ratio']:.2f}" if data['pe_ratio'] else "P/E Ratio: N/A",
                f"EPS: {format_currency(data['eps'])}" if data['eps'] else "EPS: N/A",
                "",
                f"Extraction Time: {extraction_time:.2f} seconds",
                "=" * 50
            ]
            
            report_file = f"data/{symbol.lower()}_report.txt"
            with open(report_file, 'w') as f:
                f.write("\n".join(report_lines))
            
            console.print(f"📄 Report saved: {report_file}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol')
def price(symbol: str):
    """Get current stock price quickly"""
    
    console = Console()
    
    try:
        console.print(f"⏳ Getting price for {symbol}...")
        
        data = scrape_yahoo_finance(symbol.upper())
        
        if "error" in data:
            console.print(f"❌ Error: {data['error']}")
            sys.exit(1)
        
        # Simple price display
        table = Table(title=f"{symbol.upper()} Current Price")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Current Price", format_currency(data['current_price']))
        
        if data['price_change'] is not None:
            change_color = "green" if data['price_change'] >= 0 else "red"
            table.add_row("Change", f"[{change_color}]{format_currency(data['price_change'])}[/{change_color}]")
        
        if data['price_change_percent'] is not None:
            change_color = "green" if data['price_change_percent'] >= 0 else "red"
            table.add_row("Change %", f"[{change_color}]{data['price_change_percent']:+.2f}%[/{change_color}]")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Failed to get price: {str(e)}")
        sys.exit(1)

@cli.command()
def info():
    """Show information about this CLI"""
    
    console = Console()
    
    info_panel = Panel(
        "Simple Yahoo Finance CLI\n\n" +
        "✅ Python 3.7+ compatible\n" +
        "✅ No browser automation required\n" +
        "✅ Fast HTTP-based data extraction\n" +
        "✅ Real-time stock data\n" +
        "✅ Report generation\n\n" +
        "Commands:\n" +
        "  extract --symbol AAPL --save-report\n" +
        "  price --symbol AAPL\n" +
        "  info\n\n" +
        "Note: This is a simplified version for Python 3.7.\n" +
        "For full features, upgrade to Python 3.8+ and use main.py",
        title="CLI Information",
        border_style="blue"
    )
    console.print(info_panel)

if __name__ == '__main__':
    cli()
