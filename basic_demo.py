#!/usr/bin/env python3
"""
Basic Yahoo Finance Data Extraction Demo (No Browser Required)
"""
import sys
import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def clean_numeric_value(value):
    """Clean and convert string numeric values to float"""
    if not value or value in ['N/A', '--', '']:
        return None
    
    try:
        # Remove common formatting characters
        cleaned = str(value).strip()
        cleaned = re.sub(r'[,$%+\s]', '', cleaned)
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return float(cleaned)
        
    except (ValueError, TypeError, AttributeError):
        return None

def scrape_yahoo_finance_basic(symbol="AAPL"):
    """Basic Yahoo Finance scraping using requests"""
    url = f"https://finance.yahoo.com/quote/{symbol}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic data
        data = {
            'symbol': symbol,
            'company_name': symbol,  # Default fallback
            'current_price': None,
            'price_change': None,
            'price_change_percent': None,
            'previous_close': None,
            'market_cap': None,
            'volume': None
        }
        
        # Try to find company name
        h1_elements = soup.find_all('h1')
        for h1 in h1_elements:
            if symbol in h1.text:
                data['company_name'] = h1.text.split('(')[0].strip()
                break
        
        # Look for price data in various formats
        # Method 1: Look for data attributes
        price_elements = soup.find_all(attrs={"data-symbol": symbol})
        for element in price_elements:
            field = element.get("data-field", "")
            if field == "regularMarketPrice":
                data['current_price'] = clean_numeric_value(element.text)
            elif field == "regularMarketChange":
                data['price_change'] = clean_numeric_value(element.text)
            elif field == "regularMarketChangePercent":
                data['price_change_percent'] = clean_numeric_value(element.text.replace('%', ''))
        
        # Method 2: Look for specific test IDs
        test_ids = {
            'PREV_CLOSE-value': 'previous_close',
            'MARKET_CAP-value': 'market_cap',
            'TD_VOLUME-value': 'volume'
        }
        
        for test_id, field in test_ids.items():
            element = soup.find(attrs={"data-testid": test_id})
            if element:
                if field == 'volume':
                    # Handle volume with K, M, B suffixes
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
                else:
                    data[field] = element.text if field == 'market_cap' else clean_numeric_value(element.text)
        
        # Method 3: Look in tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].text.strip().lower()
                    value = cells[1].text.strip()
                    
                    if "previous close" in label and not data['previous_close']:
                        data['previous_close'] = clean_numeric_value(value)
                    elif "market cap" in label and not data['market_cap']:
                        data['market_cap'] = value
                    elif "volume" in label and not data['volume']:
                        # Handle volume parsing
                        if 'K' in value.upper():
                            base = clean_numeric_value(value.replace('K', '').replace('k', ''))
                            data['volume'] = int(base * 1000) if base else None
                        elif 'M' in value.upper():
                            base = clean_numeric_value(value.replace('M', '').replace('m', ''))
                            data['volume'] = int(base * 1000000) if base else None
                        else:
                            data['volume'] = clean_numeric_value(value)
        
        return data
        
    except Exception as e:
        print(f"Error scraping {symbol}: {str(e)}")
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

def main():
    """Basic demo of Yahoo Finance data extraction"""
    console = Console()
    
    # Welcome message
    welcome_text = Text("Yahoo Finance Basic Data Extraction", style="bold blue", justify="center")
    welcome_panel = Panel(
        welcome_text + "\n\n" + 
        "📊 Simple stock data extraction using HTTP requests\n" +
        "🌐 No browser automation required\n" +
        "⚡ Fast and lightweight\n\n" +
        "Extracting Apple (AAPL) stock data from Yahoo Finance",
        title="Welcome",
        border_style="blue"
    )
    console.print(welcome_panel)
    
    try:
        # Extract stock data
        console.print("\n[bold cyan]Extracting AAPL Stock Data[/bold cyan]")
        console.print("⏳ Fetching data from Yahoo Finance...")
        
        start_time = datetime.now()
        data = scrape_yahoo_finance_basic("AAPL")
        end_time = datetime.now()
        
        if data:
            extraction_time = (end_time - start_time).total_seconds()
            console.print(f"✅ Data extracted successfully in {extraction_time:.2f}s")
            
            # Display results in a table
            table = Table(title=f"{data['company_name']} ({data['symbol']}) - Stock Information")
            table.add_column("Metric", style="cyan", width=20)
            table.add_column("Value", style="green", width=20)
            
            # Add data to table
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
            
            console.print(table)
            
            # Save basic report
            report_lines = [
                f"BASIC STOCK REPORT: {data['company_name']} ({data['symbol']})",
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
                "",
                f"Extraction Time: {extraction_time:.2f} seconds",
                "=" * 50
            ]
            
            report_content = "\n".join(report_lines)
            
            # Save report
            os.makedirs("data", exist_ok=True)
            report_file = "data/basic_aapl_report.txt"
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            console.print(f"\n📄 Basic report saved: {report_file}")
            
            # Success summary
            success_panel = Panel(
                "✅ Successfully extracted basic stock data\n" +
                "✅ Generated and saved report\n" +
                "✅ No browser automation required\n\n" +
                f"📁 Generated file: {report_file}\n\n" +
                "🚀 Basic functionality working!",
                title="Demo Summary",
                border_style="green"
            )
            console.print(success_panel)
            
        else:
            console.print("❌ Failed to extract stock data")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed with error: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    console.print("\n[dim]Thank you for trying the basic Yahoo Finance extractor![/dim]")

if __name__ == "__main__":
    main()
