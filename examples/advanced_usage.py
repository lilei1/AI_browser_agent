#!/usr/bin/env python3
"""
Advanced usage examples for Yahoo Finance AI Browser Agent
"""
import sys
import os
import asyncio
import time
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.yahoo_finance_agent import YahooFinanceAgent
from src.yahoo_finance_agent.ui import FinanceDashboard, ReportGenerator
from src.yahoo_finance_agent.data import DataProcessor
from src.yahoo_finance_agent.utils import error_tracker, health_monitor

def example_multi_symbol_analysis():
    """Example: Analyze multiple symbols"""
    print("=== Multi-Symbol Analysis ===")
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    dashboard = FinanceDashboard()
    results = {}
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
        for symbol in symbols:
            print(f"📊 Analyzing {symbol}...")
            
            try:
                result = agent.extract_stock_data(symbol, include_analysis=True)
                results[symbol] = result
                
                if result["success"]:
                    price = result["stock_data"]["price_info"]["current_price"]
                    change_pct = result["stock_data"]["price_info"]["price_change_percent"]
                    print(f"  ✅ {symbol}: ${price:.2f} ({change_pct:+.2f}%)")
                else:
                    print(f"  ❌ {symbol}: {result['error']}")
                    
            except Exception as e:
                print(f"  ❌ {symbol}: Error - {str(e)}")
                results[symbol] = {"success": False, "error": str(e)}
    
    # Summary
    successful = sum(1 for r in results.values() if r.get("success", False))
    print(f"\n📈 Analysis Summary: {successful}/{len(symbols)} successful")
    
    return results

def example_continuous_monitoring():
    """Example: Continuous monitoring with alerts"""
    print("\n=== Continuous Monitoring with Alerts ===")
    
    symbol = "AAPL"
    alert_threshold = 2.0  # Alert if price changes by more than 2%
    monitoring_duration = 300  # 5 minutes
    check_interval = 30  # 30 seconds
    
    print(f"🔍 Monitoring {symbol} for {monitoring_duration//60} minutes")
    print(f"⚠️  Alert threshold: ±{alert_threshold}%")
    
    dashboard = FinanceDashboard()
    baseline_price = None
    alerts_triggered = 0
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
        start_time = time.time()
        
        while time.time() - start_time < monitoring_duration:
            try:
                result = agent.get_real_time_price(symbol)
                
                if result["success"]:
                    current_price = result["current_price"]
                    change_pct = result["price_change_percent"]
                    
                    # Set baseline on first successful read
                    if baseline_price is None:
                        baseline_price = current_price
                        print(f"📍 Baseline price set: ${baseline_price:.2f}")
                    
                    # Check for alerts
                    price_change_from_baseline = ((current_price - baseline_price) / baseline_price) * 100
                    
                    if abs(price_change_from_baseline) > alert_threshold:
                        alerts_triggered += 1
                        alert_emoji = "🚨" if price_change_from_baseline < 0 else "🚀"
                        print(f"{alert_emoji} ALERT: {symbol} moved {price_change_from_baseline:+.2f}% from baseline!")
                    
                    # Regular update
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"[{timestamp}] {symbol}: ${current_price:.2f} ({change_pct:+.2f}%)")
                
                else:
                    print(f"❌ Failed to get price: {result['error']}")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {str(e)}")
                time.sleep(check_interval)
    
    print(f"\n📊 Monitoring completed. Alerts triggered: {alerts_triggered}")

