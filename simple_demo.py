#!/usr/bin/env python3
"""
Simple Yahoo Finance AI Browser Agent Demo (Python 3.7 compatible)
"""
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.ui import FinanceDashboard, ReportGenerator
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def main():
    """Simple demo of Yahoo Finance AI Browser Agent"""
    console = Console()
    dashboard = FinanceDashboard()
    
    # Welcome message
    welcome_text = Text("Yahoo Finance AI Browser Agent", style="bold blue", justify="center")
    welcome_panel = Panel(
        welcome_text + "\n\n" + 
        "🚀 AI-powered financial data extraction and analysis\n" +
        "📊 Real-time stock monitoring with intelligent insights\n" +
        "🤖 OpenAI-powered analysis and recommendations\n\n" +
        "Simple demo showcasing core features using Apple (AAPL) stock data",
        title="Welcome",
        border_style="blue"
    )
    console.print(welcome_panel)
    
    try:
        # Demo 1: Basic Stock Data Extraction
        console.print("\n[bold cyan]Demo 1: Basic Stock Data Extraction[/bold cyan]")
        console.print("Extracting comprehensive AAPL stock data...")
        
        console.print("⏳ Extracting stock data...")
        with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
            result = agent.extract_stock_data("AAPL", include_analysis=False)
        
        if result["success"]:
            from src.yahoo_finance_agent.data.models import StockData
            
            stock_data = StockData(**result["stock_data"])
            
            # Display results
            dashboard.display_stock_summary(stock_data, None)
            
            console.print(f"\n✅ Successfully extracted data in {result['extraction_time']:.2f}s")
            
            # Demo 2: Generate Report
            console.print("\n[bold cyan]Demo 2: Report Generation[/bold cyan]")
            report_generator = ReportGenerator()
            
            # Generate and save text report
            text_report = report_generator.generate_stock_report(stock_data, None)
            report_file = report_generator.save_report_to_file(text_report, "simple_demo_aapl_report.txt")
            
            console.print(f"📄 Text report saved: {report_file}")
            
        else:
            dashboard.display_error(f"Failed to extract data: {result['error']}")
            return
        
        # Demo 3: Real-time Price Check
        console.print("\n[bold cyan]Demo 3: Real-time Price Check[/bold cyan]")
        
        console.print("⏳ Getting real-time price...")
        with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
            price_result = agent.get_real_time_price("AAPL")
        
        if price_result["success"]:
            from rich.table import Table
            
            price_table = Table(title="Real-time AAPL Price")
            price_table.add_column("Metric", style="cyan")
            price_table.add_column("Value", style="green")
            
            price_table.add_row("Current Price", f"${price_result['current_price']:.2f}")
            
            change_color = "green" if price_result['price_change'] >= 0 else "red"
            change_text = f"${price_result['price_change']:.2f} ({price_result['price_change_percent']:+.2f}%)"
            price_table.add_row("Change", f"[{change_color}]{change_text}[/{change_color}]")
            
            market_status = "🟢 Open" if price_result['market_hours'] else "🔴 Closed"
            price_table.add_row("Market Status", market_status)
            
            console.print(price_table)
        
        # Demo Summary
        console.print("\n[bold green]🎉 Simple Demo Completed Successfully![/bold green]")
        
        summary_panel = Panel(
            "✅ Stock data extraction\n" +
            "✅ Report generation (text format)\n" +
            "✅ Real-time price monitoring\n\n" +
            "📁 Generated files:\n" +
            "  • simple_demo_aapl_report.txt\n" +
            "  • yahoo_finance_agent.log\n\n" +
            "🚀 Core functionality working!",
            title="Demo Summary",
            border_style="green"
        )
        console.print(summary_panel)
        
        # Usage instructions
        usage_panel = Panel(
            "Command Line Usage:\n" +
            "  python3 main.py extract --symbol AAPL --save-report\n" +
            "  python3 main.py price --symbol AAPL\n\n" +
            "Python API Usage:\n" +
            "  from src.yahoo_finance_agent import YahooFinanceAgent\n" +
            "  with YahooFinanceAgent() as agent:\n" +
            "      result = agent.extract_stock_data('AAPL')\n\n" +
            "Note: This simple demo runs without AI analysis and\n" +
            "historical data features for Python 3.7 compatibility.\n" +
            "For full features, upgrade to Python 3.8+",
            title="Next Steps",
            border_style="blue"
        )
        console.print(usage_panel)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed with error: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    console.print("\n[dim]Thank you for trying Yahoo Finance AI Browser Agent![/dim]")

if __name__ == "__main__":
    main()
