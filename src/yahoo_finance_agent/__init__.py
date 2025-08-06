"""
Yahoo Finance AI Browser Agent

A comprehensive AI-powered browser agent for extracting and analyzing
financial data from Yahoo Finance, specifically designed for AAPL stock data.
"""

__version__ = "1.0.0"
__author__ = "AI Browser Agent Team"
__description__ = "AI-powered Yahoo Finance data extraction and analysis agent"

from .core.agent import YahooFinanceAgent
from .core.browser import BrowserManager
from .scrapers.yahoo_scraper import YahooFinanceScraper
from .ai.analyzer import FinancialAnalyzer
from .data.models import StockData, CompanyInfo, HistoricalData

__all__ = [
    "YahooFinanceAgent",
    "BrowserManager", 
    "YahooFinanceScraper",
    "FinancialAnalyzer",
    "StockData",
    "CompanyInfo", 
    "HistoricalData"
]
