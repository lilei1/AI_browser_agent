"""
Data models and structures for Yahoo Finance Agent
"""

from .models import (
    StockPrice,
    TradingMetrics,
    FinancialRatios,
    CompanyInfo,
    HistoricalDataPoint,
    HistoricalData,
    StockData,
    ScrapingResult,
    AnalysisResult
)
# from .processor import DataProcessor  # Disabled for Python 3.7 compatibility

__all__ = [
    "StockPrice",
    "TradingMetrics",
    "FinancialRatios",
    "CompanyInfo",
    "HistoricalDataPoint",
    "HistoricalData",
    "StockData",
    "ScrapingResult",
    "AnalysisResult"
    # "DataProcessor"  # Disabled for Python 3.7 compatibility
]
