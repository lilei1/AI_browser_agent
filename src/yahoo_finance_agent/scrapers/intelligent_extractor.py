"""
Intelligent data extraction strategies with AI-powered adaptability
"""
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from loguru import logger

from ..utils.helpers import clean_numeric_value, extract_numeric_from_text
from config import YAHOO_FINANCE_CONFIG

class IntelligentExtractor:
    """
    AI-powered intelligent data extraction with adaptive strategies
    """
    
    def __init__(self, browser_manager=None):
        """Initialize intelligent extractor"""
        self.browser_manager = browser_manager
        self.extraction_strategies = self._initialize_strategies()
        self.fallback_selectors = self._initialize_fallback_selectors()
        self.success_cache = {}  # Cache successful selectors
        
    def _initialize_strategies(self) -> Dict[str, List[str]]:
        """Initialize extraction strategies for different data types"""
        return {
            "price": [
                "css_selector_primary",
                "css_selector_fallback", 
                "xpath_search",
                "text_pattern_matching",
                "table_data_extraction",
                "json_data_extraction"
            ],
            "company_info": [
                "header_extraction",
                "meta_data_extraction",
                "structured_data_extraction",
                "text_analysis"
            ],
            "financial_metrics": [
                "table_extraction",
                "data_attribute_extraction",
                "pattern_matching",
                "contextual_extraction"
            ]
        }
    
    def _initialize_fallback_selectors(self) -> Dict[str, List[str]]:
        """Initialize fallback selectors for different data points"""
        return {
            "current_price": [
                "[data-symbol='AAPL'][data-field='regularMarketPrice']",
                "[data-testid='qsp-price']",
                ".Trsdu\\(0\\.3s\\).Fw\\(b\\).Fz\\(36px\\).Mb\\(-4px\\).D\\(ib\\)",
                "fin-streamer[data-field='regularMarketPrice']",
                ".Fw\\(b\\).Fz\\(36px\\)",
                "span[data-reactid*='price']",
                ".price",
                "[class*='price']"
            ],
            "company_name": [
                "h1[data-reactid]",
                "h1",
                ".D\\(ib\\).Mt\\(5px\\)",
                "[data-testid='qsp-header']",
                ".company-name",
                "[class*='company']",
                "[class*='name']"
            ],
            "market_cap": [
                "[data-testid='MARKET_CAP-value']",
                "td[data-test='MARKET_CAP-value']",
                "[aria-label*='Market Cap']",
                "span:contains('Market Cap')",
                ".market-cap"
            ],
            "pe_ratio": [
                "[data-testid='PE_RATIO-value']",
                "td[data-test='PE_RATIO-value']",
                "[aria-label*='PE Ratio']",
                "span:contains('P/E')",
                ".pe-ratio"
            ]
        }
    
    def extract_with_intelligence(self, driver, data_type: str, field: str, 
                                symbol: str = "AAPL") -> Optional[Any]:
        """
        Intelligently extract data using multiple strategies
        
        Args:
            driver: Selenium WebDriver instance
            data_type: Type of data to extract (price, company_info, financial_metrics)
            field: Specific field to extract
            symbol: Stock symbol
            
        Returns:
            Extracted value or None if all strategies fail
        """
        logger.info(f"Intelligently extracting {field} for {symbol}")
        
        # Check cache first
        cache_key = f"{symbol}_{field}"
        if cache_key in self.success_cache:
            try:
                result = self._extract_with_selector(driver, self.success_cache[cache_key])
                if result:
                    logger.debug(f"Cache hit for {field}: {result}")
                    return result
            except Exception:
                # Remove from cache if it fails
                del self.success_cache[cache_key]
        
        # Try strategies in order
        strategies = self.extraction_strategies.get(data_type, ["css_selector_primary"])
        
        for strategy in strategies:
            try:
                result = self._apply_strategy(driver, strategy, field, symbol)
                if result:
                    # Cache successful selector if applicable
                    if hasattr(self, '_last_successful_selector'):
                        self.success_cache[cache_key] = self._last_successful_selector
                    
                    logger.success(f"Successfully extracted {field} using {strategy}: {result}")
                    return result
                    
            except Exception as e:
                logger.debug(f"Strategy {strategy} failed for {field}: {str(e)}")
                continue
        
        logger.warning(f"All strategies failed for {field}")
        return None
    
    def _apply_strategy(self, driver, strategy: str, field: str, symbol: str) -> Optional[Any]:
        """Apply specific extraction strategy"""
        
        if strategy == "css_selector_primary":
            return self._extract_with_primary_selectors(driver, field, symbol)
        
        elif strategy == "css_selector_fallback":
            return self._extract_with_fallback_selectors(driver, field)
        
        elif strategy == "xpath_search":
            return self._extract_with_xpath_search(driver, field)
        
        elif strategy == "text_pattern_matching":
            return self._extract_with_text_patterns(driver, field)
        
        elif strategy == "table_data_extraction":
            return self._extract_from_tables(driver, field)
        
        elif strategy == "json_data_extraction":
            return self._extract_from_json_data(driver, field)
        
        elif strategy == "header_extraction":
            return self._extract_from_headers(driver, field)
        
        elif strategy == "meta_data_extraction":
            return self._extract_from_metadata(driver, field)
        
        elif strategy == "structured_data_extraction":
            return self._extract_from_structured_data(driver, field)
        
        elif strategy == "contextual_extraction":
            return self._extract_with_context(driver, field)
        
        return None
    
    def _extract_with_primary_selectors(self, driver, field: str, symbol: str) -> Optional[Any]:
        """Extract using primary CSS selectors from config"""
        selectors = YAHOO_FINANCE_CONFIG["selectors"]
        
        if field in selectors:
            selector = selectors[field].replace("AAPL", symbol)
            return self._extract_with_selector(driver, selector)
        
        return None
    
    def _extract_with_fallback_selectors(self, driver, field: str) -> Optional[Any]:
        """Extract using fallback selectors"""
        fallback_selectors = self.fallback_selectors.get(field, [])
        
        for selector in fallback_selectors:
            try:
                result = self._extract_with_selector(driver, selector)
                if result:
                    self._last_successful_selector = selector
                    return result
            except Exception:
                continue
        
        return None
    
    def _extract_with_xpath_search(self, driver, field: str) -> Optional[Any]:
        """Extract using XPath searches"""
        xpath_patterns = {
            "current_price": [
                "//span[contains(@class, 'price')]",
                "//div[contains(@data-field, 'price')]",
                "//*[contains(text(), '$') and string-length(text()) < 20]"
            ],
            "company_name": [
                "//h1[contains(@class, 'company') or contains(@class, 'name')]",
                "//title",
                "//*[contains(@class, 'header')]//text()[string-length(.) > 3]"
            ]
        }
        
        patterns = xpath_patterns.get(field, [])
        
        for xpath in patterns:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for element in elements:
                    text = element.text.strip()
                    if text and self._validate_extracted_value(field, text):
                        return self._process_extracted_value(field, text)
            except Exception:
                continue
        
        return None
    
    def _extract_with_text_patterns(self, driver, field: str) -> Optional[Any]:
        """Extract using text pattern matching"""
        try:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            patterns = {
                "current_price": [
                    r'\$[\d,]+\.?\d*',
                    r'[\d,]+\.?\d*\s*USD',
                    r'Price:\s*\$?([\d,]+\.?\d*)'
                ],
                "market_cap": [
                    r'Market Cap[:\s]*\$?([\d.]+[BMK]?)',
                    r'Mkt Cap[:\s]*\$?([\d.]+[BMK]?)'
                ],
                "pe_ratio": [
                    r'P/E[:\s]*([\d.]+)',
                    r'PE Ratio[:\s]*([\d.]+)'
                ]
            }
            
            field_patterns = patterns.get(field, [])
            text_content = soup.get_text()
            
            for pattern in field_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    return self._process_extracted_value(field, matches[0])
            
        except Exception as e:
            logger.debug(f"Text pattern matching failed: {str(e)}")
        
        return None
    
    def _extract_from_tables(self, driver, field: str) -> Optional[Any]:
        """Extract data from HTML tables"""
        try:
            tables = driver.find_elements(By.TAG_NAME, "table")
            
            field_keywords = {
                "market_cap": ["market cap", "mkt cap"],
                "pe_ratio": ["p/e", "pe ratio", "price/earnings"],
                "eps": ["eps", "earnings per share"],
                "dividend_yield": ["dividend", "yield"],
                "beta": ["beta"],
                "volume": ["volume"],
                "previous_close": ["prev close", "previous close"]
            }
            
            keywords = field_keywords.get(field, [field.replace('_', ' ')])
            
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        label = cells[0].text.strip().lower()
                        value = cells[1].text.strip()
                        
                        for keyword in keywords:
                            if keyword in label:
                                processed_value = self._process_extracted_value(field, value)
                                if processed_value:
                                    return processed_value
            
        except Exception as e:
            logger.debug(f"Table extraction failed: {str(e)}")
        
        return None
    
    def _extract_from_json_data(self, driver, field: str) -> Optional[Any]:
        """Extract data from JSON embedded in page"""
        try:
            # Look for JSON data in script tags
            script_elements = driver.find_elements(By.TAG_NAME, "script")
            
            for script in script_elements:
                script_content = script.get_attribute("innerHTML")
                if script_content and "regularMarketPrice" in script_content:
                    # Try to extract JSON data
                    import json
                    
                    # Look for JSON patterns
                    json_matches = re.findall(r'\{[^{}]*"regularMarketPrice"[^{}]*\}', script_content)
                    
                    for match in json_matches:
                        try:
                            data = json.loads(match)
                            if field == "current_price" and "regularMarketPrice" in data:
                                return data["regularMarketPrice"]
                        except json.JSONDecodeError:
                            continue
            
        except Exception as e:
            logger.debug(f"JSON extraction failed: {str(e)}")
        
        return None
    
    def _extract_with_selector(self, driver, selector: str) -> Optional[str]:
        """Extract text using CSS selector"""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except (NoSuchElementException, TimeoutException):
            return None
    
    def _validate_extracted_value(self, field: str, value: str) -> bool:
        """Validate if extracted value is reasonable for the field"""
        if not value or value in ['N/A', '--', '']:
            return False
        
        # Field-specific validation
        if field in ["current_price", "previous_close", "open_price"]:
            # Should be a reasonable stock price (between $0.01 and $10,000)
            numeric_value = clean_numeric_value(value)
            return numeric_value and 0.01 <= numeric_value <= 10000
        
        elif field == "company_name":
            # Should be reasonable company name length
            return 2 <= len(value) <= 100 and not value.isdigit()
        
        elif field in ["pe_ratio", "eps", "beta"]:
            # Should be reasonable financial ratio
            numeric_value = clean_numeric_value(value)
            return numeric_value and -1000 <= numeric_value <= 1000
        
        return True
    
    def _process_extracted_value(self, field: str, value: str) -> Optional[Any]:
        """Process and convert extracted value to appropriate type"""
        if field in ["current_price", "previous_close", "open_price", "day_low", "day_high", 
                    "week_52_low", "week_52_high", "price_change", "pe_ratio", "eps", "beta"]:
            return clean_numeric_value(value)
        
        elif field in ["volume", "avg_volume"]:
            # Handle volume with K, M, B suffixes
            if 'K' in value.upper():
                base = clean_numeric_value(value.replace('K', '').replace('k', ''))
                return int(base * 1000) if base else None
            elif 'M' in value.upper():
                base = clean_numeric_value(value.replace('M', '').replace('m', ''))
                return int(base * 1000000) if base else None
            elif 'B' in value.upper():
                base = clean_numeric_value(value.replace('B', '').replace('b', ''))
                return int(base * 1000000000) if base else None
            else:
                return clean_numeric_value(value)
        
        elif field == "price_change_percent":
            # Remove % sign and convert
            cleaned = value.replace('%', '').replace('(', '').replace(')', '')
            if cleaned.startswith('+'):
                cleaned = cleaned[1:]
            return clean_numeric_value(cleaned)
        
        else:
            # Return as string for other fields
            return value.strip()
    
    def _extract_from_headers(self, driver, field: str) -> Optional[Any]:
        """Extract from page headers"""
        if field == "company_name":
            try:
                # Try different header selectors
                header_selectors = ["h1", "h2", ".header", "[class*='title']"]
                
                for selector in header_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 2 and not text.isdigit():
                            # Clean company name (remove ticker symbol in parentheses)
                            cleaned = re.sub(r'\s*\([^)]*\)\s*', '', text).strip()
                            if cleaned:
                                return cleaned
            except Exception:
                pass
        
        return None
    
    def _extract_from_metadata(self, driver, field: str) -> Optional[Any]:
        """Extract from page metadata"""
        try:
            # Check meta tags
            meta_elements = driver.find_elements(By.TAG_NAME, "meta")
            
            for meta in meta_elements:
                name = meta.get_attribute("name") or meta.get_attribute("property")
                content = meta.get_attribute("content")
                
                if name and content:
                    if field == "company_name" and "title" in name.lower():
                        return content.strip()
                    elif field == "current_price" and "price" in name.lower():
                        return clean_numeric_value(content)
        
        except Exception:
            pass
        
        return None
    
    def _extract_from_structured_data(self, driver, field: str) -> Optional[Any]:
        """Extract from structured data (JSON-LD, microdata)"""
        try:
            # Look for JSON-LD structured data
            json_ld_scripts = driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
            
            for script in json_ld_scripts:
                try:
                    import json
                    data = json.loads(script.get_attribute("innerHTML"))
                    
                    if isinstance(data, dict):
                        if field == "company_name" and "name" in data:
                            return data["name"]
                        elif field == "current_price" and "price" in data:
                            return clean_numeric_value(str(data["price"]))
                
                except (json.JSONDecodeError, KeyError):
                    continue
        
        except Exception:
            pass
        
        return None
    
    def _extract_with_context(self, driver, field: str) -> Optional[Any]:
        """Extract using contextual clues"""
        try:
            # Look for elements near labels
            label_patterns = {
                "current_price": ["price", "quote", "last"],
                "market_cap": ["market cap", "mkt cap"],
                "pe_ratio": ["p/e", "pe ratio"],
                "volume": ["volume", "vol"]
            }
            
            patterns = label_patterns.get(field, [])
            
            for pattern in patterns:
                # Find elements containing the pattern
                xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{pattern}')]"
                label_elements = driver.find_elements(By.XPATH, xpath)
                
                for label_element in label_elements:
                    # Look for nearby elements with values
                    parent = label_element.find_element(By.XPATH, "..")
                    value_elements = parent.find_elements(By.XPATH, ".//*[text()]")
                    
                    for value_element in value_elements:
                        text = value_element.text.strip()
                        if text != label_element.text.strip() and self._validate_extracted_value(field, text):
                            return self._process_extracted_value(field, text)
        
        except Exception:
            pass
        
        return None
