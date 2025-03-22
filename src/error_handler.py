import time
from typing import Callable, Optional, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, WebDriverException, NoSuchElementException
)


class ErrorHandler:
    """
    Handles errors, CAPTCHAs, and rate limiting for the Google Maps scraper.
    """
    
    def __init__(self, driver: webdriver.Remote, change_proxy_callback: Callable, report_proxy_error_callback: Callable):
        """
        Initialize the error handler.
        
        Args:
            driver: Selenium webdriver instance
            change_proxy_callback: Callback function to change the proxy
            report_proxy_error_callback: Callback function to report a proxy error
        """
        self.driver = driver
        self.change_proxy = change_proxy_callback
        self.report_proxy_error = report_proxy_error_callback
        self.hacker_messages = [
            "[ ALERT ] Breaking through firewall barriers...",
            "[ ALERT ] Evading neural network detection systems...",
            "[ ALERT ] Bypassing quantum encryption protocols...",
            "[ ALERT ] Rerouting through cybernetic nodes...",
            "[ ALERT ] Deploying stealth algorithms...",
            "[ ALERT ] Initiating ghost protocol...",
            "[ ALERT ] Activating digital camouflage...",
            "[ ALERT ] Implementing counter-surveillance measures...",
            "[ ALERT ] Triggering system override procedures...",
            "[ ALERT ] Engaging neural interface bypass...",
        ]
    
    def get_random_hacker_message(self) -> str:
        """Returns a random retro hacker message."""
        import random
        return random.choice(self.hacker_messages)
    
    def is_captcha_present(self) -> bool:
        """
        Check if a CAPTCHA is present on the page.
        
        Returns:
            True if CAPTCHA is detected, False otherwise
        """
        captcha_indicators = [
            # Google reCAPTCHA indicators
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[contains(@class, 'recaptcha')]",
            # Text indicators
            "//*[contains(text(), 'captcha') or contains(text(), 'CAPTCHA')]",
            "//*[contains(text(), 'unusual traffic') or contains(text(), 'suspicious activity')]",
            # Google captcha specific elements
            "//form[@action='https://www.google.com/search']//div[@id='captcha-form']",
            "//div[@id='recaptcha']"
        ]
        
        for indicator in captcha_indicators:
            try:
                element = self.driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        return False
    
    def is_rate_limited(self) -> bool:
        """
        Check if the page shows signs of rate limiting or blocking.
        
        Returns:
            True if rate limiting is detected, False otherwise
        """
        rate_limit_indicators = [
            # Text patterns for rate limiting
            "//*[contains(text(), 'rate limit') or contains(text(), 'too many requests')]",
            "//*[contains(text(), 'temporarily blocked') or contains(text(), 'access denied')]",
            "//*[contains(text(), 'unusual traffic from your computer')]",
            # Google specific rate limiting messages
            "//*[contains(text(), 'Our systems have detected unusual traffic')]",
            # General error page indicators
            "//title[contains(text(), '429') or contains(text(), 'Too Many Requests')]",
            "//h1[contains(text(), '429') or contains(text(), 'Too Many Requests')]"
        ]
        
        for indicator in rate_limit_indicators:
            try:
                element = self.driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    return True
            except NoSuchElementException:
                continue
        
        # Check HTTP status code (may not work for all browsers)
        try:
            script = "return window.performance.getEntries().filter(e => e.name.includes('google.com/maps')).pop().responseStatus"
            status = self.driver.execute_script(script)
            if status and status in [429, 403, 503]:
                return True
        except Exception:
            pass
        
        return False
    
    def check_page_errors(self, current_proxy: Dict[str, str]) -> bool:
        """
        Check for various error conditions on the page.
        
        Args:
            current_proxy: The current proxy being used
            
        Returns:
            True if any error condition is detected and handled, False otherwise
        """
        # Check for CAPTCHA
        if self.is_captcha_present():
            print(f"{self.get_random_hacker_message()}")
            print("[ SECURITY ] CAPTCHA defense system detected! Switching digital identity...")
            self.report_proxy_error(current_proxy)
            self.change_proxy()
            return True
        
        # Check for rate limiting
        if self.is_rate_limited():
            print(f"{self.get_random_hacker_message()}")
            print("[ SECURITY ] Rate limiting countermeasures detected! Engaging stealth protocols...")
            self.report_proxy_error(current_proxy)
            self.change_proxy()
            return True
        
        # Check for general page load issues
        try:
            # Check if we're on Google Maps
            if "google.com/maps" not in self.driver.current_url:
                print(f"{self.get_random_hacker_message()}")
                print("[ SECURITY ] Digital perimeter breach! Not on target system. Possible redirection detected...")
                self.report_proxy_error(current_proxy)
                self.change_proxy()
                return True
            
            # Check if search results are present (when expected)
            if "/search" in self.driver.current_url:
                try:
                    # Check for a message indicating no results
                    no_results = self.driver.find_elements(
                        By.XPATH, "//*[contains(text(), 'No results found')]"
                    )
                    if no_results and any(e.is_displayed() for e in no_results):
                        # This is not an error, just no results
                        return False
                    
                    # Check if results feed is present
                    results = self.driver.find_elements(By.CSS_SELECTOR, "div[role='feed']")
                    if not results or not any(e.is_displayed() for e in results):
                        print(f"{self.get_random_hacker_message()}")
                        print("[ SECURITY ] Data stream blockage detected! Deploying counter-measures...")
                        self.report_proxy_error(current_proxy)
                        self.change_proxy()
                        return True
                except NoSuchElementException:
                    pass
        except Exception as e:
            print(f"[ ERROR ] System integrity breach: {e}")
        
        return False
    
    def handle_timeout(self, url: str, current_proxy: Dict[str, str], retry_count: int = 0, max_retries: int = 3) -> bool:
        """
        Handle timeout errors by retrying with exponential backoff.
        
        Args:
            url: URL that timed out
            current_proxy: The current proxy being used
            retry_count: Current retry attempt
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful after retries, False if max retries exceeded
        """
        if retry_count >= max_retries:
            print(f"[ SYSTEM ] Maximum retry attempts ({max_retries}) exceeded for target: {url}")
            self.report_proxy_error(current_proxy)
            return False
        
        # Exponential backoff
        wait_time = 2 ** retry_count
        print(f"{self.get_random_hacker_message()}")
        print(f"[ SYSTEM ] Connection timeout. Initiating quantum recalibration in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
        time.sleep(wait_time)
        
        try:
            self.driver.get(url)
            return True
        except TimeoutException:
            return self.handle_timeout(url, current_proxy, retry_count + 1, max_retries)
        except WebDriverException as e:
            print(f"[ ERROR ] Network protocol disruption: {e}")
            self.report_proxy_error(current_proxy)
            self.change_proxy()
            return False
    
    def slow_down_if_needed(self, error_count: int) -> None:
        """
        Slow down scraping rate if errors are being encountered.
        
        Args:
            error_count: Number of errors encountered recently
        """
        if error_count > 2:
            # Exponential backoff based on error count
            delay = min(30, 5 * (2 ** (error_count - 2)))
            print(f"{self.get_random_hacker_message()}")
            print(f"[ SYSTEM ] Defense grid resistance increasing. Cooling system for {delay} seconds to avoid detection...")
            time.sleep(delay)
