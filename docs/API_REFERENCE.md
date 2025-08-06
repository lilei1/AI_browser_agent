# API Reference

## Core Classes

### YahooFinanceAgent

Main agent class for Yahoo Finance data extraction and analysis.

```python
from src.yahoo_finance_agent import YahooFinanceAgent

agent = YahooFinanceAgent(headless=True, use_ai_analysis=True)
```

#### Constructor Parameters

- `headless` (bool): Run browser in headless mode (default: True)
- `use_ai_analysis` (bool): Enable AI-powered analysis (default: True)

#### Methods

##### `extract_stock_data(symbol, include_analysis=True)`

Extract comprehensive stock data for a symbol.

**Parameters:**
- `symbol` (str): Stock symbol (e.g., "AAPL")
- `include_analysis` (bool): Include AI analysis in results

**Returns:**
- `Dict[str, Any]`: Result dictionary with success status, data, and analysis

**Example:**
```python
with YahooFinanceAgent() as agent:
    result = agent.extract_stock_data("AAPL")
    if result["success"]:
        print(f"Price: ${result['stock_data']['price_info']['current_price']}")
```

##### `get_real_time_price(symbol)`

Get current stock price quickly.

**Parameters:**
- `symbol` (str): Stock symbol

**Returns:**
- `Dict[str, Any]`: Price information with current price, change, and market status

##### `monitor_stock(symbol, duration_minutes, interval_seconds)`

Monitor stock price for a specified duration.

**Parameters:**
- `symbol` (str): Stock symbol to monitor
- `duration_minutes` (int): Monitoring duration in minutes
- `interval_seconds` (int): Check interval in seconds

**Returns:**
- `List[Dict[str, Any]]`: List of price data points collected

### BrowserManager

Manages browser instances for web scraping.

```python
from src.yahoo_finance_agent.core import BrowserManager

browser = BrowserManager(headless=True, use_undetected=True)
```

#### Constructor Parameters

- `headless` (bool): Run browser in headless mode
- `use_undetected` (bool): Use undetected-chromedriver for anti-detection

#### Methods

##### `setup_driver()`

Set up and configure Chrome driver.

**Returns:**
- `webdriver.Chrome`: Configured Chrome WebDriver instance

##### `navigate_to_url(url, wait_for_element=None)`

Navigate to a URL and optionally wait for an element.

**Parameters:**
- `url` (str): URL to navigate to
- `wait_for_element` (str): CSS selector to wait for (optional)

**Returns:**
- `bool`: True if navigation successful

### YahooFinanceScraper

Advanced scraper for Yahoo Finance data.

```python
from src.yahoo_finance_agent.scrapers import YahooFinanceScraper

scraper = YahooFinanceScraper(browser_manager)
```

#### Methods

##### `scrape_stock_data(symbol)`

Scrape comprehensive stock data.

**Parameters:**
- `symbol` (str): Stock symbol

**Returns:**
- `ScrapingResult`: Result object with success status and extracted data

### FinancialAnalyzer

AI-powered financial data analyzer.

```python
from src.yahoo_finance_agent.ai import FinancialAnalyzer

analyzer = FinancialAnalyzer(api_key="your_openai_key")
```

#### Methods

##### `analyze_stock_data(stock_data)`

Perform AI analysis of stock data.

**Parameters:**
- `stock_data` (StockData): Stock data to analyze

**Returns:**
- `AnalysisResult`: Analysis result with insights and recommendations

### DataProcessor

Process and analyze financial data.

```python
from src.yahoo_finance_agent.data import DataProcessor

processor = DataProcessor()
```

#### Methods

##### `get_historical_data(symbol, period="1y", interval="1d")`

Fetch historical stock data.