def example_technical_analysis_comparison():
    """Example: Compare technical indicators across timeframes"""
    print("\n=== Technical Analysis Comparison ===")
    
    symbol = "AAPL"
    timeframes = [
        ("1mo", "1d", "1 Month Daily"),
        ("3mo", "1d", "3 Month Daily"),
        ("1y", "1wk", "1 Year Weekly")
    ]
    
    processor = DataProcessor()
    
    print(f"📈 Analyzing {symbol} across multiple timeframes...")
    
    for period, interval, description in timeframes:
        print(f"\n📊 {description}:")
        
        try:
            historical_data = processor.get_historical_data(symbol, period, interval)
            
            if historical_data:
                indicators = processor.calculate_technical_indicators(historical_data)
                patterns = processor.analyze_price_patterns(historical_data)
                
                # Display key indicators
                print(f"  Data points: {len(historical_data.data_points)}")
                
                if indicators.get("sma_20"):
                    print(f"  SMA 20: ${indicators['sma_20']:.2f}")
                if indicators.get("rsi"):
                    rsi_status = "Overbought" if indicators['rsi'] > 70 else "Oversold" if indicators['rsi'] < 30 else "Neutral"
                    print(f"  RSI: {indicators['rsi']:.1f} ({rsi_status})")
                if indicators.get("macd"):
                    macd_signal = "Bullish" if indicators['macd'] > indicators.get('macd_signal', 0) else "Bearish"
                    print(f"  MACD: {indicators['macd']:.4f} ({macd_signal})")
                
                # Trend analysis
                if patterns and not patterns.get("error"):
                    trend = patterns.get("trend", {})
                    print(f"  Trend: {trend.get('direction', 'unknown').title()} (Strength: {trend.get('strength', 0):.2f})")
            
            else:
                print(f"  ❌ Failed to get data for {description}")
                
        except Exception as e:
            print(f"  ❌ Error analyzing {description}: {str(e)}")

def example_custom_analysis_workflow():
    """Example: Custom analysis workflow with AI insights"""
    print("\n=== Custom Analysis Workflow ===")
    
    symbol = "AAPL"
    dashboard = FinanceDashboard()
    report_generator = ReportGenerator()
    
    print(f"🔬 Running comprehensive analysis for {symbol}...")
    
    # Step 1: Extract current data
    print("1️⃣ Extracting current market data...")
    with YahooFinanceAgent(headless=True, use_ai_analysis=True) as agent:
        current_result = agent.extract_stock_data(symbol, include_analysis=True)
    
    if not current_result["success"]:
        print(f"❌ Failed to get current data: {current_result['error']}")
        return
    
    # Step 2: Get historical context
    print("2️⃣ Gathering historical context...")
    processor = DataProcessor()
    historical_data = processor.get_historical_data(symbol, period="1y", interval="1d")
    
    if not historical_data:
        print("❌ Failed to get historical data")
        return
    
    # Step 3: Technical analysis
    print("3️⃣ Performing technical analysis...")
    indicators = processor.calculate_technical_indicators(historical_data)
    patterns = processor.analyze_price_patterns(historical_data)
    
    # Step 4: Compile comprehensive report
    print("4️⃣ Compiling comprehensive report...")
    
    from src.yahoo_finance_agent.data.models import StockData, AnalysisResult
    stock_data = StockData(**current_result["stock_data"])
    analysis = AnalysisResult(**current_result["analysis"]) if current_result.get("analysis") else None
    
    # Create enhanced report with technical analysis
    report_lines = []
    report_lines.append(f"COMPREHENSIVE ANALYSIS REPORT: {symbol}")
    report_lines.append("=" * 50)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Current market data
    report_lines.append("CURRENT MARKET DATA")
    report_lines.append("-" * 20)
    price_info = stock_data.price_info
    report_lines.append(f"Price: ${price_info.current_price:.2f}")
    report_lines.append(f"Change: ${price_info.price_change:.2f} ({price_info.price_change_percent:.2f}%)")
    report_lines.append("")
    
    # Technical indicators
    report_lines.append("TECHNICAL INDICATORS")
    report_lines.append("-" * 19)
    if indicators.get("sma_20"):
        report_lines.append(f"SMA 20: ${indicators['sma_20']:.2f}")
    if indicators.get("sma_50"):
        report_lines.append(f"SMA 50: ${indicators['sma_50']:.2f}")
    if indicators.get("rsi"):
        report_lines.append(f"RSI: {indicators['rsi']:.1f}")
    if indicators.get("macd"):
        report_lines.append(f"MACD: {indicators['macd']:.4f}")
    report_lines.append("")
    
    # Pattern analysis
    if patterns and not patterns.get("error"):
        report_lines.append("PATTERN ANALYSIS")
        report_lines.append("-" * 16)
        trend = patterns.get("trend", {})
        report_lines.append(f"Trend: {trend.get('direction', 'unknown').title()}")
        report_lines.append(f"Trend Strength: {trend.get('strength', 0):.2f}")
        
        chart_patterns = patterns.get("chart_patterns", [])
        if chart_patterns:
            report_lines.append(f"Chart Patterns: {', '.join(chart_patterns)}")
        report_lines.append("")
    
    # AI insights
    if analysis:
        report_lines.append("AI INSIGHTS")
        report_lines.append("-" * 11)
        for insight in analysis.insights:
            report_lines.append(f"• {insight}")
        report_lines.append("")
        
        if analysis.recommendations:
            report_lines.append("RECOMMENDATIONS")
            report_lines.append("-" * 15)
            for rec in analysis.recommendations:
                report_lines.append(f"• {rec}")
            report_lines.append("")
    
    # Save comprehensive report
    comprehensive_report = "\n".join(report_lines)
    report_file = report_generator.save_report_to_file(
        comprehensive_report, 
        f"{symbol}_comprehensive_analysis.txt"
    )
    
    print(f"✅ Comprehensive analysis completed!")
    print(f"📄 Report saved: {report_file}")
    
    # Display summary on dashboard
    dashboard.display_stock_summary(stock_data, analysis)

