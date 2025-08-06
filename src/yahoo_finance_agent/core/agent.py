"""
Main Yahoo Finance AI Agent
"""
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from .browser import BrowserManager
from ..scrapers.yahoo_scraper import YahooFinanceScraper
from ..ai.analyzer import FinancialAnalyzer
from ..data.models import StockData, ScrapingResult, AnalysisResult
from ..utils.helpers import validate_symbol, is_market_hours
from config import settings, get_yahoo_finance_url

class YahooFinanceAgent:
    """
    Main AI agent for Yahoo Finance data extraction and analysis
    """
    
    def __init__(self, headless: bool = None, use_ai_analysis: bool = True):
        """
        Initialize the Yahoo Finance Agent
        
        Args:
            headless: Run browser in headless mode
            use_ai_analysis: Enable AI-powered analysis
        """
        self.browser_manager = BrowserManager(headless=headless)
        self.scraper = YahooFinanceScraper(self.browser_manager)
        self.analyzer = FinancialAnalyzer() if use_ai_analysis else None
        self.use_ai_analysis = use_ai_analysis
        
        # Session tracking
        self.session_start = datetime.now()
        self.scraping_history: List[ScrapingResult] = []
        self.analysis_history: List[AnalysisResult] = []
        
        logger.info("Yahoo Finance Agent initialized successfully")
    
    def extract_stock_data(self, symbol: str = "AAPL", include_analysis: bool = True) -> Dict[str, Any]:
        """
        Extract comprehensive stock data for a given symbol
        
        Args:
            symbol: Stock symbol to extract data for
            include_analysis: Whether to include AI analysis
            
        Returns:
            Dictionary containing stock data and analysis results
        """
        # Validate symbol
        if not validate_symbol(symbol):
            logger.error(f"Invalid stock symbol: {symbol}")
            return {
                "success": False,
                "error": f"Invalid stock symbol: {symbol}",
                "timestamp": datetime.now()
            }
        
        logger.info(f"Starting data extraction for {symbol}")
        start_time = time.time()
        
        try:
            # Extract basic stock data
            scraping_result = self.scraper.scrape_stock_data(symbol)
            self.scraping_history.append(scraping_result)
            
            if not scraping_result.success:
                return {
                    "success": False,
                    "error": scraping_result.error_message,
                    "extraction_time": scraping_result.extraction_time,
                    "timestamp": scraping_result.timestamp
                }
            
            result = {
                "success": True,
                "symbol": symbol,
                "stock_data": scraping_result.data.dict(),
                "extraction_time": scraping_result.extraction_time,
                "timestamp": scraping_result.timestamp,
                "market_hours": is_market_hours()
            }
            
            # Add AI analysis if requested and available
            if include_analysis and self.use_ai_analysis and self.analyzer:
                try:
                    analysis_result = self.analyzer.analyze_stock_data(scraping_result.data)
                    self.analysis_history.append(analysis_result)
                    
                    result["analysis"] = {
                        "insights": analysis_result.insights,
                        "recommendations": analysis_result.recommendations,
                        "confidence_score": analysis_result.confidence_score,
                        "analysis_timestamp": analysis_result.analysis_timestamp
                    }
                    
                except Exception as e:
                    logger.warning(f"AI analysis failed: {str(e)}")
                    result["analysis_error"] = str(e)
            
            total_time = time.time() - start_time
            result["total_processing_time"] = total_time
            
            logger.success(f"Successfully extracted data for {symbol} in {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Data extraction failed for {symbol}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(),
                "total_processing_time": time.time() - start_time
            }
    
    def get_real_time_price(self, symbol: str = "AAPL") -> Dict[str, Any]:
        """
        Get real-time price information for a stock
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with current price information
        """
        logger.info(f"Getting real-time price for {symbol}")
        
        try:
            # Navigate to the stock page
            url = get_yahoo_finance_url(symbol)
            if not self.browser_manager.navigate_to_url(url):
                return {
                    "success": False,
                    "error": "Failed to navigate to Yahoo Finance page"
                }
            
            # Extract just price information quickly
            scraping_result = self.scraper.scrape_stock_data(symbol)
            
            if scraping_result.success and scraping_result.data:
                price_info = scraping_result.data.price_info
                return {
                    "success": True,
                    "symbol": symbol,
                    "current_price": price_info.current_price,
                    "price_change": price_info.price_change,
                    "price_change_percent": price_info.price_change_percent,
                    "timestamp": price_info.timestamp,
                    "market_hours": is_market_hours()
                }
            else:
                return {
                    "success": False,
                    "error": scraping_result.error_message or "Failed to extract price data"
                }
                
        except Exception as e:
            logger.error(f"Real-time price extraction failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def monitor_stock(self, symbol: str = "AAPL", duration_minutes: int = 60, 
                     interval_seconds: int = 300) -> List[Dict[str, Any]]:
        """
        Monitor a stock for a specified duration
        
        Args:
            symbol: Stock symbol to monitor
            duration_minutes: How long to monitor (in minutes)
            interval_seconds: Interval between checks (in seconds)
            
        Returns:
            List of price data points collected during monitoring
        """
        logger.info(f"Starting to monitor {symbol} for {duration_minutes} minutes")
        
        monitoring_data = []
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Get current price data
                price_data = self.get_real_time_price(symbol)
                price_data["monitoring_timestamp"] = datetime.now()
                monitoring_data.append(price_data)
                
                logger.info(f"Collected data point {len(monitoring_data)} for {symbol}")
                
                # Wait for next interval
                time.sleep(interval_seconds)
            
            logger.success(f"Monitoring completed for {symbol}. Collected {len(monitoring_data)} data points")
            return monitoring_data
            
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
            return monitoring_data
        except Exception as e:
            logger.error(f"Monitoring failed: {str(e)}")
            return monitoring_data
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session activities
        
        Returns:
            Dictionary with session statistics
        """
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        successful_scrapes = sum(1 for result in self.scraping_history if result.success)
        failed_scrapes = len(self.scraping_history) - successful_scrapes
        
        return {
            "session_start": self.session_start,
            "session_duration_seconds": session_duration,
            "total_scraping_attempts": len(self.scraping_history),
            "successful_scrapes": successful_scrapes,
            "failed_scrapes": failed_scrapes,
            "success_rate": successful_scrapes / len(self.scraping_history) if self.scraping_history else 0,
            "total_analyses": len(self.analysis_history),
            "ai_analysis_enabled": self.use_ai_analysis
        }
    
    def close(self):
        """Clean up resources and close browser"""
        logger.info("Closing Yahoo Finance Agent")
        
        # Log session summary
        summary = self.get_session_summary()
        logger.info(f"Session summary: {summary}")
        
        # Close browser
        self.browser_manager.close()
        
        logger.info("Yahoo Finance Agent closed successfully")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
