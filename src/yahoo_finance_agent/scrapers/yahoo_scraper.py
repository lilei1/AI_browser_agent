"""
Yahoo Finance web scraper for extracting stock data
"""
import time
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import requests
from loguru import logger

from ..data.models import (
    StockData, StockPrice, TradingMetrics, FinancialRatios, 
    CompanyInfo, ScrapingResult
)
from ..utils.helpers import clean_numeric_value, parse_market_cap
from ..utils.error_handler import (
    retry_with_backoff, handle_errors, monitor_performance,
    ErrorCategory, ErrorSeverity, error_tracker
)
from .intelligent_extractor import IntelligentExtractor
from config import settings, YAHOO_FINANCE_CONFIG, get_yahoo_finance_url

class YahooFinanceScraper:
    """
    Advanced scraper for Yahoo Finance stock data with multiple extraction methods
    """
    
    def __init__(self, browser_manager=None):
        """Initialize the scraper"""
        self.browser_manager = browser_manager
        self.intelligent_extractor = IntelligentExtractor(browser_manager)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    @monitor_performance
    @retry_with_backoff(max_retries=3, base_delay=2.0, exceptions=(TimeoutException, NoSuchElementException))
    def scrape_stock_data(self, symbol: str = "AAPL") -> ScrapingResult:
        """
        Main method to scrape comprehensive stock data
        """
        start_time = time.time()

        try:
            logger.info(f"Starting to scrape data for {symbol}")

            # Try browser-based scraping first (more reliable for dynamic content)
            if self.browser_manager:
                stock_data = self._scrape_with_browser(symbol)
            else:
                # Fallback to requests-based scraping
                stock_data = self._scrape_with_requests(symbol)

            extraction_time = time.time() - start_time

            if stock_data:
                logger.success(f"Successfully scraped data for {symbol} in {extraction_time:.2f}s")
                return ScrapingResult(
                    success=True,
                    data=stock_data,
                    extraction_time=extraction_time
                )
            else:
                logger.error(f"Failed to scrape data for {symbol}")
                return ScrapingResult(
                    success=False,
                    error_message="No data extracted",
                    extraction_time=extraction_time
                )

        except Exception as e:
            extraction_time = time.time() - start_time

            # Record error with appropriate category
            category = ErrorCategory.BROWSER if "webdriver" in str(e).lower() else ErrorCategory.PARSING
            error_tracker.record_error(e, category, ErrorSeverity.HIGH, {"symbol": symbol})

            logger.error(f"Error scraping {symbol}: {str(e)}")
            return ScrapingResult(
                success=False,
                error_message=str(e),
                extraction_time=extraction_time
            )
    
    @handle_errors(category=ErrorCategory.BROWSER, severity=ErrorSeverity.HIGH, reraise=False, default_return=None)
    def _scrape_with_browser(self, symbol: str) -> Optional[StockData]:
        """Scrape using browser automation (Selenium)"""
        try:
            url = get_yahoo_finance_url(symbol)
            driver = self.browser_manager.get_driver()

            logger.info(f"Navigating to {url}")
            driver.get(url)

            # Wait for page to load
            WebDriverWait(driver, settings.page_load_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Add small delay for dynamic content
            time.sleep(2)

            # Extract data using multiple strategies
            price_info = self._extract_price_info(driver, symbol)
            trading_metrics = self._extract_trading_metrics(driver)
            financial_ratios = self._extract_financial_ratios(driver)
            company_info = self._extract_company_info(driver, symbol)

            return StockData(
                symbol=symbol,
                price_info=price_info,
                trading_metrics=trading_metrics,
                financial_ratios=financial_ratios,
                company_info=company_info
            )

        except Exception as e:
            logger.error(f"Browser scraping failed: {str(e)}")
            return None
    
    def _scrape_with_requests(self, symbol: str) -> Optional[StockData]:
        """Scrape using HTTP requests and BeautifulSoup"""
        try:
            url = get_yahoo_finance_url(symbol)
            logger.info(f"Fetching {url} with requests")
            
            response = self.session.get(url, timeout=settings.browser_timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data from HTML
            price_info = self._extract_price_info_from_soup(soup, symbol)
            trading_metrics = self._extract_trading_metrics_from_soup(soup)
            financial_ratios = self._extract_financial_ratios_from_soup(soup)
            company_info = self._extract_company_info_from_soup(soup, symbol)
            
            return StockData(
                symbol=symbol,
                price_info=price_info,
                trading_metrics=trading_metrics,
                financial_ratios=financial_ratios,
                company_info=company_info
            )
            
        except Exception as e:
            logger.error(f"Requests scraping failed: {str(e)}")
            return None
    
    def _extract_price_info(self, driver, symbol: str) -> StockPrice:
        """Extract price information using intelligent extraction"""
        price_info = StockPrice()

        try:
            # Use intelligent extractor for better reliability
            price_info.current_price = self.intelligent_extractor.extract_with_intelligence(
                driver, "price", "current_price", symbol)

            price_info.price_change = self.intelligent_extractor.extract_with_intelligence(
                driver, "price", "price_change", symbol)

            price_info.price_change_percent = self.intelligent_extractor.extract_with_intelligence(
                driver, "price", "price_change_percent", symbol)

            price_info.previous_close = self.intelligent_extractor.extract_with_intelligence(
                driver, "price", "previous_close", symbol)

            price_info.open_price = self.intelligent_extractor.extract_with_intelligence(
                driver, "price", "open_price", symbol)

            # Day range - try intelligent extraction first, then fallback
            day_range = self._get_element_text(driver, "[data-testid='DAYS_RANGE-value']")
            if day_range and ' - ' in day_range:
                low, high = day_range.split(' - ')
                price_info.day_low = clean_numeric_value(low)
                price_info.day_high = clean_numeric_value(high)

            # 52-week range
            week_range = self._get_element_text(driver, "[data-testid='FIFTY_TWO_WK_RANGE-value']")
            if week_range and ' - ' in week_range:
                low, high = week_range.split(' - ')
                price_info.week_52_low = clean_numeric_value(low)
                price_info.week_52_high = clean_numeric_value(high)

        except Exception as e:
            logger.warning(f"Error extracting price info: {str(e)}")

        return price_info

    def _extract_trading_metrics(self, driver) -> TradingMetrics:
        """Extract trading metrics using intelligent extraction"""
        metrics = TradingMetrics()

        try:
            # Use intelligent extractor for better reliability
            volume = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "volume")
            metrics.volume = volume

            avg_volume = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "avg_volume")
            metrics.avg_volume = avg_volume

            market_cap = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "market_cap")
            metrics.market_cap = market_cap

        except Exception as e:
            logger.warning(f"Error extracting trading metrics: {str(e)}")

        return metrics

    def _extract_financial_ratios(self, driver) -> FinancialRatios:
        """Extract financial ratios using intelligent extraction"""
        ratios = FinancialRatios()

        try:
            # Use intelligent extractor for better reliability
            ratios.pe_ratio = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "pe_ratio")

            ratios.eps = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "eps")

            ratios.beta = self.intelligent_extractor.extract_with_intelligence(
                driver, "financial_metrics", "beta")

            # Dividend yield - special handling for format like "0.52 (0.47%)"
            dividend = self._get_element_text(driver, "[data-testid='DIVIDEND_AND_YIELD-value']")
            if dividend and '(' in dividend:
                yield_match = re.search(r'\(([\d.]+)%\)', dividend)
                if yield_match:
                    ratios.dividend_yield = float(yield_match.group(1))

        except Exception as e:
            logger.warning(f"Error extracting financial ratios: {str(e)}")

        return ratios

    def _extract_company_info(self, driver, symbol: str) -> CompanyInfo:
        """Extract company information using intelligent extraction"""
        try:
            # Use intelligent extractor for company name
            company_name = self.intelligent_extractor.extract_with_intelligence(
                driver, "company_info", "company_name", symbol)

            if not company_name:
                # Fallback to basic extraction
                name_element = driver.find_element(By.CSS_SELECTOR, "h1")
                company_name = name_element.text.split('(')[0].strip() if name_element else symbol

            return CompanyInfo(
                symbol=symbol,
                company_name=company_name or symbol
            )

        except Exception as e:
            logger.warning(f"Error extracting company info: {str(e)}")
            return CompanyInfo(symbol=symbol, company_name=symbol)

    def _extract_price_info_from_soup(self, soup, symbol: str) -> StockPrice:
        """Extract price information from BeautifulSoup"""
        price_info = StockPrice()

        try:
            # Try to find price elements in the HTML
            price_elements = soup.find_all(attrs={"data-symbol": symbol})

            for element in price_elements:
                field = element.get("data-field", "")
                if field == "regularMarketPrice":
                    price_info.current_price = clean_numeric_value(element.text)
                elif field == "regularMarketChange":
                    price_info.price_change = clean_numeric_value(element.text)
                elif field == "regularMarketChangePercent":
                    price_info.price_change_percent = clean_numeric_value(element.text.replace('%', ''))

            # Extract other price data from table rows
            self._extract_summary_data_from_soup(soup, price_info)

        except Exception as e:
            logger.warning(f"Error extracting price info from soup: {str(e)}")

        return price_info

    def _extract_trading_metrics_from_soup(self, soup) -> TradingMetrics:
        """Extract trading metrics from BeautifulSoup"""
        metrics = TradingMetrics()

        try:
            # Look for data-testid attributes
            volume_elem = soup.find(attrs={"data-testid": "TD_VOLUME-value"})
            if volume_elem:
                metrics.volume = self._parse_volume(volume_elem.text)

            avg_volume_elem = soup.find(attrs={"data-testid": "AVERAGE_VOLUME_3MONTH-value"})
            if avg_volume_elem:
                metrics.avg_volume = self._parse_volume(avg_volume_elem.text)

            market_cap_elem = soup.find(attrs={"data-testid": "MARKET_CAP-value"})
            if market_cap_elem:
                metrics.market_cap = market_cap_elem.text

        except Exception as e:
            logger.warning(f"Error extracting trading metrics from soup: {str(e)}")

        return metrics

    def _extract_financial_ratios_from_soup(self, soup) -> FinancialRatios:
        """Extract financial ratios from BeautifulSoup"""
        ratios = FinancialRatios()

        try:
            # P/E ratio
            pe_elem = soup.find(attrs={"data-testid": "PE_RATIO-value"})
            if pe_elem:
                ratios.pe_ratio = clean_numeric_value(pe_elem.text)

            # EPS
            eps_elem = soup.find(attrs={"data-testid": "EPS_RATIO-value"})
            if eps_elem:
                ratios.eps = clean_numeric_value(eps_elem.text)

            # Beta
            beta_elem = soup.find(attrs={"data-testid": "BETA_5Y-value"})
            if beta_elem:
                ratios.beta = clean_numeric_value(beta_elem.text)

        except Exception as e:
            logger.warning(f"Error extracting financial ratios from soup: {str(e)}")

        return ratios

    def _extract_company_info_from_soup(self, soup, symbol: str) -> CompanyInfo:
        """Extract company information from BeautifulSoup"""
        try:
            # Company name from h1 tag
            h1_elem = soup.find("h1")
            company_name = h1_elem.text.split('(')[0].strip() if h1_elem else symbol

            return CompanyInfo(
                symbol=symbol,
                company_name=company_name
            )

        except Exception as e:
            logger.warning(f"Error extracting company info from soup: {str(e)}")
            return CompanyInfo(symbol=symbol, company_name=symbol)

    def _extract_summary_data_from_soup(self, soup, price_info: StockPrice):
        """Extract additional price data from summary table"""
        try:
            # Look for table rows with financial data
            rows = soup.find_all("tr")

            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    label = cells[0].text.strip().lower()
                    value = cells[1].text.strip()

                    if "previous close" in label:
                        price_info.previous_close = clean_numeric_value(value)
                    elif "open" in label:
                        price_info.open_price = clean_numeric_value(value)
                    elif "day's range" in label or "day range" in label:
                        if ' - ' in value:
                            low, high = value.split(' - ')
                            price_info.day_low = clean_numeric_value(low)
                            price_info.day_high = clean_numeric_value(high)
                    elif "52 week range" in label or "52-week range" in label:
                        if ' - ' in value:
                            low, high = value.split(' - ')
                            price_info.week_52_low = clean_numeric_value(low)
                            price_info.week_52_high = clean_numeric_value(high)

        except Exception as e:
            logger.warning(f"Error extracting summary data: {str(e)}")

    def _get_element_text(self, driver, selector: str) -> Optional[str]:
        """Safely get text from an element"""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except (NoSuchElementException, TimeoutException):
            return None

    def _parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume string (e.g., '1.2M' -> 1200000)"""
        if not volume_str:
            return None

        try:
            # Remove commas and convert
            volume_str = volume_str.replace(',', '').upper()

            if 'K' in volume_str:
                return int(float(volume_str.replace('K', '')) * 1000)
            elif 'M' in volume_str:
                return int(float(volume_str.replace('M', '')) * 1000000)
            elif 'B' in volume_str:
                return int(float(volume_str.replace('B', '')) * 1000000000)
            else:
                return int(float(volume_str))

        except (ValueError, TypeError):
            return None
