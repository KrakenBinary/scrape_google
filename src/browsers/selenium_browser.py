"""
Selenium Browser Module for web scraping.
This module provides a Selenium-based browser implementation.
"""
import os
import time
import json
import random
import logging
import tempfile
import subprocess
from typing import Dict, Optional, List, Any, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Try to import undetected_chromedriver for better anti-bot detection
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    logging.warning("undetected_chromedriver not available. Using standard ChromeDriver.")

from .base import BaseBrowser

class SeleniumBrowser(BaseBrowser):
    """
    Selenium-based browser implementation for web scraping.
    Supports both regular ChromeDriver and undetected_chromedriver for better bot detection avoidance.
    """
    
    def __init__(self):
        """Initialize the Selenium browser"""
        super().__init__()
        self.driver = None
        self.temp_dir = tempfile.mkdtemp()  # Create a temp directory immediately
        self.user_agent = None
        self.proxy = None
        self.headless = False
        self.initialized = False
    
    def _generate_user_agent(self) -> str:
        """Get a random user agent string"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        ]
        return random.choice(user_agents)
    
    def initialize(self, headless: bool = False, browser_type: str = "chrome", 
                  chrome_arguments: Optional[Dict[str, str]] = None, 
                  proxy: Optional[Union[str, Dict[str, str]]] = None) -> bool:
        """
        Initialize the Selenium browser.
        
        Args:
            headless: Run browser in headless mode (no GUI)
            browser_type: Type of browser to use ('chrome' or 'firefox')
            chrome_arguments: Additional Chrome arguments
            proxy: Proxy configuration (string 'host:port' or dict with 'http'/'https' keys)
            
        Returns:
            bool: True if initialization successful
        """
        # Create a temporary directory if it doesn't exist
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)
            
        # Set up user agent
        self.user_agent = self._generate_user_agent()
        
        # Set up proxy if provided
        if proxy:
            chrome_arguments = chrome_arguments or {}
            
            if isinstance(proxy, str):
                chrome_arguments["proxy-server"] = proxy
            elif isinstance(proxy, dict):
                # Handle more complex proxy configurations
                if "http" in proxy:
                    chrome_arguments["proxy-server"] = proxy["http"]
                elif "https" in proxy:
                    chrome_arguments["proxy-server"] = proxy["https"]
                    
        # Initialize the browser
        if browser_type.lower() == "chrome":
            success = self._initialize_chrome(headless, chrome_arguments)
        elif browser_type.lower() == "firefox":
            logging.warning("Firefox not fully implemented yet, using Chrome")
            success = self._initialize_chrome(headless, chrome_arguments)
        else:
            logging.error(f"Unsupported browser type: {browser_type}")
            return False
            
        if success:
            self.initialized = True
            logging.info(f"Browser initialized successfully (headless: {headless})")
            return True
        else:
            logging.error("Failed to initialize browser")
            return False
    
    def _initialize_chrome(self, headless: bool = False, chrome_arguments: Optional[Dict[str, str]] = None) -> bool:
        """Initialize Chrome browser"""
        try:
            options = webdriver.ChromeOptions()
            
            # Essential options for stability
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            # Linux-specific rendering fixes for glitchy windows
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-accelerated-2d-canvas")
            options.add_argument("--disable-accelerated-video-decode")
            options.add_argument("--disable-webgl")
            
            # Enable software rendering mode - often helps with Linux display issues
            options.add_argument("--use-gl=swiftshader")
            options.add_argument("--use-angle=swiftshader")
            
            # Window settings
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
            
            # User agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")
            
            # Disable automation flags
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Disable unnecessary extensions/features for better performance
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            # Add additional chrome arguments if provided
            if chrome_arguments:
                for key, value in chrome_arguments.items():
                    if value:
                        options.add_argument(f"--{key}={value}")
                    else:
                        options.add_argument(f"--{key}")
            
            # Try to use undetected_chromedriver if available
            try:
                if headless:
                    options.add_argument("--headless=new")
                
                self.driver = uc.Chrome(
                    options=options,
                    driver_executable_path=None,
                    version_main=None  # Auto-detect Chrome version
                )
                logging.info("Using undetected-chromedriver for better anti-bot detection")
            except Exception as e:
                logging.warning("undetected_chromedriver not available. Using standard ChromeDriver.")
                
                # Fallback to standard Chrome
                options.add_argument("--disable-blink-features=AutomationControlled")
                
                if headless:
                    options.add_argument("--headless=new")
                    
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=options)
            
            # Explicitly set window size for better visualization
            if not headless:
                self.driver.maximize_window()
                self.driver.set_window_position(0, 0)  # Position window at top-left corner
            
            # Set page load timeout
            self.driver.set_page_load_timeout(60)
            
            return True
            
        except Exception as e:
            logging.error(f"Error initializing Chrome: {str(e)}")
            return False
    
    def navigate(self, url: str, timeout: int = 30) -> bool:
        """Navigate to the specified URL"""
        if not self.initialized or not self.driver:
            logging.error("Browser not initialized. Call initialize() first.")
            return False
        
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logging.error(f"Error navigating to {url}: {str(e)}")
            return False
    
    def get_page_source(self) -> str:
        """Get the current page source"""
        if not self.initialized or not self.driver:
            logging.error("Browser not initialized. Call initialize() first.")
            return ""
        
        try:
            return self.driver.page_source
        except Exception as e:
            logging.error(f"Error getting page source: {str(e)}")
            return ""
    
    def execute_script(self, script: str, *args) -> Any:
        """
        Execute JavaScript in the browser.
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the script
            
        Returns:
            The result of the script execution
        """
        if not self.driver:
            logging.error("Browser not initialized")
            return None
            
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logging.error(f"Error executing script: {str(e)}")
            return None
    
    def wait_for_element(self, selector: str, by: str = "css", timeout: int = 10) -> Optional[Any]:
        """
        Wait for an element to be present on the page and return it.
        
        Args:
            selector: Element selector
            by: Selector type (css, xpath, id, class)
            timeout: Maximum time to wait in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        if not self.driver:
            logging.error("Browser not initialized")
            return None
        
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "name": By.NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_type, selector))
            )
            return element
            
        except TimeoutException:
            logging.warning(f"Timeout waiting for element: {selector}")
            return None
        except Exception as e:
            logging.error(f"Error waiting for element: {str(e)}")
            return None
    
    def cleanup(self) -> None:
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.warning(f"Error quitting driver: {str(e)}")
        
        # Clean up temporary directory
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logging.warning(f"Error cleaning up temporary directory: {str(e)}")
        
        self.initialized = False
        self.driver = None

    # Implement required abstract methods
    def click(self, element_or_selector: Any) -> bool:
        """
        Click on an element or selector.
        
        Args:
            element_or_selector: Element or CSS selector string
            
        Returns:
            bool: True if click was successful
        """
        try:
            if isinstance(element_or_selector, str):
                element = self.find_element(element_or_selector)
                if not element:
                    return False
            else:
                element = element_or_selector
                
            # Try to scroll element into view before clicking
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # Small delay after scrolling
            except Exception:
                pass
                
            element.click()
            return True
        except Exception as e:
            logging.error(f"Error clicking element: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the browser and clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")
        finally:
            self.driver = None
            self.initialized = False
            
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    import shutil
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                except Exception:
                    pass
                self.temp_dir = None
    
    def find_element(self, selector: str, by_type: str = "css") -> Optional[Any]:
        """
        Find a single element using the specified selector.
        
        Args:
            selector: The selector string
            by_type: The selector type (css, xpath, id, class_name)
            
        Returns:
            The found element or None
        """
        if not self.driver:
            return None
            
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "class_name": By.CLASS_NAME,
                "name": By.NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT
            }
            
            by_method = by_map.get(by_type.lower(), By.CSS_SELECTOR)
            element = self.driver.find_element(by_method, selector)
            return element
        except Exception as e:
            logging.debug(f"Element not found: {selector} (by: {by_type})")
            return None
    
    def find_elements(self, selector: str, by_type: str = "css") -> List[Any]:
        """
        Find multiple elements using the specified selector.
        
        Args:
            selector: The selector string
            by_type: The selector type (css, xpath, id, class_name)
            
        Returns:
            List of found elements (empty list if none found)
        """
        if not self.driver:
            return []
            
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "class_name": By.CLASS_NAME,
                "name": By.NAME,
                "tag": By.TAG_NAME,
                "link_text": By.LINK_TEXT,
                "partial_link_text": By.PARTIAL_LINK_TEXT
            }
            
            by_method = by_map.get(by_type.lower(), By.CSS_SELECTOR)
            elements = self.driver.find_elements(by_method, selector)
            return elements
        except Exception as e:
            logging.debug(f"Elements not found: {selector} (by: {by_type})")
            return []
    
    def get_attribute(self, element_or_selector: Any, attribute: str) -> Optional[str]:
        """
        Get an attribute from an element.
        
        Args:
            element_or_selector: Element or selector string
            attribute: Attribute name to get
            
        Returns:
            Attribute value or None
        """
        try:
            element = element_or_selector
            if isinstance(element_or_selector, str):
                element = self.find_element(element_or_selector)
                
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logging.error(f"Error getting attribute: {str(e)}")
            return None
    
    def get_text(self, element_or_selector: Any) -> Optional[str]:
        """
        Get text content from an element.
        
        Args:
            element_or_selector: Element or selector string
            
        Returns:
            Text content or None
        """
        try:
            element = element_or_selector
            if isinstance(element_or_selector, str):
                element = self.find_element(element_or_selector)
                
            if element:
                return element.text
            return None
        except Exception as e:
            logging.error(f"Error getting text: {str(e)}")
            return None
    
    def scroll(self, direction: str = "down", amount: int = 500) -> None:
        """
        Scroll the page.
        
        Args:
            direction: Direction to scroll (down, up, left, right)
            amount: Amount to scroll in pixels
        """
        if not self.driver:
            return
            
        try:
            if direction.lower() == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction.lower() == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction.lower() == "right":
                self.driver.execute_script(f"window.scrollBy({amount}, 0);")
            elif direction.lower() == "left":
                self.driver.execute_script(f"window.scrollBy(-{amount}, 0);")
            elif direction.lower() == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            elif direction.lower() == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
        except Exception as e:
            logging.error(f"Error scrolling: {str(e)}")
    
    def send_keys(self, element_or_selector: Any, text: str) -> bool:
        """
        Send keystrokes to an element.
        
        Args:
            element_or_selector: Element or selector string
            text: Text to type
            
        Returns:
            bool: True if successful
        """
        try:
            element = element_or_selector
            if isinstance(element_or_selector, str):
                element = self.find_element(element_or_selector)
                
            if element:
                element.send_keys(text)
                return True
            return False
        except Exception as e:
            logging.error(f"Error sending keys: {str(e)}")
            return False
