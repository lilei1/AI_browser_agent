"""
User interface and dashboard for Yahoo Finance Agent
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
# import plotly.graph_objects as go  # Disabled for Python 3.7 compatibility
# import plotly.express as px
# from plotly.subplots import make_subplots
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from ..data.models import StockData, AnalysisResult
from ..utils.helpers import format_currency, format_percentage, format_volume

class FinanceDashboard:
    """
    Rich console-based dashboard for displaying financial data
    """
    
    def __init__(self):
        """Initialize the dashboard"""
        self.console = Console()
        logger.info("Finance dashboard initialized")
    
    def display_stock_summary(self, stock_data: StockData, analysis: Optional[AnalysisResult] = None):
        """
        Display comprehensive stock summary
        
        Args:
            stock_data: Stock data to display
            analysis: Optional AI analysis results
        """
        self.console.clear()
        
        # Create main layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        header_text = Text(f"{stock_data.company_info.company_name} ({stock_data.symbol})", 
                          style="bold blue", justify="center")
        layout["header"].update(Panel(header_text, title="Yahoo Finance AI Agent"))
        
        # Main content
        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1)
        )
        
        # Left side - Price and metrics
        layout["left"].split_column(
            Layout(name="price", size=8),
            Layout(name="metrics", ratio=1)
        )
        
        # Price information
        price_table = self._create_price_table(stock_data.price_info)
        layout["price"].update(Panel(price_table, title="Price Information"))
        
        # Financial metrics
        metrics_table = self._create_metrics_table(stock_data.trading_metrics, stock_data.financial_ratios)
        layout["metrics"].update(Panel(metrics_table, title="Financial Metrics"))
        
        # Right side - Analysis
        if analysis:
            analysis_panel = self._create_analysis_panel(analysis)
            layout["right"].update(Panel(analysis_panel, title="AI Analysis"))
        else:
            layout["right"].update(Panel("No AI analysis available", title="AI Analysis"))
        
        # Footer
        footer_text = f"Last updated: {stock_data.last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
        layout["footer"].update(Panel(footer_text, style="dim"))
        
        self.console.print(layout)
    
    def _create_price_table(self, price_info) -> Table:
        """Create price information table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green", width=15)
        table.add_column("Change", style="yellow", width=15)
        
        # Current price
        change_color = "green" if (price_info.price_change or 0) >= 0 else "red"
        change_text = f"{format_currency(price_info.price_change)} ({format_percentage(price_info.price_change_percent)})"
        
        table.add_row(
            "Current Price",
            format_currency(price_info.current_price),
            f"[{change_color}]{change_text}[/{change_color}]"
        )
        
        table.add_row("Previous Close", format_currency(price_info.previous_close), "")
        table.add_row("Open", format_currency(price_info.open_price), "")
        
        if price_info.day_low and price_info.day_high:
            day_range = f"{format_currency(price_info.day_low)} - {format_currency(price_info.day_high)}"
            table.add_row("Day Range", day_range, "")
        
        if price_info.week_52_low and price_info.week_52_high:
            week_range = f"{format_currency(price_info.week_52_low)} - {format_currency(price_info.week_52_high)}"
            table.add_row("52-Week Range", week_range, "")
        
        return table
    
    def _create_metrics_table(self, trading_metrics, financial_ratios) -> Table:
        """Create financial metrics table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="white", width=20)
        
        # Trading metrics
        if trading_metrics.volume:
            table.add_row("Volume", format_volume(trading_metrics.volume))
        
        if trading_metrics.avg_volume:
            table.add_row("Avg Volume", format_volume(trading_metrics.avg_volume))
        
        if trading_metrics.market_cap:
            table.add_row("Market Cap", trading_metrics.market_cap)
        
        # Financial ratios
        if financial_ratios.pe_ratio:
            table.add_row("P/E Ratio", f"{financial_ratios.pe_ratio:.2f}")
        
        if financial_ratios.eps:
            table.add_row("EPS", format_currency(financial_ratios.eps))
        
        if financial_ratios.beta:
            table.add_row("Beta", f"{financial_ratios.beta:.2f}")
        
        if financial_ratios.dividend_yield:
            table.add_row("Dividend Yield", format_percentage(financial_ratios.dividend_yield))
        
        return table
    
    def _create_analysis_panel(self, analysis: AnalysisResult) -> str:
        """Create AI analysis panel content"""
        content = []
        
        if analysis.insights:
            content.append("[bold]Key Insights:[/bold]")
            for i, insight in enumerate(analysis.insights[:5], 1):
                content.append(f"{i}. {insight}")
            content.append("")
        
        if analysis.recommendations:
            content.append("[bold]Recommendations:[/bold]")
            for i, rec in enumerate(analysis.recommendations[:3], 1):
                content.append(f"{i}. {rec}")
            content.append("")
        
        if analysis.confidence_score:
            confidence_color = "green" if analysis.confidence_score > 0.7 else "yellow" if analysis.confidence_score > 0.5 else "red"
            content.append(f"[bold]Confidence:[/bold] [{confidence_color}]{analysis.confidence_score:.1%}[/{confidence_color}]")
        
        return "\n".join(content)
    
    def display_monitoring_results(self, monitoring_data: List[Dict[str, Any]]):
        """Display stock monitoring results"""
        if not monitoring_data:
            self.console.print("[red]No monitoring data available[/red]")
            return
        
        self.console.print("\n[bold blue]Stock Monitoring Results[/bold blue]")
        
        # Create monitoring table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Time", style="cyan", width=20)
        table.add_column("Price", style="green", width=12)
        table.add_column("Change", style="yellow", width=15)
        table.add_column("Status", style="white", width=10)
        
        for data_point in monitoring_data[-10:]:  # Show last 10 points
            if data_point.get("success"):
                timestamp = data_point.get("monitoring_timestamp", datetime.now())
                price = data_point.get("current_price")
                change = data_point.get("price_change")
                change_percent = data_point.get("price_change_percent")
                
                change_color = "green" if (change or 0) >= 0 else "red"
                change_text = f"{format_currency(change)} ({format_percentage(change_percent)})"
                
                table.add_row(
                    timestamp.strftime("%H:%M:%S"),
                    format_currency(price),
                    f"[{change_color}]{change_text}[/{change_color}]",
                    "[green]✓[/green]"
                )
            else:
                table.add_row(
                    data_point.get("monitoring_timestamp", datetime.now()).strftime("%H:%M:%S"),
                    "N/A",
                    "N/A",
                    "[red]✗[/red]"
                )
        
        self.console.print(table)
    
    def show_progress(self, description: str = "Processing..."):
        """Show progress spinner"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(description, total=None)
            return progress, task
    
    def display_error(self, error_message: str):
        """Display error message"""
        error_panel = Panel(
            f"[red]Error: {error_message}[/red]",
            title="Error",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def display_success(self, message: str):
        """Display success message"""
        success_panel = Panel(
            f"[green]{message}[/green]",
            title="Success",
            border_style="green"
        )
        self.console.print(success_panel)

class ReportGenerator:
    """
    Generate various types of reports from financial data
    """
    
    def __init__(self):
        """Initialize report generator"""
        logger.info("Report generator initialized")
    
    def generate_stock_report(self, stock_data: StockData, analysis: Optional[AnalysisResult] = None) -> str:
        """
        Generate comprehensive stock report
        
        Args:
            stock_data: Stock data
            analysis: Optional AI analysis
            
        Returns:
            Formatted report string
        """
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append(f"STOCK ANALYSIS REPORT: {stock_data.company_info.company_name} ({stock_data.symbol})")
        report_lines.append("=" * 60)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Price Information
        report_lines.append("PRICE INFORMATION")
        report_lines.append("-" * 20)
        price_info = stock_data.price_info
        report_lines.append(f"Current Price: {format_currency(price_info.current_price)}")
        report_lines.append(f"Price Change: {format_currency(price_info.price_change)} ({format_percentage(price_info.price_change_percent)})")
        report_lines.append(f"Previous Close: {format_currency(price_info.previous_close)}")
        report_lines.append(f"Open: {format_currency(price_info.open_price)}")
        
        if price_info.day_low and price_info.day_high:
            report_lines.append(f"Day Range: {format_currency(price_info.day_low)} - {format_currency(price_info.day_high)}")
        
        if price_info.week_52_low and price_info.week_52_high:
            report_lines.append(f"52-Week Range: {format_currency(price_info.week_52_low)} - {format_currency(price_info.week_52_high)}")
        
        report_lines.append("")
        
        # Trading Metrics
        report_lines.append("TRADING METRICS")
        report_lines.append("-" * 15)
        trading = stock_data.trading_metrics
        
        if trading.volume:
            report_lines.append(f"Volume: {format_volume(trading.volume)}")
        
        if trading.avg_volume:
            report_lines.append(f"Average Volume: {format_volume(trading.avg_volume)}")
        
        if trading.market_cap:
            report_lines.append(f"Market Cap: {trading.market_cap}")
        
        report_lines.append("")
        
        # Financial Ratios
        report_lines.append("FINANCIAL RATIOS")
        report_lines.append("-" * 17)
        ratios = stock_data.financial_ratios
        
        if ratios.pe_ratio:
            report_lines.append(f"P/E Ratio: {ratios.pe_ratio:.2f}")
        
        if ratios.eps:
            report_lines.append(f"EPS: {format_currency(ratios.eps)}")
        
        if ratios.beta:
            report_lines.append(f"Beta: {ratios.beta:.2f}")
        
        if ratios.dividend_yield:
            report_lines.append(f"Dividend Yield: {format_percentage(ratios.dividend_yield)}")
        
        # AI Analysis
        if analysis:
            report_lines.append("")
            report_lines.append("AI ANALYSIS")
            report_lines.append("-" * 11)
            
            if analysis.insights:
                report_lines.append("Key Insights:")
                for i, insight in enumerate(analysis.insights, 1):
                    report_lines.append(f"  {i}. {insight}")
                report_lines.append("")
            
            if analysis.recommendations:
                report_lines.append("Recommendations:")
                for i, rec in enumerate(analysis.recommendations, 1):
                    report_lines.append(f"  {i}. {rec}")
                report_lines.append("")
            
            if analysis.confidence_score:
                report_lines.append(f"Analysis Confidence: {analysis.confidence_score:.1%}")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def save_report_to_file(self, report_content: str, filename: str = None) -> str:
        """
        Save report to file
        
        Args:
            report_content: Report content to save
            filename: Optional filename (auto-generated if not provided)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_report_{timestamp}.txt"
        
        filepath = f"data/{filename}"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.success(f"Report saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise
    
    def generate_json_report(self, stock_data: StockData, analysis: Optional[AnalysisResult] = None) -> str:
        """
        Generate JSON format report
        
        Args:
            stock_data: Stock data
            analysis: Optional AI analysis
            
        Returns:
            JSON formatted report
        """
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "symbol": stock_data.symbol,
                "company_name": stock_data.company_info.company_name
            },
            "stock_data": stock_data.dict(),
            "analysis": analysis.dict() if analysis else None
        }
        
        return json.dumps(report_data, indent=2, default=str)
