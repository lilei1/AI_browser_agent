"""
Browser management for Yahoo Finance Agent
"""
import os
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc  # Not available in Python 3.7
from loguru import logger

from config import settings

class BrowserManager:
    """
    Manages browser instances for web scraping with anti-detection features
    """
    
    def __init__(self, headless: bool = None, use_undetected: bool = False):
        """
        Initialize browser manager

        Args:
            headless: Run browser in headless mode (default from settings)
            use_undetected: Use undetected-chromedriver for better anti-detection (disabled for Python 3.7)
        """
        self.headless = headless if headless is not None else settings.browser_headless
        self.use_undetected = use_undetected and False  # Disabled for Python 3.7 compatibility
        self.driver: Optional[webdriver.Chrome] = None
        self._setup_complete = False
        
    def setup_driver(self) -> webdriver.Chrome:
        """
        Set up and configure Chrome driver with optimal settings
        
        Returns:
            Configured Chrome WebDriver instance
        """
        try:
            # Always use regular Chrome for Python 3.7 compatibility
            driver = self._setup_regular_chrome()
            
            # Configure timeouts
            driver.implicitly_wait(settings.implicit_wait)
            driver.set_page_load_timeout(settings.page_load_timeout)
            
            # Set window size for consistent rendering
            if not self.headless:
                driver.set_window_size(1920, 1080)
            
            self.driver = driver
            self._setup_complete = True
            logger.success("Browser driver setup completed successfully")
            
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup browser driver: {str(e)}")
            raise
    
    def _setup_undetected_chrome(self) -> webdriver.Chrome:
        """Setup undetected Chrome driver - disabled for Python 3.7 compatibility"""
        logger.warning("Undetected Chrome not available in Python 3.7. Using regular Chrome.")
        return self._setup_regular_chrome()
    
    def _setup_regular_chrome(self) -> webdriver.Chrome:
        """Setup regular Chrome driver"""
        options = Options()
        
        # Basic options
        if self.headless:
            options.add_argument('--headless')
        
        # Standard options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--window-size=1920,1080')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Setup service
        service = Service(ChromeDriverManager().install())
        
        return webdriver.Chrome(service=service, options=options)
    
    def get_driver(self) -> webdriver.Chrome:
        """
        Get the current driver instance, setting it up if necessary
        
        Returns:
            Chrome WebDriver instance
        """
        if not self.driver or not self._setup_complete:
            return self.setup_driver()
        
        return self.driver
    
    def navigate_to_url(self, url: str, wait_for_element: str = None) -> bool:
        """
        Navigate to a URL and optionally wait for an element
        
        Args:
            url: URL to navigate to
            wait_for_element: CSS selector to wait for (optional)
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            driver = self.get_driver()
            logger.info(f"Navigating to: {url}")
            
            driver.get(url)
            
            # Wait for specific element if provided
            if wait_for_element:
                WebDriverWait(driver, settings.page_load_timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                )
            
            # Add small delay for page stability
            time.sleep(2)
            
            logger.success(f"Successfully navigated to: {url}")
            return True
            
        except TimeoutException:
            logger.error(f"Timeout waiting for page to load: {url}")
            return False
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False
    
    def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """
        Wait for an element to be present
        
        Args:
            selector: CSS selector for the element
            timeout: Timeout in seconds (default from settings)
            
        Returns:
            True if element found, False otherwise
        """
        try:
            timeout = timeout or settings.page_load_timeout
            driver = self.get_driver()
            
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
            
        except TimeoutException:
            logger.warning(f"Element not found within {timeout}s: {selector}")
            return False
    
    def scroll_to_bottom(self, pause_time: float = 1.0):
        """
        Scroll to bottom of page to load dynamic content
        
        Args:
            pause_time: Time to pause between scrolls
        """
        try:
            driver = self.get_driver()
            
            # Get initial height
            last_height = driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # Scroll down to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                time.sleep(pause_time)
                
                # Calculate new scroll height
                new_height = driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except Exception as e:
            logger.warning(f"Error during scrolling: {str(e)}")
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """
        Take a screenshot of the current page
        
        Args:
            filename: Optional filename for the screenshot
            
        Returns:
            Path to the screenshot file or None if failed
        """
        try:
            driver = self.get_driver()
            
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(settings.data_dir, filename)
            driver.save_screenshot(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def close(self):
        """Close the browser and clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {str(e)}")
            finally:
                self.driver = None
                self._setup_complete = False
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