def example_performance_monitoring():
    """Example: Monitor agent performance and health"""
    print("\n=== Performance Monitoring ===")
    
    # Run some operations to generate metrics
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    print("🏃 Running operations to generate performance metrics...")
    
    with YahooFinanceAgent(headless=True, use_ai_analysis=False) as agent:
        for symbol in symbols:
            try:
                result = agent.get_real_time_price(symbol)
                print(f"  📊 {symbol}: {'✅' if result['success'] else '❌'}")
            except Exception as e:
                print(f"  📊 {symbol}: ❌ {str(e)}")
    
    # Check health status
    health_status = health_monitor.get_health_status()
    
    print(f"\n🏥 System Health Status: {health_status['status'].upper()}")
    print(f"  Success Rate: {health_status['success_rate']:.1%}")
    print(f"  Total Requests: {health_status['metrics']['requests_total']}")
    print(f"  Successful: {health_status['metrics']['requests_successful']}")
    print(f"  Failed: {health_status['metrics']['requests_failed']}")
    print(f"  Avg Response Time: {health_status['metrics']['average_response_time']:.2f}s")
    print(f"  Uptime: {health_status['uptime_seconds']:.0f}s")
    
    # Error summary
    error_summary = error_tracker.get_error_summary(hours=24)
    print(f"\n📊 Error Summary (24h):")
    print(f"  Total Errors: {error_summary['total_errors']}")
    
    if error_summary['by_category']:
        print("  By Category:")
        for category, count in error_summary['by_category'].items():
            print(f"    {category}: {count}")
    
    if error_summary['most_common']:
        print("  Most Common:")
        for error_info in error_summary['most_common'][:3]:
            print(f"    {error_info['error'][:50]}... ({error_info['count']}x)")

def main():
    """Run advanced examples"""
    print("🚀 Yahoo Finance AI Browser Agent - Advanced Examples")
    print("=" * 60)
    
    try:
        # Run advanced examples
        multi_results = example_multi_symbol_analysis()
        example_continuous_monitoring()
        example_technical_analysis_comparison()
        example_custom_analysis_workflow()
        example_performance_monitoring()
        
        print("\n✅ All advanced examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
