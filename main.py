#!/usr/bin/env python3
"""
Yahoo Finance AI Browser Agent - Main CLI Interface
"""
import click
import asyncio
from typing import Optional
from loguru import logger
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.ui import FinanceDashboard, ReportGenerator
# from src.yahoo_finance_agent.data import DataProcessor  # Disabled for Python 3.7
from config import settings, create_directories

# Setup logging
logger.remove()
logger.add(
    settings.log_file,
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    rotation="10 MB"
)
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}"
)

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Yahoo Finance AI Browser Agent - Extract and analyze stock data with AI"""
    create_directories()

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol to analyze')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
@click.option('--analysis/--no-analysis', default=True, help='Include AI analysis')
@click.option('--save-report', is_flag=True, help='Save report to file')
@click.option('--output-format', type=click.Choice(['text', 'json']), default='text', help='Output format')
def extract(symbol: str, headless: bool, analysis: bool, save_report: bool, output_format: str):
    """Extract comprehensive stock data for a symbol"""
    
    dashboard = FinanceDashboard()
    report_generator = ReportGenerator()
    
    try:
        dashboard.console.print(f"⏳ Extracting data for {symbol}...")

        # Use the working HTTP-based scraping method
        from basic_demo import scrape_yahoo_finance_basic

        data = scrape_yahoo_finance_basic(symbol.upper())

        if data and "error" not in data:
            # Display results in a table
            from rich.table import Table

            table = Table(title=f"{data['company_name']} ({data['symbol']}) - Stock Information")
            table.add_column("Metric", style="cyan", width=20)
            table.add_column("Value", style="green", width=20)

            # Format currency helper
            def format_currency(value):
                return f"${value:,.2f}" if value is not None else "N/A"

            def format_volume(volume):
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

            if data.get('pe_ratio'):
                table.add_row("P/E Ratio", f"{data['pe_ratio']:.2f}")

            if data.get('eps'):
                table.add_row("EPS", format_currency(data['eps']))

            dashboard.console.print(table)
            dashboard.display_success(f"Successfully extracted data for {symbol}")

            # Save report if requested
            if save_report:
                import os
                os.makedirs("data", exist_ok=True)

                from datetime import datetime

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
                    f"P/E Ratio: {data['pe_ratio']:.2f}" if data.get('pe_ratio') else "P/E Ratio: N/A",
                    f"EPS: {format_currency(data['eps'])}" if data.get('eps') else "EPS: N/A",
                    "",
                    "=" * 50
                ]

                if output_format == 'json':
                    import json
                    report_content = json.dumps(data, indent=2, default=str)
                    filename = f"data/{symbol.lower()}_report.json"
                else:
                    report_content = "\n".join(report_lines)
                    filename = f"data/{symbol.lower()}_report.txt"

                with open(filename, 'w') as f:
                    f.write(report_content)

                dashboard.display_success(f"Report saved to: {filename}")

        else:
            error_msg = data.get("error", "Failed to extract data") if data else "No data returned"
            dashboard.display_error(error_msg)
            sys.exit(1)
    
    except KeyboardInterrupt:
        dashboard.display_error("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        dashboard.display_error(f"Unexpected error: {str(e)}")
        logger.exception("Unexpected error in extract command")
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol to monitor')
@click.option('--duration', '-d', default=60, help='Monitoring duration in minutes')
@click.option('--interval', '-i', default=300, help='Check interval in seconds')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def monitor(symbol: str, duration: int, interval: int, headless: bool):
    """Monitor stock price in real-time"""
    
    dashboard = FinanceDashboard()
    
    try:
        dashboard.console.print(f"[bold blue]Starting to monitor {symbol} for {duration} minutes[/bold blue]")
        dashboard.console.print(f"Check interval: {interval} seconds\n")
        
        with YahooFinanceAgent(headless=headless, use_ai_analysis=False) as agent:
            monitoring_data = agent.monitor_stock(symbol, duration, interval)
        
        # Display monitoring results
        dashboard.display_monitoring_results(monitoring_data)
        
        if monitoring_data:
            dashboard.display_success(f"Monitoring completed. Collected {len(monitoring_data)} data points.")
        else:
            dashboard.display_error("No monitoring data collected")
    
    except KeyboardInterrupt:
        dashboard.display_error("Monitoring stopped by user")
    except Exception as e:
        dashboard.display_error(f"Monitoring failed: {str(e)}")
        logger.exception("Error in monitor command")
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol')
@click.option('--headless/--no-headless', default=True, help='Run browser in headless mode')
def price(symbol: str, headless: bool):
    """Get current stock price quickly"""
    
    dashboard = FinanceDashboard()
    
    try:
        dashboard.console.print(f"⏳ Getting price for {symbol}...")

        # Use the working HTTP-based scraping method
        from basic_demo import scrape_yahoo_finance_basic

        data = scrape_yahoo_finance_basic(symbol.upper())

        if data and "error" not in data:
            # Create simple price display
            from rich.table import Table
            table = Table(title=f"{symbol.upper()} Current Price")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            def format_currency(value):
                return f"${value:,.2f}" if value is not None else "N/A"

            table.add_row("Current Price", format_currency(data['current_price']))

            if data['price_change'] is not None:
                change_color = "green" if data['price_change'] >= 0 else "red"
                table.add_row("Change", f"[{change_color}]{format_currency(data['price_change'])}[/{change_color}]")

            if data['price_change_percent'] is not None:
                change_color = "green" if data['price_change_percent'] >= 0 else "red"
                table.add_row("Change %", f"[{change_color}]{data['price_change_percent']:+.2f}%[/{change_color}]")

            dashboard.console.print(table)

        else:
            error_msg = data.get("error", "Failed to get price") if data else "No data returned"
            dashboard.display_error(error_msg)
            sys.exit(1)
    
    except Exception as e:
        dashboard.display_error(f"Failed to get price: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol')
@click.option('--period', '-p', default='1y', help='Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
@click.option('--interval', '-i', default='1d', help='Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)')
def historical(symbol: str, period: str, interval: str):
    """Get historical data and technical analysis (disabled for Python 3.7)"""

    dashboard = FinanceDashboard()

    try:
        dashboard.display_error("Historical data analysis is not available in Python 3.7 compatibility mode.")
        dashboard.console.print("\n[yellow]To use historical data features:[/yellow]")
        dashboard.console.print("1. Upgrade to Python 3.8 or higher")
        dashboard.console.print("2. Run: pip install -r requirements.txt")
        dashboard.console.print("3. Use the full version with DataProcessor")
        dashboard.console.print("\n[cyan]Alternative: Use basic_demo.py for current price data[/cyan]")

    
    except Exception as e:
        dashboard.display_error(f"Historical analysis failed: {str(e)}")
        logger.exception("Error in historical command")
        sys.exit(1)

@cli.command()
def config():
    """Show current configuration"""
    
    dashboard = FinanceDashboard()
    
    from rich.table import Table
    table = Table(title="Yahoo Finance Agent Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Display key settings
    table.add_row("OpenAI API Key", "✓ Set" if settings.openai_api_key else "✗ Not Set")
    table.add_row("OpenAI Model", settings.openai_model)
    table.add_row("Browser Headless", str(settings.browser_headless))
    table.add_row("Browser Timeout", f"{settings.browser_timeout}s")
    table.add_row("Max Retries", str(settings.max_retries))
    table.add_row("Log Level", settings.log_level)
    table.add_row("Data Directory", settings.data_dir)
    
    dashboard.console.print(table)

if __name__ == '__main__':
    cli()
