#!/usr/bin/env python3
"""
Basic usage examples for Yahoo Finance AI Browser Agent
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.ui import FinanceDashboard, ReportGenerator
from src.yahoo_finance_agent.data import DataProcessor

def example_basic_extraction():
    """Example: Basic stock data extraction"""
    print("=== Basic Stock Data Extraction ===")
    
    # Create agent with headless browser and AI analysis
    with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
        # Extract comprehensive data for AAPL
        result = agent.extract_stock_data("AAPL", include_analysis=True)
        
        if result["success"]:
            print(f"✅ Successfully extracted data for {result['symbol']}")
            print(f"📊 Current Price: ${result['stock_data']['price_info']['current_price']:.2f}")
            print(f"📈 Price Change: {result['stock_data']['price_info']['price_change']:.2f} ({result['stock_data']['price_info']['price_change_percent']:.2f}%)")
            print(f"🏢 Company: {result['stock_data']['company_info']['company_name']}")
            print(f"⏱️  Extraction Time: {result['extraction_time']:.2f}s")
            
            # Display AI insights if available
            if "analysis" in result:
                print("\n🤖 AI Insights:")
                for insight in result["analysis"]["insights"][:3]:
                    print(f"  • {insight}")
        else:
            print(f"❌ Failed to extract data: {result['error']}")

def example_real_time_price():
    """Example: Real-time price monitoring"""
    print("\n=== Real-time Price Monitoring ===")
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
        # Get current price
        price_result = agent.get_real_time_price("AAPL")
        
        if price_result["success"]:
            print(f"💰 Current AAPL Price: ${price_result['current_price']:.2f}")
            print(f"📊 Change: ${price_result['price_change']:.2f} ({price_result['price_change_percent']:.2f}%)")
            print(f"🕐 Market Status: {'Open' if price_result['market_hours'] else 'Closed'}")
        else:
            print(f"❌ Failed to get price: {price_result['error']}")

def example_historical_analysis():
    """Example: Historical data and technical analysis"""
    print("\n=== Historical Data Analysis ===")
    
    processor = DataProcessor()
    
    # Get 6 months of historical data
    historical_data = processor.get_historical_data("AAPL", period="6mo", interval="1d")
    
    if historical_data:
        print(f"📈 Retrieved {len(historical_data.data_points)} historical data points")
        
        # Calculate technical indicators
        indicators = processor.calculate_technical_indicators(historical_data)
        
        print("\n📊 Technical Indicators:")
        if indicators.get("sma_20"):
            print(f"  SMA 20: ${indicators['sma_20']:.2f}")
        if indicators.get("sma_50"):
            print(f"  SMA 50: ${indicators['sma_50']:.2f}")
        if indicators.get("rsi"):
            print(f"  RSI: {indicators['rsi']:.2f}")
        if indicators.get("macd"):
            print(f"  MACD: {indicators['macd']:.4f}")
        
        # Analyze price patterns
        patterns = processor.analyze_price_patterns(historical_data)
        
        if patterns and not patterns.get("error"):
            trend = patterns.get("trend", {})
            print(f"\n📈 Trend Analysis:")
            print(f"  Direction: {trend.get('direction', 'unknown').title()}")
            print(f"  Strength: {trend.get('strength', 0):.2f}")
            
            chart_patterns = patterns.get("chart_patterns", [])
            if chart_patterns:
                print(f"  Chart Patterns: {', '.join(chart_patterns)}")
    else:
        print("❌ Failed to retrieve historical data")

def example_dashboard_display():
    """Example: Using the dashboard for rich display"""
    print("\n=== Dashboard Display Example ===")
    
    dashboard = FinanceDashboard()
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
        result = agent.extract_stock_data("AAPL", include_analysis=True)
        
        if result["success"]:
            # Convert dict back to objects for dashboard
            from src.yahoo_finance_agent.data.models import StockData, AnalysisResult
            
            stock_data = StockData(**result["stock_data"])
            analysis = AnalysisResult(**result["analysis"]) if result.get("analysis") else None
            
            # Display using rich dashboard
            dashboard.display_stock_summary(stock_data, analysis)
        else:
            dashboard.display_error(result["error"])

def example_report_generation():
    """Example: Generate and save reports"""
    print("\n=== Report Generation Example ===")
    
    report_generator = ReportGenerator()
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
        result = agent.extract_stock_data("AAPL", include_analysis=True)
        
        if result["success"]:
            from src.yahoo_finance_agent.data.models import StockData, AnalysisResult
            
            stock_data = StockData(**result["stock_data"])
            analysis = AnalysisResult(**result["analysis"]) if result.get("analysis") else None
            
            # Generate text report
            text_report = report_generator.generate_stock_report(stock_data, analysis)
            text_file = report_generator.save_report_to_file(text_report, "aapl_report.txt")
            print(f"📄 Text report saved: {text_file}")
            
            # Generate JSON report
            json_report = report_generator.generate_json_report(stock_data, analysis)
            json_file = report_generator.save_report_to_file(json_report, "aapl_report.json")
            print(f"📋 JSON report saved: {json_file}")
        else:
            print(f"❌ Failed to generate report: {result['error']}")

def example_error_handling():
    """Example: Error handling and monitoring"""
    print("\n=== Error Handling Example ===")
    
    from src.yahoo_finance_agent.utils import error_tracker, health_monitor
    
    # Try to extract data for an invalid symbol
    with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
        result = agent.extract_stock_data("INVALID_SYMBOL")
        
        if not result["success"]:
            print(f"❌ Expected error: {result['error']}")
    
    # Check error summary
    error_summary = error_tracker.get_error_summary(hours=1)
    print(f"\n📊 Error Summary (last hour):")
    print(f"  Total errors: {error_summary['total_errors']}")
    print(f"  By category: {error_summary['by_category']}")
    
    # Check health status
    health_status = health_monitor.get_health_status()
    print(f"\n🏥 Health Status: {health_status['status'].upper()}")
    print(f"  Success rate: {health_status['success_rate']:.1%}")
    print(f"  Uptime: {health_status['uptime_seconds']:.0f}s")

def main():
    """Run all examples"""
    print("🚀 Yahoo Finance AI Browser Agent - Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_basic_extraction()
        example_real_time_price()
        example_historical_analysis()
        example_dashboard_display()
        example_report_generation()
        example_error_handling()
        
        print("\n✅ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
