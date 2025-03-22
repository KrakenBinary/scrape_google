import os
import time
import random
from typing import Dict, Optional, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import fake_useragent with proper error handling
try:
    from fake_useragent import UserAgent
    ua_instance = UserAgent()
    ua_available = True
except Exception:
    ua_available = False
    # Fallback user agents if fake_useragent fails
    FALLBACK_USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]

# Import the centralized console output module
from src.console_output import (
    print_system_message, print_info_message, print_warning_message,
    print_error_message, print_success_message
)

class BrowserManager:
    """Manages browser instances with proxy configuration."""
    
    def __init__(self, headless: bool = False, browser_type: str = "chrome"):
        """
        Initialize the browser manager.
        
        Args:
            headless: Whether to run the browser in headless mode
            browser_type: Type of browser to use ('chrome' or 'firefox')
        """
        self.headless = headless
        self.browser_type = browser_type.lower()
        
        # Set user agent
        if ua_available:
            try:
                self.user_agent = ua_instance.random
            except Exception:
                self.user_agent = random.choice(FALLBACK_USER_AGENTS)
        else:
            self.user_agent = random.choice(FALLBACK_USER_AGENTS)
        
        # Check for Chromium
        self.chromium_path = self._find_chrome_binary()
    
    def get_browser(self, proxy: Optional[Dict[str, str]] = None) -> webdriver.Remote:
        """
        Initialize and return a browser instance with the specified configuration.
        
        Args:
            proxy: Optional proxy configuration dict ('http'/'https' keys or 'direct: True')
            
        Returns:
            Configured WebDriver instance
        """
        print_system_message("Initializing chrome browser...")
        
        # Check if we're using a direct connection (no proxy)
        using_direct_connection = proxy is not None and proxy.get('direct', False)
        
        # Log headless mode status
        if self.headless:
            print_info_message("Headless mode: ON")
        else:
            print_info_message("Headless mode: OFF")
            print_info_message("Running in visible mode (non-headless)")
        
        # Get appropriate WebDriver options
        options = self._get_browser_options(proxy)
        
        try:
            # Initialize the browser based on type
            if self.browser_type == "chrome":
                return self._get_chrome_browser(options, using_direct_connection)
            elif self.browser_type == "firefox":
                return self._get_firefox_browser(options, using_direct_connection)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")
        except Exception as e:
            print_error_message(f"Browser initialization failed: {str(e)}")
            raise
            
    def _get_chrome_browser(self, options, direct_connection: bool = False) -> webdriver.Chrome:
        """Initialize a Chrome browser with the specified options."""
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Check for Chrome/Chromium location
        chrome_path = self._find_chrome_binary()
        if chrome_path:
            print_info_message(f"Found Chromium at: {chrome_path}")
            options.binary_location = chrome_path
        
        # Configure proxy if specified
        if not direct_connection and options._proxy:
            print_system_message(f"Configuring Chrome/Chromium with proxy: {options._proxy}")
            
        # Set window position and size for better visibility
        if not self.headless:
            window_position = {
                "x": 10,
                "y": 10
            }
            window_size = {
                "width": 1366,
                "height": 768
            }
            options.add_argument(f"--window-position={window_position['x']},{window_position['y']}")
            options.add_argument(f"--window-size={window_size['width']},{window_size['height']}")
        
        # Initialize Chrome driver with error handling
        try:
            # Use ChromeDriverManager to automatically get the right chromedriver
            service = Service(ChromeDriverManager().install())
            
            # Start browser with the configured options
            if not self.headless:
                print_info_message("Starting Chrome browser with visible UI...")
                # Additional steps to ensure browser is visible
                options.add_argument("--start-maximized")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(service=service, options=options)
            
            # Explicitly set window size again after initialization
            if not self.headless:
                driver.set_window_size(window_size["width"], window_size["height"])
                driver.set_window_position(window_position["x"], window_position["y"])
                driver.execute_script("document.body.style.zoom='100%'")
                
            print_success_message("Chrome browser initialized successfully!")
            return driver
            
        except Exception as e:
            print_error_message(f"Chrome initialization error: {str(e)}")
            raise

    def _get_browser_options(self, proxy: Optional[Dict[str, str]] = None) -> Union[ChromeOptions, FirefoxOptions]:
        """
        Configure browser options based on the browser type and settings.
        
        Args:
            proxy: Optional proxy configuration
            
        Returns:
            Configured browser options object
        """
        if self.browser_type == "chrome":
            options = ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-popup-blocking")
            
            # Add user agent
            user_agent = self._get_user_agent()
            options.add_argument(f"--user-agent={user_agent}")
            
            # Configure headless mode
            if self.headless:
                options.add_argument("--headless=new")  # Modern Chrome headless mode
            
            # Check if using direct connection
            if proxy and proxy.get('direct', False):
                print_info_message("Using direct connection (no proxy)")
            # Add proxy if provided and not direct
            elif proxy and 'http' in proxy:
                proxy_server = proxy['http']
                if proxy_server.startswith('http://'):
                    proxy_server = proxy_server[7:]  # Remove http:// prefix
                
                options.add_argument(f"--proxy-server={proxy_server}")
                options._proxy = proxy_server  # Store for logging
            
            # Add preferences
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.geolocation": 2,  # 0=ask, 1=allow, 2=block
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            })
            
            # Disable automation flags
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            return options
            
        elif self.browser_type == "firefox":
            options = FirefoxOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            
            # Add user agent
            user_agent = self._get_user_agent()
            options.set_preference("general.useragent.override", user_agent)
            
            # Configure headless mode
            if self.headless:
                options.add_argument("--headless")
            
            # Add proxy if provided and not direct
            if proxy and not proxy.get('direct', False) and 'http' in proxy:
                proxy_server = proxy['http']
                if proxy_server.startswith('http://'):
                    proxy_server = proxy_server[7:]  # Remove http:// prefix
                
                host, port = proxy_server.split(':')
                options.set_preference("network.proxy.type", 1)
                options.set_preference("network.proxy.http", host)
                options.set_preference("network.proxy.http_port", int(port))
                options.set_preference("network.proxy.ssl", host)
                options.set_preference("network.proxy.ssl_port", int(port))
                options._proxy = proxy_server  # Store for logging
            
            # Disable automation flags
            options.set_preference("dom.webdriver.enabled", False)
            
            return options
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")

    def _find_chrome_binary(self) -> Optional[str]:
        """Find the Chrome or Chromium binary on the system."""
        possible_paths = [
            # Linux paths
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            # Add more paths as needed
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
                
        return None

    def close_browser(self, driver: webdriver.Remote) -> None:
        """
        Safely close a browser instance.
        
        Args:
            driver: Webdriver instance to close
        """
        try:
            driver.quit()
        except Exception as e:
            print_warning_message(f"Error closing browser: {e}")
