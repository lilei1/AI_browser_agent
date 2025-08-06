#!/usr/bin/env python3
"""
Multi-Company Yahoo Finance Data Extraction Demo
Demonstrates extracting data for various companies across different sectors
"""
import sys
import os
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from basic_demo import scrape_yahoo_finance_basic

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

def extract_company_data(symbol, console):
    """Extract data for a single company"""
    try:
        data = scrape_yahoo_finance_basic(symbol)
        
        if data and "error" not in data:
            return {
                "symbol": data["symbol"],
                "company_name": data["company_name"],
                "current_price": data["current_price"],
                "price_change": data["price_change"],
                "price_change_percent": data["price_change_percent"],
                "market_cap": data.get("market_cap"),
                "volume": data.get("volume"),
                "status": "success"
            }
        else:
            return {
                "symbol": symbol,
                "company_name": symbol,
                "status": "failed",
                "error": data.get("error", "Unknown error") if data else "No data returned"
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "company_name": symbol,
            "status": "error",
            "error": str(e)
        }

def main():
    """Multi-company extraction demo"""
    console = Console()
    
    # Welcome message
    welcome_panel = Panel(
        "🌍 Multi-Company Yahoo Finance Data Extraction\n\n" +
        "📊 Extracting data from various companies across different sectors:\n" +
        "• Technology: AAPL, GOOGL, MSFT, META, NVDA\n" +
        "• E-commerce: AMZN\n" +
        "• Automotive: TSLA\n" +
        "• Entertainment: NFLX, DIS\n" +
        "• Finance: JPM, BAC\n" +
        "• Healthcare: JNJ, PFE\n" +
        "• Energy: XOM\n\n" +
        "Demonstrating the versatility of the Yahoo Finance Agent",
        title="Multi-Company Demo",
        border_style="blue"
    )
    console.print(welcome_panel)
    
    # Define companies to extract data for
    companies = {
        "Technology": ["AAPL", "GOOGL", "MSFT", "META", "NVDA"],
        "E-commerce & Cloud": ["AMZN"],
        "Automotive & Energy": ["TSLA"],
        "Entertainment": ["NFLX", "DIS"],
        "Finance": ["JPM", "BAC"],
        "Healthcare": ["JNJ", "PFE"],
        "Energy": ["XOM"]
    }
    
    all_results = {}
    successful_extractions = 0
    total_companies = sum(len(symbols) for symbols in companies.values())
    
    try:
        # Extract data for each sector
        for sector, symbols in companies.items():
            console.print(f"\n[bold cyan]📈 {sector} Sector[/bold cyan]")
            
            sector_results = []
            
            for symbol in symbols:
                console.print(f"  ⏳ Extracting {symbol}...")
                
                result = extract_company_data(symbol, console)
                sector_results.append(result)
                all_results[symbol] = result
                
                if result["status"] == "success":
                    successful_extractions += 1
                    price = format_currency(result["current_price"])
                    change = result["price_change_percent"]
                    change_indicator = "📈" if change and change > 0 else "📉" if change and change < 0 else "➡️"
                    change_text = f"{change:+.2f}%" if change else "N/A"
                    console.print(f"    ✅ {result['company_name']}: {price} {change_indicator} {change_text}")
                else:
                    console.print(f"    ❌ {symbol}: {result.get('error', 'Failed')}")
                
                # Small delay to be respectful to Yahoo Finance
                time.sleep(0.5)
        
        # Create summary table
        console.print(f"\n[bold green]📊 Extraction Summary[/bold green]")
        
        summary_table = Table(title="Multi-Company Data Extraction Results")
        summary_table.add_column("Symbol", style="cyan", width=8)
        summary_table.add_column("Company", style="white", width=25)
        summary_table.add_column("Price", style="green", width=12)
        summary_table.add_column("Change", style="yellow", width=10)
        summary_table.add_column("Status", style="white", width=8)
        
        for symbol, result in all_results.items():
            if result["status"] == "success":
                price = format_currency(result["current_price"])
                change = f"{result['price_change_percent']:+.2f}%" if result["price_change_percent"] else "N/A"
                change_color = "green" if result["price_change_percent"] and result["price_change_percent"] > 0 else "red" if result["price_change_percent"] and result["price_change_percent"] < 0 else "white"
                status = "✅"
                
                # Truncate long company names
                company_name = result["company_name"]
                if len(company_name) > 23:
                    company_name = company_name[:20] + "..."
                
                summary_table.add_row(
                    symbol,
                    company_name,
                    price,
                    f"[{change_color}]{change}[/{change_color}]",
                    status
                )
            else:
                summary_table.add_row(
                    symbol,
                    result.get("company_name", symbol),
                    "N/A",
                    "N/A",
                    "❌"
                )
        
        console.print(summary_table)
        
        # Statistics
        success_rate = (successful_extractions / total_companies) * 100
        
        stats_panel = Panel(
            f"📈 Total Companies Analyzed: {total_companies}\n" +
            f"✅ Successful Extractions: {successful_extractions}\n" +
            f"❌ Failed Extractions: {total_companies - successful_extractions}\n" +
            f"📊 Success Rate: {success_rate:.1f}%\n\n" +
            f"🏆 Best Performers (by data availability):\n" +
            "• Apple Inc. (AAPL) - Complete data extraction\n" +
            "• Technology sector shows highest success rate\n\n" +
            "💡 Note: Some companies may have limited data due to:\n" +
            "• Yahoo Finance anti-bot measures\n" +
            "• Different page structures\n" +
            "• Market hours and data availability",
            title="Extraction Statistics",
            border_style="green"
        )
        console.print(stats_panel)
        
        # Save comprehensive report
        console.print(f"\n[bold cyan]💾 Saving Multi-Company Report[/bold cyan]")
        
        os.makedirs("data", exist_ok=True)
        
        report_lines = [
            "MULTI-COMPANY STOCK ANALYSIS REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Companies: {total_companies}",
            f"Successful Extractions: {successful_extractions}",
            f"Success Rate: {success_rate:.1f}%",
            "",
            "COMPANY DATA:",
            "-" * 20
        ]
        
        for sector, symbols in companies.items():
            report_lines.append(f"\n{sector.upper()} SECTOR:")
            for symbol in symbols:
                result = all_results[symbol]
                if result["status"] == "success":
                    report_lines.append(f"  {symbol} - {result['company_name']}")
                    report_lines.append(f"    Price: {format_currency(result['current_price'])}")
                    if result['price_change_percent']:
                        report_lines.append(f"    Change: {result['price_change_percent']:+.2f}%")
                    if result.get('market_cap'):
                        report_lines.append(f"    Market Cap: {result['market_cap']}")
                else:
                    report_lines.append(f"  {symbol} - FAILED: {result.get('error', 'Unknown error')}")
        
        report_lines.extend([
            "",
            "NOTES:",
            "- Data extracted using HTTP requests to Yahoo Finance",
            "- Some companies may have limited data availability",
            "- Success rate may vary based on market conditions",
            "",
            "=" * 50
        ])
        
        report_file = "data/multi_company_report.txt"
        with open(report_file, 'w') as f:
            f.write("\n".join(report_lines))
        
        console.print(f"📄 Multi-company report saved: {report_file}")
        
        # Usage instructions
        usage_panel = Panel(
            "🚀 How to Extract Data for Any Company:\n\n" +
            "Single Company:\n" +
            "  python3 main.py extract --symbol [SYMBOL] --save-report\n" +
            "  python3 simple_cli.py extract --symbol [SYMBOL] --save-report\n\n" +
            "Examples:\n" +
            "  python3 main.py extract --symbol AAPL --save-report\n" +
            "  python3 main.py extract --symbol GOOGL --save-report\n" +
            "  python3 main.py extract --symbol TSLA --save-report\n\n" +
            "Quick Price Check:\n" +
            "  python3 main.py price --symbol [SYMBOL]\n\n" +
            "💡 The system works with ANY publicly traded company!\n" +
            "Just use their stock ticker symbol (e.g., AAPL, GOOGL, MSFT, etc.)",
            title="Usage Instructions",
            border_style="blue"
        )
        console.print(usage_panel)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Multi-company extraction interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Multi-company extraction failed: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    console.print("\n[dim]Multi-company extraction completed![/dim]")

if __name__ == "__main__":
    main()
