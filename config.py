"""
Configuration settings for Yahoo Finance AI Browser Agent
"""
import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    # Yahoo Finance URLs
    yahoo_finance_base_url: str = "https://finance.yahoo.com"
    yahoo_finance_quote_url: str = "https://finance.yahoo.com/quote/{symbol}/"
    
    # Browser settings
    browser_headless: bool = Field(default=True, env="BROWSER_HEADLESS")
    browser_timeout: int = Field(default=30, env="BROWSER_TIMEOUT")
    page_load_timeout: int = Field(default=20, env="PAGE_LOAD_TIMEOUT")
    implicit_wait: int = Field(default=10, env="IMPLICIT_WAIT")
    
    # Data extraction settings
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=2.0, env="RETRY_DELAY")
    request_delay: float = Field(default=1.0, env="REQUEST_DELAY")
    
    # AI settings
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    max_tokens: int = Field(default=2000, env="MAX_TOKENS")
    temperature: float = Field(default=0.1, env="TEMPERATURE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="yahoo_finance_agent.log", env="LOG_FILE")
    
    # Data storage
    data_dir: str = Field(default="data", env="DATA_DIR")
    cache_dir: str = Field(default="cache", env="CACHE_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Yahoo Finance specific configurations
YAHOO_FINANCE_CONFIG = {
    "selectors": {
        "price": "[data-symbol='AAPL'][data-field='regularMarketPrice']",
        "price_change": "[data-symbol='AAPL'][data-field='regularMarketChange']",
        "price_change_percent": "[data-symbol='AAPL'][data-field='regularMarketChangePercent']",
        "market_cap": "[data-testid='MARKET_CAP-value']",
        "pe_ratio": "[data-testid='PE_RATIO-value']",
        "eps": "[data-testid='EPS_RATIO-value']",
        "volume": "[data-testid='TD_VOLUME-value']",
        "avg_volume": "[data-testid='AVERAGE_VOLUME_3MONTH-value']",
        "company_name": "h1[data-reactid]",
        "previous_close": "[data-testid='PREV_CLOSE-value']",
        "open": "[data-testid='OPEN-value']",
        "day_range": "[data-testid='DAYS_RANGE-value']",
        "52_week_range": "[data-testid='FIFTY_TWO_WK_RANGE-value']",
        "dividend_yield": "[data-testid='DIVIDEND_AND_YIELD-value']",
        "beta": "[data-testid='BETA_5Y-value']"
    },
    "tabs": {
        "summary": "Summary",
        "historical": "Historical Data",
        "profile": "Profile",
        "financials": "Financials",
        "analysis": "Analysis",
        "options": "Options",
        "holders": "Holders",
        "sustainability": "Sustainability"
    }
}

def get_yahoo_finance_url(symbol: str = "AAPL") -> str:
    """Get Yahoo Finance URL for a specific symbol"""
    return settings.yahoo_finance_quote_url.format(symbol=symbol)

def create_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.cache_dir, exist_ok=True)
