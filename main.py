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
from src.yahoo_finance_agent.data import DataProcessor
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
        with dashboard.show_progress(f"Extracting data for {symbol}..."):
            with YahooFinanceAgent(headless=headless, use_ai_analysis=analysis) as agent:
                result = agent.extract_stock_data(symbol, include_analysis=analysis)
        
        if result["success"]:
            stock_data = result["stock_data"]
            analysis_result = result.get("analysis")
            
            # Display results
            dashboard.display_stock_summary(stock_data, analysis_result)
            
            # Save report if requested
            if save_report:
                if output_format == 'json':
                    report_content = report_generator.generate_json_report(stock_data, analysis_result)
                    filename = f"{symbol}_report.json"
                else:
                    report_content = report_generator.generate_stock_report(stock_data, analysis_result)
                    filename = f"{symbol}_report.txt"
                
                filepath = report_generator.save_report_to_file(report_content, filename)
                dashboard.display_success(f"Report saved to: {filepath}")
        
        else:
            dashboard.display_error(result["error"])
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
        with dashboard.show_progress(f"Getting price for {symbol}..."):
            with YahooFinanceAgent(headless=headless, use_ai_analysis=False) as agent:
                result = agent.get_real_time_price(symbol)
        
        if result["success"]:
            price_info = result
            
            # Create simple price display
            from rich.table import Table
            table = Table(title=f"{symbol} Current Price")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Current Price", f"${price_info['current_price']:.2f}")
            table.add_row("Change", f"${price_info['price_change']:.2f}")
            table.add_row("Change %", f"{price_info['price_change_percent']:.2f}%")
            table.add_row("Market Status", "Open" if price_info['market_hours'] else "Closed")
            
            dashboard.console.print(table)
        
        else:
            dashboard.display_error(result["error"])
            sys.exit(1)
    
    except Exception as e:
        dashboard.display_error(f"Failed to get price: {str(e)}")
        sys.exit(1)

@cli.command()
@click.option('--symbol', '-s', default='AAPL', help='Stock symbol')
@click.option('--period', '-p', default='1y', help='Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)')
@click.option('--interval', '-i', default='1d', help='Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)')
def historical(symbol: str, period: str, interval: str):
    """Get historical data and technical analysis"""
    
    dashboard = FinanceDashboard()
    processor = DataProcessor()
    
    try:
        with dashboard.show_progress(f"Fetching historical data for {symbol}..."):
            historical_data = processor.get_historical_data(symbol, period, interval)
        
        if historical_data:
            # Calculate technical indicators
            indicators = processor.calculate_technical_indicators(historical_data)
            patterns = processor.analyze_price_patterns(historical_data)
            
            # Display results
            from rich.table import Table
            
            # Technical indicators table
            indicators_table = Table(title=f"{symbol} Technical Indicators")
            indicators_table.add_column("Indicator", style="cyan")
            indicators_table.add_column("Value", style="green")
            
            for key, value in indicators.items():
                if value is not None:
                    if isinstance(value, float):
                        indicators_table.add_row(key.replace('_', ' ').title(), f"{value:.2f}")
                    else:
                        indicators_table.add_row(key.replace('_', ' ').title(), str(value))
            
            dashboard.console.print(indicators_table)
            
            # Pattern analysis
            if patterns and not patterns.get('error'):
                dashboard.console.print(f"\n[bold]Pattern Analysis:[/bold]")
                
                trend = patterns.get('trend', {})
                if trend:
                    dashboard.console.print(f"Trend: {trend.get('direction', 'unknown').title()} (Strength: {trend.get('strength', 0):.2f})")
                
                chart_patterns = patterns.get('chart_patterns', [])
                if chart_patterns:
                    dashboard.console.print(f"Chart Patterns: {', '.join(chart_patterns)}")
                
                candlestick_patterns = patterns.get('candlestick_patterns', [])
                if candlestick_patterns:
                    dashboard.console.print(f"Candlestick Patterns: {', '.join(candlestick_patterns)}")
            
            dashboard.display_success(f"Historical analysis completed for {symbol}")
        
        else:
            dashboard.display_error(f"Failed to fetch historical data for {symbol}")
    
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
