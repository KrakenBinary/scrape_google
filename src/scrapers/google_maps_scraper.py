"""
Google Maps scraper implementation for TryloByte.
This implementation is built on the new modular structure to make future updates easier.
"""
import time
import json
import random
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from src.browsers.base import BaseBrowser
from src.browsers.selenium_browser import SeleniumBrowser
from src.common.logger import (
    print_system_message,
    print_info_message,
    print_success_message,
    print_warning_message,
    print_error_message
)
from src.scrapers.base_scraper import BaseScraper


class GoogleMapsScraper(BaseScraper):
    """
    Scraper for extracting business data from Google Maps.
    Uses the abstracted browser interface for Selenium operations.
    """
    
    def __init__(
        self,
        output_dir: str = "../data",
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
        wait_time: int = 10,
        scroll_pause_time: float = 1.5,
        max_results: int = 100,
        browser_type: str = "selenium"
    ):
        """
        Initialize the Google Maps Scraper.
        
        Args:
            output_dir: Directory to save scraped data
            headless: Run browser in headless mode
            proxy: Proxy to use for the browser
            wait_time: Maximum wait time for elements to load
            scroll_pause_time: Pause time between scrolls
            max_results: Maximum number of results to scrape
            browser_type: Type of browser implementation to use
        """
        super().__init__(output_dir)
        
        self.headless = headless
        self.proxy = proxy
        self.wait_time = wait_time
        self.scroll_pause_time = scroll_pause_time
        self.max_results = max_results
        self.browser_type = browser_type
        
        self.browser = None
        self.base_url = "https://www.google.com/maps"
        
        # Selectors for Google Maps elements
        self.selectors = {
            "search_box": "input#searchboxinput",
            "search_button": "button#searchbox-searchbutton",
            "results_container": "div[role='feed']",
            "result_items": "div[role='feed'] > div > div > a",
            "next_page": "button[jsaction*='pane.paginationSection.nextPage']",
            "business_name": "h1 span:first-child",
            "business_category": "button[jsaction*='pane.rating.category']",
            "business_address": "button[data-item-id*='address']",
            "business_website": "a[data-item-id*='authority']",
            "business_phone": "button[data-item-id*='phone:tel']",
            "business_hours_button": "button[data-item-id*='oh']",
            "business_hours_content": "div[role='dialog']",
            "back_button": "button[jsaction*='pane.backButton']",
        }
    
    def setup(self, **kwargs) -> bool:
        """
        Set up the scraper with appropriate browser instance.
        
        Args:
            **kwargs: Additional options for browser setup
            
        Returns:
            bool: True if setup was successful
        """
        try:
            # Initialize browser
            self.browser = SeleniumBrowser()
            
            # Configure browser options
            headless = kwargs.get('headless', self.headless)
            proxy = kwargs.get('proxy', self.proxy)
            
            # Extract special browser options
            browser_type = kwargs.get('browser_type', 'chrome')
            
            # Enhanced Chrome arguments to fix transparency and freezing issues on Linux
            chrome_arguments = {
                # Basic rendering fixes
                'disable-features': 'VizDisplayCompositor,IsolateOrigins,site-per-process',
                
                # Aggressive rendering fixes for Linux transparency/freezing issues
                'disable-gpu': '',
                'disable-gpu-compositing': '',
                'disable-gpu-vsync': '',
                'disable-software-rasterizer': '',
                'disable-gpu-rasterization': '',
                
                # Force compositing mode and layers
                'force-color-profile': 'srgb',
                'force-device-scale-factor': '1',
                
                # Window and UI fixes
                'disable-background-networking': '',
                'disable-default-apps': '',
                'window-size': '1920,1080',
                'window-position': '0,0',
                
                # User overrides
                **kwargs.get('chrome_arguments', {})
            }
            
            # Initialize the browser with our configuration
            success = self.browser.initialize(
                headless=headless,
                browser_type=browser_type,
                chrome_arguments=chrome_arguments,
                proxy=proxy
            )
            
            if not success:
                print_error_message("Failed to initialize browser")
                return False
            
            print_info_message(f"Browser initialized successfully (headless: {headless})")
            return True
            
        except Exception as e:
            print_error_message(f"Error setting up scraper: {str(e)}")
            return False
    
    def cleanup(self) -> None:
        """Clean up the browser resources."""
        if self.browser:
            self.browser.close()
    
    def search_query(self, query: str, location: Optional[str] = None) -> bool:
        """
        Perform a search on Google Maps.
        
        Args:
            query: Search query (e.g., "restaurants", "hotels")
            location: Optional location to add to query
            
        Returns:
            True if search was successful, False otherwise
        """
        try:
            # Navigate to Google Maps
            if not self.browser.navigate(self.base_url):
                return False
            
            # Wait for search box to be available
            search_box = self.browser.wait_for_element(
                self.selectors["search_box"], 
                timeout=self.wait_time
            )
            
            if not search_box:
                print_error_message("Search box not found")
                return False
            
            # Format query with location if provided
            full_query = f"{query} {location}" if location else query
            
            # Enter search query - explicitly pass the WebElement, not a boolean
            if not self.browser.send_keys(search_box, full_query):
                print_error_message("Failed to enter search query")
                return False
            
            print_info_message(f"Entered search query: '{full_query}'")
            
            # Click search button or press Enter
            search_button = self.browser.wait_for_element(
                self.selectors["search_button"], 
                timeout=5
            )
            
            if search_button and self.browser.click(search_button):
                print_info_message("Clicked search button")
            else:
                # Fallback to pressing Enter - need to get the search box element again in case it changed
                search_box = self.browser.wait_for_element(
                    self.selectors["search_box"], 
                    timeout=5
                )
                
                if not search_box:
                    print_error_message("Search box not found for Enter key")
                    return False
                    
                # Make sure to send Enter key to the actual element
                if not self.browser.send_keys(search_box, "\n"):
                    print_error_message("Failed to press Enter key")
                    return False
                    
                print_info_message("Pressed Enter to search")
            
            # Wait for results to load
            results = self.browser.wait_for_element(
                self.selectors["results_container"],
                timeout=self.wait_time
            )
            
            if not results:
                print_error_message("No results found")
                return False
            
            print_success_message(f"Search for '{full_query}' completed successfully")
            return True
            
        except Exception as e:
            print_error_message(f"Failed to perform search: {str(e)}")
            return False
    
    def scroll_results(self) -> int:
        """
        Scroll through the search results to load more items.
        
        Returns:
            Number of results found
        """
        print_system_message("Scrolling through results to load all available listings...")
        
        try:
            # Wait for the results container to be present
            results_container = self.browser.wait_for_element(
                self.selectors["results_container"],
                timeout=self.wait_time
            )
            
            if not results_container:
                print_error_message("Results container not found")
                return 0
            
            # Track the number of items
            last_count = 0
            same_count_iterations = 0
            
            # Scroll until no new items are loaded or max_results is reached
            while True:
                # Get current items
                items = self.browser.find_elements(self.selectors["result_items"])
                current_count = len(items)
                
                # Print the current count
                print_info_message(f"Currently loaded {current_count} business listings")
                
                # Check if we've reached the maximum
                if 0 < self.max_results <= current_count:
                    print_success_message(f"Reached maximum results limit: {self.max_results}")
                    break
                    
                # Check if no new items were loaded after several scrolls
                if current_count == last_count:
                    same_count_iterations += 1
                    if same_count_iterations >= 3:
                        print_success_message("No new results loaded after multiple scrolls, assuming all results loaded")
                        break
                else:
                    same_count_iterations = 0
                
                # Update last count
                last_count = current_count
                
                # Scroll down in the results panel
                self.browser.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    results_container
                )
                
                # Pause to let new results load
                time.sleep(self.scroll_pause_time)
                
                # Add some human-like randomness to scrolling
                if random.random() < 0.2:
                    extra_pause = random.uniform(0.5, 2.0)
                    time.sleep(extra_pause)
            
            return current_count
            
        except Exception as e:
            print_error_message(f"Error while scrolling results: {str(e)}")
            return 0
    
    def extract_business_data(self, element) -> Optional[Dict[str, str]]:
        """
        Extract business data from a listing element.
        
        Args:
            element: The listing element to extract data from
            
        Returns:
            Dict containing business information or None if extraction failed
        """
        try:
            # Click on the listing to open the details panel
            if not self.browser.click(element):
                print_error_message("Failed to click on business listing")
                return None
            
            # Wait for business details to load
            time.sleep(2)
            
            # Extract business name
            name_element = self.browser.wait_for_element(
                self.selectors["business_name"],
                timeout=5
            )
            name = self.browser.get_text(name_element) if name_element else "Unknown"
            
            print_info_message(f"Extracting data for: {name}")
            
            # Extract business category
            category_element = self.browser.find_element(self.selectors["business_category"])
            category = self.browser.get_text(category_element) if category_element else ""
            
            # Extract business address
            address_element = self.browser.find_element(self.selectors["business_address"])
            address = self.browser.get_text(address_element) if address_element else ""
            
            # Extract website
            website_element = self.browser.find_element(self.selectors["business_website"])
            website = self.browser.get_attribute(website_element, "href") if website_element else ""
            
            # Extract phone number
            phone_element = self.browser.find_element(self.selectors["business_phone"])
            phone = self.browser.get_text(phone_element) if phone_element else ""
            
            # Extract hours of operation
            hours = ""
            hours_button = self.browser.find_element(self.selectors["business_hours_button"])
            if hours_button and self.browser.click(hours_button):
                # Wait for hours dialog to appear
                time.sleep(1)
                hours_content = self.browser.find_element(self.selectors["business_hours_content"])
                hours = self.browser.get_text(hours_content) if hours_content else ""
                
                # Close hours dialog by clicking back button
                back_button = self.browser.find_element(self.selectors["back_button"])
                if back_button:
                    self.browser.click(back_button)
            
            # Compile business data
            business_data = {
                "name": name,
                "category": category,
                "address": address,
                "website": website,
                "phone": phone,
                "hours": hours,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Click back to results
            back_button = self.browser.find_element(self.selectors["back_button"])
            if back_button:
                self.browser.click(back_button)
                time.sleep(1)  # Wait for results to load again
            
            return business_data
            
        except Exception as e:
            print_error_message(f"Error extracting business data: {str(e)}")
            return None
    
    def run(self, query: str, location: Optional[str] = None, **kwargs) -> Tuple[List[Dict[str, Any]], str]:
        """
        Run the Google Maps scraper.
        
        Args:
            query: Search query
            location: Optional location for the search
            **kwargs: Additional options
            
        Returns:
            Tuple containing a list of scraped businesses and the output filename
        """
        output_file = ""
        businesses = []
        
        try:
            # Set up the browser if not already done
            if not self.browser:
                if not self.setup(**kwargs):
                    return [], ""
            
            # Perform the search
            if not self.search_query(query, location):
                return [], ""
            
            # Scroll to load all results
            total_results = self.scroll_results()
            
            if total_results == 0:
                print_warning_message("No business listings found")
                return [], ""
            
            print_success_message(f"Found {total_results} business listings")
            
            # Get all listing elements
            listing_elements = self.browser.find_elements(self.selectors["result_items"])
            
            # Limit to max_results if specified
            if 0 < self.max_results < len(listing_elements):
                listing_elements = listing_elements[:self.max_results]
            
            # Process each listing
            for i, element in enumerate(listing_elements):
                print_system_message(f"Processing business {i+1} of {len(listing_elements)}")
                
                business_data = self.extract_business_data(element)
                if business_data:
                    businesses.append(business_data)
            
            # Save results to file
            if businesses:
                # Create timestamp for the filename
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                # Create a safe filename from the query
                safe_query = "".join(c if c.isalnum() else "_" for c in query)
                if len(safe_query) > 30:
                    safe_query = safe_query[:30]
                
                # Create the output filename
                output_file = self.output_dir / f"google_maps_{safe_query}_{timestamp}.json"
                
                # Prepare the data structure
                output_data = {
                    "search_query": f"{query} {location}" if location else query,
                    "timestamp": timestamp,
                    "count": len(businesses),
                    "businesses": businesses
                }
                
                # Write to file
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                print_success_message(f"Saved {len(businesses)} businesses to {output_file}")
            
            return businesses, str(output_file)
            
        except Exception as e:
            print_error_message(f"Error running Google Maps scraper: {str(e)}")
            return [], ""
        finally:
            # Always clean up resources
            self.cleanup()
