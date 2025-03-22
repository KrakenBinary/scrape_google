import time
import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)

from common.logger import (
    print_system_message,
    print_info_message, 
    print_success_message, 
    print_warning_message, 
    print_error_message
)

class GoogleMapsScraper:
    """
    Scraper for extracting business data from Google Maps using Selenium.
    This visible browser scraper searches, scrolls, and extracts business information.
    """
    
    def __init__(
        self,
        output_dir: str = "../data",
        headless: bool = False,
        proxy: Optional[Dict[str, str]] = None,
        wait_time: int = 10,
        scroll_pause_time: float = 1.5,
        max_results: int = 100
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
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.headless = headless
        self.proxy = proxy
        self.wait_time = wait_time
        self.scroll_pause_time = scroll_pause_time
        self.max_results = max_results
        
        self.driver = None
        self.wait = None
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
    
    def setup_driver(self) -> None:
        """
        Set up the Chrome WebDriver with specified options.
        """
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Add common options for stability and performance
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Use proxy if provided
        if self.proxy:
            if "http" in self.proxy:
                chrome_options.add_argument(f"--proxy-server={self.proxy['http'].replace('http://', '')}")
            elif "https" in self.proxy:
                chrome_options.add_argument(f"--proxy-server={self.proxy['https'].replace('https://', '')}")
        
        # Create and configure the WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, self.wait_time)
        
        # Set window size for better visibility of elements
        self.driver.set_window_size(1920, 1080)
        print_success_message("Chrome WebDriver initialized successfully")
    
    def close_driver(self) -> None:
        """
        Close the WebDriver and release resources.
        """
        if self.driver:
            self.driver.quit()
            print_info_message("WebDriver closed and resources released")
    
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
            self.driver.get(self.base_url)
            print_info_message(f"Navigated to {self.base_url}")
            
            # Wait for search box to be available
            search_box = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["search_box"]))
            )
            
            # Clear and fill the search box
            search_box.clear()
            
            # Format query with location if provided
            full_query = f"{query} {location}" if location else query
            search_box.send_keys(full_query)
            print_info_message(f"Entered search query: '{full_query}'")
            
            # Click search button or press Enter
            try:
                search_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["search_button"]))
                )
                search_button.click()
            except (TimeoutException, ElementClickInterceptedException):
                # Fallback to pressing Enter
                search_box.send_keys(Keys.ENTER)
            
            # Wait for results to load
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["results_container"]))
            )
            
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
            results_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["results_container"]))
            )
            
            # Track the number of items
            last_count = 0
            same_count_iterations = 0
            
            # Scroll until no new items are loaded or max_results is reached
            while True:
                # Get current items
                items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["result_items"])
                current_count = len(items)
                
                # Print the current count
                print_info_message(f"Currently loaded {current_count} business listings")
                
                # Check if we've reached our limit or if no new items are loaded
                if current_count >= self.max_results:
                    print_info_message(f"Reached maximum result limit: {self.max_results}")
                    break
                
                if current_count == last_count:
                    same_count_iterations += 1
                    if same_count_iterations >= 3:
                        # If count hasn't changed for several iterations, we've likely reached the end
                        print_info_message("No new listings found after multiple scrolls, likely reached the end")
                        break
                else:
                    same_count_iterations = 0
                
                # Scroll down in the results panel
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    results_container
                )
                
                # Wait for new results to load
                time.sleep(self.scroll_pause_time)
                
                # Update last count
                last_count = current_count
            
            # Final count after scrolling
            final_items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["result_items"])
            final_count = len(final_items)
            
            print_success_message(f"Scrolling complete. Found {final_count} business listings")
            return final_count
            
        except Exception as e:
            print_error_message(f"Error while scrolling through results: {str(e)}")
            return 0
    
    def extract_business_data(self) -> List[Dict[str, Any]]:
        """
        Extract data from all visible business listings.
        
        Returns:
            List of dictionaries containing business data
        """
        print_system_message("Starting extraction of business data...")
        
        all_business_data = []
        
        try:
            # Get all result items
            items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["result_items"])
            total_items = len(items)
            
            if total_items == 0:
                print_warning_message("No business listings found to extract")
                return []
            
            print_info_message(f"Found {total_items} businesses to process")
            
            # Process each business listing
            for index, item in enumerate(items[:self.max_results]):
                print_info_message(f"Processing business {index + 1} of {min(total_items, self.max_results)}")
                
                try:
                    # Click on the listing to view details
                    item.click()
                    time.sleep(2)  # Wait for business details to load
                    
                    # Extract business data
                    business_data = self._extract_current_business_data()
                    
                    if business_data:
                        all_business_data.append(business_data)
                        print_success_message(f"Successfully extracted data for: {business_data.get('name', 'Unknown Business')}")
                    
                    # Go back to the results list
                    back_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors["back_button"]))
                    )
                    back_button.click()
                    time.sleep(1.5)  # Wait for results to reload
                    
                    # Re-find the items as the DOM has likely been refreshed
                    items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["result_items"])
                    
                except (StaleElementReferenceException, ElementClickInterceptedException):
                    # If element becomes stale, refresh the items list
                    print_warning_message(f"Element reference issue with item {index + 1}, skipping")
                    items = self.driver.find_elements(By.CSS_SELECTOR, self.selectors["result_items"])
                    continue
                    
                except Exception as e:
                    print_error_message(f"Error processing business {index + 1}: {str(e)}")
                    continue
            
            print_success_message(f"Extraction complete. Processed {len(all_business_data)} businesses successfully")
            return all_business_data
            
        except Exception as e:
            print_error_message(f"Failed to extract business data: {str(e)}")
            return all_business_data
    
    def _extract_current_business_data(self) -> Dict[str, Any]:
        """
        Extract data for the currently displayed business.
        
        Returns:
            Dictionary containing business data
        """
        business_data = {}
        
        try:
            # Extract business name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors["business_name"]))
                )
                business_data["name"] = name_element.text.strip()
            except TimeoutException:
                business_data["name"] = "Unknown"
            
            # Extract business category
            try:
                category_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_category"])
                business_data["category"] = category_element.text.strip()
            except NoSuchElementException:
                business_data["category"] = ""
            
            # Extract address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_address"])
                business_data["address"] = address_element.text.strip()
            except NoSuchElementException:
                business_data["address"] = ""
            
            # Extract website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_website"])
                business_data["website"] = website_element.text.strip()
            except NoSuchElementException:
                business_data["website"] = ""
            
            # Extract phone number
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_phone"])
                business_data["phone"] = phone_element.text.strip()
            except NoSuchElementException:
                business_data["phone"] = ""
            
            # Extract business hours
            try:
                hours_button = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_hours_button"])
                hours_button.click()
                time.sleep(1)  # Wait for hours dialog to open
                
                hours_content = self.driver.find_element(By.CSS_SELECTOR, self.selectors["business_hours_content"])
                business_data["hours"] = hours_content.text.strip()
                
                # Close the hours dialog by clicking outside
                self.driver.find_element(By.TAG_NAME, "body").click()
            except (NoSuchElementException, ElementClickInterceptedException):
                business_data["hours"] = ""
            
            # Add timestamp
            business_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return business_data
            
        except Exception as e:
            print_error_message(f"Error extracting data for current business: {str(e)}")
            return business_data
    
    def save_data(self, data: List[Dict[str, Any]], search_query: str) -> str:
        """
        Save the scraped data to a JSON file.
        
        Args:
            data: List of business data dictionaries
            search_query: The search query used
            
        Returns:
            Path to the saved file
        """
        if not data:
            print_warning_message("No data to save")
            return ""
        
        # Create a filename based on the search query and timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_query = search_query.replace(" ", "_").lower()
        filename = f"gmaps_{safe_query}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            # Create output data structure
            output_data = {
                "search_query": search_query,
                "timestamp": timestamp,
                "count": len(data),
                "businesses": data
            }
            
            # Save to JSON file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print_success_message(f"Scraped data saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print_error_message(f"Failed to save data: {str(e)}")
            return ""
    
    def run(self, query: str, location: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str]:
        """
        Run the complete scraping process.
        
        Args:
            query: Search query
            location: Optional location
            
        Returns:
            Tuple of (scraped_data, output_file_path)
        """
        print_system_message(f"Starting Google Maps scraping for: {query}" + (f" in {location}" if location else ""))
        
        try:
            # Setup the WebDriver
            self.setup_driver()
            
            # Search for the query
            if not self.search_query(query, location):
                raise Exception("Search failed")
            
            # Allow the page to load fully
            time.sleep(3)
            
            # Scroll to load all results
            result_count = self.scroll_results()
            
            if result_count == 0:
                print_warning_message("No results found. Exiting scraper.")
                self.close_driver()
                return [], ""
            
            # Extract business data
            business_data = self.extract_business_data()
            
            # Save the data
            full_query = f"{query} {location}" if location else query
            output_file = self.save_data(business_data, full_query)
            
            # Cleanup
            self.close_driver()
            
            print_system_message("Google Maps scraping completed successfully!")
            return business_data, output_file
            
        except Exception as e:
            print_error_message(f"Error during scraping process: {str(e)}")
            
            # Ensure driver is closed
            self.close_driver()
            
            return [], ""


def main():
    """Run the Google Maps scraper as a standalone script."""
    parser = argparse.ArgumentParser(description="Google Maps Business Data Scraper")
    parser.add_argument("query", help="Search query for Google Maps")
    parser.add_argument("--location", "-l", help="Location for the search")
    parser.add_argument("--output", "-o", default="../data", help="Output directory for scraped data")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-results", "-m", type=int, default=100, help="Maximum number of results to scrape")
    parser.add_argument("--proxy", "-p", help="Proxy in format 'ip:port'")
    
    args = parser.parse_args()
    
    # Setup proxy dict if provided
    proxy = None
    if args.proxy:
        proxy = {
            "http": f"http://{args.proxy}",
            "https": f"https://{args.proxy}"
        }
    
    # Initialize and run the scraper
    scraper = GoogleMapsScraper(
        output_dir=args.output,
        headless=args.headless,
        proxy=proxy,
        max_results=args.max_results
    )
    
    scraper.run(args.query, args.location)


if __name__ == "__main__":
    main()
