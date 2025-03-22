import random
import time
from typing import List, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class HumanBehavior:
    """Simulates human-like behavior in browser automation."""
    
    def __init__(self, driver: webdriver.Chrome):
        """
        Initialize with a webdriver instance.
        
        Args:
            driver: Selenium webdriver instance
        """
        self.driver = driver
        self.action_chains = ActionChains(driver)
    
    def random_delay(self, min_seconds: float = 1.0, max_seconds: float = 5.0) -> None:
        """
        Wait for a random period between min and max seconds.
        
        Args:
            min_seconds: Minimum wait time in seconds
            max_seconds: Maximum wait time in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_type(self, element: WebElement, text: str, min_delay: float = 0.1, max_delay: float = 0.3) -> None:
        """
        Type text into an element with random delays between keypresses.
        
        Args:
            element: WebElement to type into
            text: Text to type
            min_delay: Minimum delay between keypresses in seconds
            max_delay: Maximum delay between keypresses in seconds
        """
        element.clear()
        for char in text:
            element.send_keys(char)
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
        
        # Add a final delay before pressing Enter
        self.random_delay(0.5, 1.5)
        element.send_keys(Keys.RETURN)
    
    def human_click(self, element: WebElement, offset_range: int = 50) -> None:
        """
        Click an element with human-like behavior by moving to a random position
        within the element first.
        
        Args:
            element: WebElement to click
            offset_range: Range for random offsets in pixels
        """
        # Get element dimensions
        size = element.size
        width, height = size['width'], size['height']
        
        # Calculate random offset from center (but ensure we stay within the element)
        x_offset = random.randint(-min(offset_range, width // 2), min(offset_range, width // 2))
        y_offset = random.randint(-min(offset_range, height // 2), min(offset_range, height // 2))
        
        # Move to random position within element and click
        try:
            self.action_chains.move_to_element(element).move_by_offset(x_offset, y_offset).click().perform()
        except Exception:
            # Fallback to regular click if ActionChains fails
            element.click()
    
    def human_scroll(self, scroll_amount: Optional[int] = None, direction: str = "down") -> None:
        """
        Scroll the page like a human would.
        
        Args:
            scroll_amount: Amount to scroll in pixels, random if None
            direction: 'up' or 'down'
        """
        if scroll_amount is None:
            scroll_amount = random.randint(300, 700)
        
        if direction == "up":
            scroll_amount = -scroll_amount
        
        # Split scroll into several smaller scrolls
        num_steps = random.randint(3, 7)
        scroll_step = scroll_amount // num_steps
        
        for _ in range(num_steps):
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            self.random_delay(0.1, 0.3)
    
    def random_mouse_movement(self, num_movements: int = 3) -> None:
        """
        Move the mouse to random positions on the screen.
        
        Args:
            num_movements: Number of random movements to make
        """
        # Get viewport dimensions
        viewport_width = self.driver.execute_script("return window.innerWidth;")
        viewport_height = self.driver.execute_script("return window.innerHeight;")
        
        for _ in range(num_movements):
            x = random.randint(0, viewport_width)
            y = random.randint(0, viewport_height)
            
            self.action_chains.move_by_offset(x, y).perform()
            self.random_delay(0.1, 0.5)
    
    def hover_over_element(self, element: WebElement, hover_time: Optional[float] = None) -> None:
        """
        Hover over an element for a random amount of time.
        
        Args:
            element: WebElement to hover over
            hover_time: Time to hover in seconds, random if None
        """
        if hover_time is None:
            hover_time = random.uniform(0.5, 2.0)
        
        try:
            self.action_chains.move_to_element(element).perform()
            time.sleep(hover_time)
        except Exception:
            # Ignore if hover fails
            pass
        
    def human_navigate_back(self) -> None:
        """Navigate back using browser back button with human-like behavior."""
        # Small chance to use keyboard shortcut instead of browser button
        if random.random() < 0.2:
            self.action_chains.key_down(Keys.ALT).send_keys(Keys.LEFT).key_up(Keys.ALT).perform()
        else:
            self.driver.back()
        
        # Wait for page to load
        self.random_delay(2.0, 4.0)
