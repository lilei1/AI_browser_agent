"""
Utility functions and helpers for Yahoo Finance Agent
"""
import re
import time
from typing import Optional, Union, Any
from decimal import Decimal, InvalidOperation
from loguru import logger

def clean_numeric_value(value: str) -> Optional[float]:
    """
    Clean and convert string numeric values to float
    
    Args:
        value: String value to clean and convert
        
    Returns:
        Float value or None if conversion fails
    """
    if not value or value in ['N/A', '--', '']:
        return None
    
    try:
        # Remove common formatting characters
        cleaned = str(value).strip()
        cleaned = re.sub(r'[,$%+\s]', '', cleaned)
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Handle percentage values
        if '%' in str(value):
            cleaned = cleaned.replace('%', '')
            return float(cleaned)
        
        return float(cleaned)
        
    except (ValueError, TypeError, AttributeError):
        logger.warning(f"Could not convert '{value}' to numeric value")
        return None

def parse_market_cap(market_cap_str: str) -> Optional[str]:
    """
    Parse market cap string and return standardized format
    
    Args:
        market_cap_str: Market cap string (e.g., "2.5T", "150.2B")
        
    Returns:
        Standardized market cap string or None
    """
    if not market_cap_str:
        return None
    
    try:
        # Clean the string
        cleaned = market_cap_str.strip().upper()
        
        # Extract number and suffix
        match = re.match(r'([\d.]+)([KMBT]?)', cleaned)
        if match:
            number, suffix = match.groups()
            
            # Convert to standard format
            if suffix == 'K':
                return f"{float(number) * 1000:,.0f}"
            elif suffix == 'M':
                return f"{float(number) * 1000000:,.0f}"
            elif suffix == 'B':
                return f"{float(number) * 1000000000:,.0f}"
            elif suffix == 'T':
                return f"{float(number) * 1000000000000:,.0f}"
            else:
                return f"{float(number):,.0f}"
        
        return market_cap_str
        
    except (ValueError, TypeError, AttributeError):
        logger.warning(f"Could not parse market cap '{market_cap_str}'")
        return market_cap_str

def format_currency(value: Optional[float], currency: str = "USD") -> str:
    """
    Format numeric value as currency
    
    Args:
        value: Numeric value to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return "N/A"
    
    try:
        if currency.upper() == "USD":
            return f"${value:,.2f}"
        else:
            return f"{value:,.2f} {currency}"
    except (ValueError, TypeError):
        return str(value)

def format_percentage(value: Optional[float], decimal_places: int = 2) -> str:
    """
    Format numeric value as percentage
    
    Args:
        value: Numeric value to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "N/A"
    
    try:
        return f"{value:.{decimal_places}f}%"
    except (ValueError, TypeError):
        return str(value)

def format_volume(volume: Optional[int]) -> str:
    """
    Format volume with appropriate suffix (K, M, B)
    
    Args:
        volume: Volume value to format
        
    Returns:
        Formatted volume string
    """
    if volume is None:
        return "N/A"
    
    try:
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.2f}K"
        else:
            return f"{volume:,}"
    except (ValueError, TypeError):
        return str(volume)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {str(e)}")
            
            raise last_exception
        
        return wrapper
    return decorator

def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """
    Safely divide two numbers, handling None values and division by zero
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        
    Returns:
        Division result or None if invalid
    """
    if numerator is None or denominator is None or denominator == 0:
        return None
    
    try:
        return float(numerator) / float(denominator)
    except (ValueError, TypeError, ZeroDivisionError):
        return None

def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # Basic validation: 1-5 characters, letters only
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol.upper()))

def extract_numeric_from_text(text: str) -> Optional[float]:
    """
    Extract first numeric value from text
    
    Args:
        text: Text containing numeric value
        
    Returns:
        First numeric value found or None
    """
    if not text:
        return None
    
    # Find first number in the text
    match = re.search(r'[\d,]+\.?\d*', text.replace(',', ''))
    if match:
        try:
            return float(match.group().replace(',', ''))
        except ValueError:
            pass
    
    return None

def is_market_hours() -> bool:
    """
    Check if current time is within market hours (9:30 AM - 4:00 PM ET)
    
    Returns:
        True if within market hours, False otherwise
    """
    from datetime import datetime
    import pytz
    
    try:
        et = pytz.timezone('US/Eastern')
        now = datetime.now(et)
        
        # Check if weekday (0=Monday, 6=Sunday)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if within trading hours (9:30 AM - 4:00 PM ET)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
        
    except Exception:
        # If timezone handling fails, assume market is open
        return True
