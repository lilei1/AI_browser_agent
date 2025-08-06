"""
Data models for Yahoo Finance data structures
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class StockPrice(BaseModel):
    """Stock price information"""
    current_price: Optional[float] = Field(None, description="Current stock price")
    price_change: Optional[float] = Field(None, description="Price change from previous close")
    price_change_percent: Optional[float] = Field(None, description="Percentage change from previous close")
    previous_close: Optional[float] = Field(None, description="Previous closing price")
    open_price: Optional[float] = Field(None, description="Opening price")
    day_low: Optional[float] = Field(None, description="Day's low price")
    day_high: Optional[float] = Field(None, description="Day's high price")
    week_52_low: Optional[float] = Field(None, description="52-week low price")
    week_52_high: Optional[float] = Field(None, description="52-week high price")
    timestamp: datetime = Field(default_factory=datetime.now, description="Data extraction timestamp")

class TradingMetrics(BaseModel):
    """Trading volume and metrics"""
    volume: Optional[int] = Field(None, description="Current trading volume")
    avg_volume: Optional[int] = Field(None, description="Average trading volume (3 months)")
    market_cap: Optional[str] = Field(None, description="Market capitalization")
    shares_outstanding: Optional[int] = Field(None, description="Shares outstanding")

class FinancialRatios(BaseModel):
    """Financial ratios and metrics"""
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    eps: Optional[float] = Field(None, description="Earnings per share")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield percentage")
    beta: Optional[float] = Field(None, description="Beta coefficient")
    book_value: Optional[float] = Field(None, description="Book value per share")
    price_to_book: Optional[float] = Field(None, description="Price-to-book ratio")

class CompanyInfo(BaseModel):
    """Company information and profile"""
    symbol: str = Field(..., description="Stock symbol")
    company_name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    description: Optional[str] = Field(None, description="Company description")
    website: Optional[str] = Field(None, description="Company website")
    employees: Optional[int] = Field(None, description="Number of employees")
    headquarters: Optional[str] = Field(None, description="Headquarters location")

class HistoricalDataPoint(BaseModel):
    """Single historical data point"""
    date: datetime = Field(..., description="Date of the data point")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="High price")
    low: Optional[float] = Field(None, description="Low price")
    close: Optional[float] = Field(None, description="Closing price")
    adj_close: Optional[float] = Field(None, description="Adjusted closing price")
    volume: Optional[int] = Field(None, description="Trading volume")

class HistoricalData(BaseModel):
    """Historical stock data"""
    symbol: str = Field(..., description="Stock symbol")
    data_points: List[HistoricalDataPoint] = Field(default_factory=list, description="Historical data points")
    period: Optional[str] = Field(None, description="Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: Optional[str] = Field(None, description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")

class StockData(BaseModel):
    """Complete stock data model"""
    symbol: str = Field(..., description="Stock symbol")
    price_info: StockPrice = Field(..., description="Current price information")
    trading_metrics: TradingMetrics = Field(default_factory=TradingMetrics, description="Trading metrics")
    financial_ratios: FinancialRatios = Field(default_factory=FinancialRatios, description="Financial ratios")
    company_info: CompanyInfo = Field(..., description="Company information")
    historical_data: Optional[HistoricalData] = Field(None, description="Historical data")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper() if v else v

class ScrapingResult(BaseModel):
    """Result of a scraping operation"""
    success: bool = Field(..., description="Whether scraping was successful")
    data: Optional[StockData] = Field(None, description="Scraped stock data")
    error_message: Optional[str] = Field(None, description="Error message if scraping failed")
    extraction_time: float = Field(..., description="Time taken for extraction in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Scraping timestamp")

class AnalysisResult(BaseModel):
    """Result of AI analysis"""
    symbol: str = Field(..., description="Stock symbol")
    analysis_type: str = Field(..., description="Type of analysis performed")
    insights: List[str] = Field(default_factory=list, description="Key insights from analysis")
    recommendations: List[str] = Field(default_factory=list, description="AI recommendations")
    confidence_score: Optional[float] = Field(None, description="Confidence score (0-1)")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")