**Parameters:**
- `symbol` (str): Stock symbol
- `period` (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
- `interval` (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

**Returns:**
- `HistoricalData`: Historical data object

##### `calculate_technical_indicators(historical_data)`

Calculate technical indicators from historical data.

**Parameters:**
- `historical_data` (HistoricalData): Historical stock data

**Returns:**
- `Dict[str, Any]`: Dictionary with technical indicators

### FinanceDashboard

Rich console-based dashboard for displaying financial data.

```python
from src.yahoo_finance_agent.ui import FinanceDashboard

dashboard = FinanceDashboard()
```

#### Methods

##### `display_stock_summary(stock_data, analysis=None)`

Display comprehensive stock summary.

**Parameters:**
- `stock_data` (StockData): Stock data to display
- `analysis` (AnalysisResult): Optional AI analysis results

##### `display_monitoring_results(monitoring_data)`

Display stock monitoring results.

**Parameters:**
- `monitoring_data` (List[Dict]): List of monitoring data points

### ReportGenerator

Generate various types of reports from financial data.

```python
from src.yahoo_finance_agent.ui import ReportGenerator

generator = ReportGenerator()
```

#### Methods

##### `generate_stock_report(stock_data, analysis=None)`

Generate comprehensive stock report.

**Parameters:**
- `stock_data` (StockData): Stock data
- `analysis` (AnalysisResult): Optional AI analysis

**Returns:**
- `str`: Formatted report string

##### `save_report_to_file(report_content, filename=None)`

Save report to file.

**Parameters:**
- `report_content` (str): Report content to save
- `filename` (str): Optional filename (auto-generated if not provided)

**Returns:**
- `str`: Path to saved file

## Data Models

### StockData

Complete stock data model.

**Fields:**
- `symbol` (str): Stock symbol
- `price_info` (StockPrice): Current price information
- `trading_metrics` (TradingMetrics): Trading metrics
- `financial_ratios` (FinancialRatios): Financial ratios
- `company_info` (CompanyInfo): Company information
- `historical_data` (HistoricalData): Optional historical data
- `last_updated` (datetime): Last update timestamp

### StockPrice

Stock price information.

**Fields:**
- `current_price` (float): Current stock price
- `price_change` (float): Price change from previous close
- `price_change_percent` (float): Percentage change
- `previous_close` (float): Previous closing price
- `open_price` (float): Opening price
- `day_low` (float): Day's low price
- `day_high` (float): Day's high price
- `week_52_low` (float): 52-week low price
- `week_52_high` (float): 52-week high price

### TradingMetrics

Trading volume and metrics.

**Fields:**
- `volume` (int): Current trading volume
- `avg_volume` (int): Average trading volume (3 months)
- `market_cap` (str): Market capitalization
- `shares_outstanding` (int): Shares outstanding

### FinancialRatios

Financial ratios and metrics.

**Fields:**
- `pe_ratio` (float): Price-to-earnings ratio
- `eps` (float): Earnings per share
- `dividend_yield` (float): Dividend yield percentage
- `beta` (float): Beta coefficient
- `book_value` (float): Book value per share
- `price_to_book` (float): Price-to-book ratio

### CompanyInfo

Company information and profile.

**Fields:**
- `symbol` (str): Stock symbol
- `company_name` (str): Company name
- `sector` (str): Business sector
- `industry` (str): Industry classification
- `description` (str): Company description
- `website` (str): Company website
- `employees` (int): Number of employees
- `headquarters` (str): Headquarters location

## Utility Functions

### Error Handling

```python
from src.yahoo_finance_agent.utils import retry_with_backoff, handle_errors

@retry_with_backoff(max_retries=3, base_delay=1.0)
def my_function():
    # Function that might fail
    pass

@handle_errors(category=ErrorCategory.NETWORK, severity=ErrorSeverity.HIGH)
def another_function():
    # Function with error handling
    pass
```

### Data Formatting

```python
from src.yahoo_finance_agent.utils import format_currency, format_percentage, format_volume

price_str = format_currency(123.45)  # "$123.45"
percent_str = format_percentage(2.5)  # "2.50%"
volume_str = format_volume(1500000)  # "1.50M"
```

### Validation

```python
from src.yahoo_finance_agent.utils import validate_symbol, clean_numeric_value

is_valid = validate_symbol("AAPL")  # True
numeric_value = clean_numeric_value("$123.45")  # 123.45
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
BROWSER_HEADLESS=true
BROWSER_TIMEOUT=30
MAX_RETRIES=3
LOG_LEVEL=INFO
```

### Settings Object

```python
from config import settings

print(settings.openai_api_key)
print(settings.browser_headless)
print(settings.max_retries)
```

## Error Handling

### Error Categories

- `ErrorCategory.NETWORK`: Network-related errors
- `ErrorCategory.BROWSER`: Browser automation errors
- `ErrorCategory.PARSING`: Data parsing errors
- `ErrorCategory.VALIDATION`: Data validation errors
- `ErrorCategory.API`: API-related errors
- `ErrorCategory.SYSTEM`: System-level errors

### Error Severity

- `ErrorSeverity.LOW`: Low severity errors
- `ErrorSeverity.MEDIUM`: Medium severity errors
- `ErrorSeverity.HIGH`: High severity errors
- `ErrorSeverity.CRITICAL`: Critical errors

### Monitoring

```python
from src.yahoo_finance_agent.utils import error_tracker, health_monitor

# Get error summary
error_summary = error_tracker.get_error_summary(hours=24)

# Check health status
health_status = health_monitor.get_health_status()
is_healthy = health_monitor.is_healthy()
```
