#!/usr/bin/env python3
"""
Yahoo Finance AI Browser Agent - Interactive Demo
"""
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.ui import FinanceDashboard, ReportGenerator
from src.yahoo_finance_agent.data import DataProcessor
from src.yahoo_finance_agent.utils import health_monitor, error_tracker
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

def main():
    """Interactive demo of Yahoo Finance AI Browser Agent"""
    console = Console()
    dashboard = FinanceDashboard()
    
    # Welcome message
    welcome_text = Text("Yahoo Finance AI Browser Agent", style="bold blue", justify="center")
    welcome_panel = Panel(
        welcome_text + "\n\n" + 
        "🚀 Comprehensive AI-powered financial data extraction and analysis\n" +
        "📊 Real-time stock monitoring with intelligent insights\n" +
        "🤖 OpenAI-powered analysis and recommendations\n" +
        "📈 Technical analysis with 20+ indicators\n\n" +
        "Demo will showcase key features using Apple (AAPL) stock data",
        title="Welcome",
        border_style="blue"
    )
    console.print(welcome_panel)
    
    try:
        # Demo 1: Basic Stock Data Extraction
        console.print("\n[bold cyan]Demo 1: Basic Stock Data Extraction[/bold cyan]")
        console.print("Extracting comprehensive AAPL stock data with AI analysis...")
        
        with dashboard.show_progress("Extracting stock data..."):
            with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
                result = agent.extract_stock_data("AAPL", include_analysis=True)
        
        if result["success"]:
            from src.yahoo_finance_agent.data.models import StockData, AnalysisResult
            
            stock_data = StockData(**result["stock_data"])
            analysis = AnalysisResult(**result["analysis"]) if result.get("analysis") else None
            
            # Display results
            dashboard.display_stock_summary(stock_data, analysis)
            
            console.print(f"\n✅ Successfully extracted data in {result['extraction_time']:.2f}s")
            
            # Demo 2: Generate Report
            console.print("\n[bold cyan]Demo 2: Report Generation[/bold cyan]")
            report_generator = ReportGenerator()
            
            # Generate and save text report
            text_report = report_generator.generate_stock_report(stock_data, analysis)
            report_file = report_generator.save_report_to_file(text_report, "demo_aapl_report.txt")
            
            console.print(f"📄 Text report saved: {report_file}")
            
            # Generate JSON report
            json_report = report_generator.generate_json_report(stock_data, analysis)
            json_file = report_generator.save_report_to_file(json_report, "demo_aapl_report.json")
            
            console.print(f"📋 JSON report saved: {json_file}")
            
        else:
            dashboard.display_error(f"Failed to extract data: {result['error']}")
            return
        
        # Demo 3: Historical Data and Technical Analysis
        console.print("\n[bold cyan]Demo 3: Historical Data & Technical Analysis[/bold cyan]")
        
        processor = DataProcessor()
        
        with dashboard.show_progress("Fetching historical data..."):
            historical_data = processor.get_historical_data("AAPL", period="6mo", interval="1d")
        
        if historical_data:
            console.print(f"📈 Retrieved {len(historical_data.data_points)} historical data points")
            
            # Calculate technical indicators
            with dashboard.show_progress("Calculating technical indicators..."):
                indicators = processor.calculate_technical_indicators(historical_data)
                patterns = processor.analyze_price_patterns(historical_data)
            
            # Display technical analysis
            from rich.table import Table
            
            tech_table = Table(title="Technical Analysis Summary")
            tech_table.add_column("Indicator", style="cyan")
            tech_table.add_column("Value", style="green")
            tech_table.add_column("Signal", style="yellow")
            
            if indicators.get("sma_20"):
                signal = "Bullish" if stock_data.price_info.current_price > indicators["sma_20"] else "Bearish"
                tech_table.add_row("SMA 20", f"${indicators['sma_20']:.2f}", signal)
            
            if indicators.get("rsi"):
                rsi_signal = "Overbought" if indicators["rsi"] > 70 else "Oversold" if indicators["rsi"] < 30 else "Neutral"
                tech_table.add_row("RSI", f"{indicators['rsi']:.1f}", rsi_signal)
            
            if indicators.get("macd"):
                macd_signal = "Bullish" if indicators["macd"] > indicators.get("macd_signal", 0) else "Bearish"
                tech_table.add_row("MACD", f"{indicators['macd']:.4f}", macd_signal)
            
            if patterns and not patterns.get("error"):
                trend = patterns.get("trend", {})
                trend_strength = "Strong" if trend.get("strength", 0) > 0.7 else "Moderate" if trend.get("strength", 0) > 0.4 else "Weak"
                tech_table.add_row("Trend", trend.get("direction", "Unknown").title(), trend_strength)
            
            console.print(tech_table)
        
        # Demo 4: Real-time Price Check
        console.print("\n[bold cyan]Demo 4: Real-time Price Check[/bold cyan]")
        
        with dashboard.show_progress("Getting real-time price..."):
            with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
                price_result = agent.get_real_time_price("AAPL")
        
        if price_result["success"]:
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
        
        # Demo 5: System Health and Performance
        console.print("\n[bold cyan]Demo 5: System Health & Performance[/bold cyan]")
        
        # Get health status
        health_status = health_monitor.get_health_status()
        error_summary = error_tracker.get_error_summary(hours=1)
        
        health_table = Table(title="System Health Status")
        health_table.add_column("Metric", style="cyan")
        health_table.add_column("Value", style="green")
        
        status_color = "green" if health_status["status"] == "healthy" else "yellow" if health_status["status"] == "degraded" else "red"
        health_table.add_row("Status", f"[{status_color}]{health_status['status'].upper()}[/{status_color}]")
        health_table.add_row("Success Rate", f"{health_status['success_rate']:.1%}")
        health_table.add_row("Total Requests", str(health_status['metrics']['requests_total']))
        health_table.add_row("Avg Response Time", f"{health_status['metrics']['average_response_time']:.2f}s")
        health_table.add_row("Uptime", f"{health_status['uptime_seconds']:.0f}s")
        health_table.add_row("Errors (1h)", str(error_summary['total_errors']))
        
        console.print(health_table)
        
        # Demo Summary
        console.print("\n[bold green]🎉 Demo Completed Successfully![/bold green]")
        
        summary_panel = Panel(
            "✅ Stock data extraction with AI analysis\n" +
            "✅ Report generation (text and JSON formats)\n" +
            "✅ Historical data and technical analysis\n" +
            "✅ Real-time price monitoring\n" +
            "✅ System health and performance monitoring\n\n" +
            "📁 Generated files:\n" +
            "  • demo_aapl_report.txt\n" +
            "  • demo_aapl_report.json\n" +
            "  • yahoo_finance_agent.log\n\n" +
            "🚀 Ready for production use!",
            title="Demo Summary",
            border_style="green"
        )
        console.print(summary_panel)
        
        # Usage instructions
        usage_panel = Panel(
            "Command Line Usage:\n" +
            "  python main.py extract --symbol AAPL --save-report\n" +
            "  python main.py monitor --symbol AAPL --duration 30\n" +
            "  python main.py price --symbol AAPL\n" +
            "  python main.py historical --symbol AAPL --period 1y\n\n" +
            "Python API Usage:\n" +
            "  from src.yahoo_finance_agent import YahooFinanceAgent\n" +
            "  with YahooFinanceAgent() as agent:\n" +
            "      result = agent.extract_stock_data('AAPL')\n\n" +
            "Documentation:\n" +
            "  • README.md - Complete setup and usage guide\n" +
            "  • docs/API_REFERENCE.md - Full API documentation\n" +
            "  • examples/ - Usage examples and patterns",
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
