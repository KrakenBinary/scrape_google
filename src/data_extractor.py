import json
import time
from typing import Dict, List, Optional, Any
import sys
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

try:
    from colorama import init, Fore, Style
    # Initialize colorama
    init(autoreset=True)
    # Color constants
    NEON_GREEN = Fore.GREEN + Style.BRIGHT
    ALERT_RED = Fore.RED + Style.BRIGHT
    WARNING_YELLOW = Fore.YELLOW
    INFO_CYAN = Fore.CYAN
    SUCCESS_GREEN = Fore.GREEN
    LOADING_BLUE = Fore.BLUE + Style.BRIGHT
    RESET = Style.RESET_ALL
except ImportError:
    # Fallback if colorama is not available
    NEON_GREEN = ALERT_RED = WARNING_YELLOW = INFO_CYAN = SUCCESS_GREEN = LOADING_BLUE = RESET = ""

from .human_behavior import HumanBehavior


class DataExtractor:
    """Extracts data from Google Maps listings."""
    
    def __init__(self, driver: webdriver.Remote, human_behavior: HumanBehavior, wait_timeout: int = 10):
        """
        Initialize the data extractor.
        
        Args:
            driver: Selenium webdriver instance
            human_behavior: HumanBehavior instance for simulating human-like behavior
            wait_timeout: Maximum wait time in seconds for elements to appear
        """
        self.driver = driver
        self.human = human_behavior
        self.wait = WebDriverWait(
            driver, 
            wait_timeout, 
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException)
        )
    
    def search_for_query(self, query: str) -> bool:
        """
        Search for a query on Google Maps.
        
        Args:
            query: Search query (e.g., "restaurants in New York")
            
        Returns:
            True if search was successful, False otherwise
        """
        try:
            # Navigate to Google Maps
            self.driver.get("https://www.google.com/maps")
            
            # Wait for the page to load
            self.human.random_delay(2.0, 4.0)
            
            # Find and click the search box
            search_box = self.wait.until(
                EC.element_to_be_clickable((By.ID, "searchboxinput"))
            )
            
            # Simulate human-like clicking and typing
            self.human.random_mouse_movement(2)
            self.human.human_click(search_box)
            self.human.human_type(search_box, query)
            
            # Wait for search results to load
            self.human.random_delay(3.0, 5.0)
            
            # Check if results are displayed
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
                )
                return True
            except TimeoutException:
                return False
            
        except Exception as e:
            print(f"Error during search: {e}")
            return False
    
    def _extract_from_listing_card(self, card_element) -> Dict[str, Any]:
        """
        Extract data from a listing card in the search results.
        
        Args:
            card_element: WebElement representing a listing card
            
        Returns:
            Dictionary containing extracted data
        """
        data = {
            "name": "",
            "rating": None,
            "reviews_count": None,
            "category": "",
            "address": "",
            "phone": "",
            "website": ""
        }
        
        try:
            # Hover over the card first (human-like behavior)
            self.human.hover_over_element(card_element)
            
            # Extract name
            try:
                name_element = card_element.find_element(By.CSS_SELECTOR, "div.fontHeadlineSmall")
                data["name"] = name_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract rating and reviews
            try:
                rating_element = card_element.find_element(By.CSS_SELECTOR, "span.fontBodyMedium > span")
                rating_text = rating_element.text.strip()
                if rating_text:
                    data["rating"] = float(rating_text.split()[0].replace(",", "."))
                    
                    # Extract review count
                    reviews_text = rating_element.find_element(By.XPATH, "..").text
                    if "(" in reviews_text and ")" in reviews_text:
                        reviews_count = reviews_text.split("(")[1].split(")")[0].replace(",", "")
                        data["reviews_count"] = int(reviews_count)
            except (NoSuchElementException, ValueError, IndexError):
                pass
            
            # Extract category and address
            try:
                details_elements = card_element.find_elements(By.CSS_SELECTOR, "div.fontBodyMedium > div:not(.UaQhfb)")
                if len(details_elements) >= 1:
                    data["category"] = details_elements[0].text.strip()
                if len(details_elements) >= 2:
                    data["address"] = details_elements[1].text.strip()
            except NoSuchElementException:
                pass
            
        except Exception as e:
            print(f"Error extracting data from listing card: {e}")
        
        return data
    
    def _extract_detailed_data(self) -> Dict[str, Any]:
        """
        Extract detailed data from a business listing page.
        
        Returns:
            Dictionary containing detailed business data
        """
        data = {
            "name": "",
            "rating": None,
            "reviews_count": None,
            "category": "",
            "address": "",
            "phone": "",
            "website": "",
            "hours": {},
            "price_level": "",
            "description": "",
            "photos_count": 0,
            "location": {"lat": None, "lng": None}
        }
        
        try:
            # Wait for the page to load
            self.human.random_delay(2.0, 4.0)
            
            # Extract name
            try:
                name_element = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.fontHeadlineLarge"))
                )
                data["name"] = name_element.text.strip()
            except TimeoutException:
                pass
            
            # Extract rating and reviews
            try:
                rating_element = self.driver.find_element(By.CSS_SELECTOR, "div.fontDisplayLarge")
                if rating_element:
                    data["rating"] = float(rating_element.text.replace(",", "."))
                
                reviews_element = self.driver.find_element(By.CSS_SELECTOR, "div.fontBodyMedium span[aria-label*='reviews']")
                if reviews_element:
                    reviews_text = reviews_element.get_attribute("aria-label")
                    data["reviews_count"] = int(reviews_text.split()[0].replace(",", "").replace(".", ""))
            except (NoSuchElementException, ValueError):
                pass
            
            # Extract category
            try:
                category_element = self.driver.find_element(By.CSS_SELECTOR, "button[jsaction*='category']")
                data["category"] = category_element.text.strip()
            except NoSuchElementException:
                pass
            
            # Extract address
            try:
                address_element = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']")
                data["address"] = address_element.find_element(By.CSS_SELECTOR, "div.fontBodyMedium").text.strip()
            except NoSuchElementException:
                pass
            
            # Extract phone number
            try:
                phone_element = self.driver.find_element(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                data["phone"] = phone_element.find_element(By.CSS_SELECTOR, "div.fontBodyMedium").text.strip()
            except NoSuchElementException:
                pass
            
            # Extract website
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, "a[data-item-id*='authority']")
                data["website"] = website_element.get_attribute("href")
            except NoSuchElementException:
                pass
            
            # Extract hours
            try:
                hours_button = self.driver.find_element(By.CSS_SELECTOR, "div[role='button'][aria-label*='hour']")
                
                # Simulate human clicking on hours button
                self.human.human_click(hours_button)
                self.human.random_delay(1.0, 2.0)
                
                # Get hours from the popup
                hours_elements = self.driver.find_elements(By.CSS_SELECTOR, "tr.fontBodyMedium")
                for element in hours_elements:
                    try:
                        day = element.find_element(By.CSS_SELECTOR, "th").text.strip()
                        time_range = element.find_element(By.CSS_SELECTOR, "td").text.strip()
                        data["hours"][day] = time_range
                    except NoSuchElementException:
                        continue
                
                # Click somewhere else to close the popup
                self.human.random_mouse_movement(1)
                self.driver.find_element(By.TAG_NAME, "body").click()
                
            except (NoSuchElementException, TimeoutException):
                pass
            
            # Extract price level
            try:
                price_element = self.driver.find_element(By.CSS_SELECTOR, "span.fontTitleSmall[aria-label*='Price']")
                data["price_level"] = len(price_element.text.strip())
            except NoSuchElementException:
                pass
            
            # Extract coordinates from URL
            try:
                url = self.driver.current_url
                if "@" in url and "," in url:
                    coords = url.split("@")[1].split(",")
                    if len(coords) >= 2:
                        data["location"]["lat"] = float(coords[0])
                        data["location"]["lng"] = float(coords[1])
            except (IndexError, ValueError):
                pass
            
        except Exception as e:
            print(f"Error extracting detailed data: {e}")
        
        return data
    
    def get_listing_results(self, max_results: int = 0) -> List[Dict[str, Any]]:
        """
        Extract details from Google Maps listing results.
        
        Args:
            max_results: Maximum number of results to extract (0 = unlimited)
            
        Returns:
            List of dictionaries containing listing details
        """
        results = []
        scroll_count = 0
        start_time = time.time()
        total_processed = 0
        
        # Progress bar variables
        progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        progress_idx = 0
        
        try:
            # Wait for results container
            result_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            # Get all listing cards
            listing_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            
            if not listing_cards:
                print(f"[ {WARNING_YELLOW}ALERT{RESET} ] No listing cards found. Security measures may be active.")
                return results
            
            print(f"[ {NEON_GREEN}TARGET{RESET} ] Located {len(listing_cards)} potential data packets.")
            
            # Process each listing card
            for i, card in enumerate(listing_cards):
                try:
                    # Update progress spinner
                    progress_idx = (progress_idx + 1) % len(progress_chars)
                    progress_percentage = (i + 1) / len(listing_cards) * 100 if listing_cards else 0
                    status_msg = f"[ {LOADING_BLUE}PROCESS{RESET} ] Extracting data {progress_chars[progress_idx]} {i+1}/{len(listing_cards)} ({progress_percentage:.1f}%)"
                    sys.stdout.write(f"\r{status_msg}")
                    sys.stdout.flush()
                    
                    # Extract data from the card
                    card_data = self._extract_from_listing_card(card)
                    
                    # Click on the card to view details
                    try:
                        self.human.random_delay(1.0, 2.0)
                        self.human.human_click(card)
                        
                        # Extract detailed data
                        detailed_data = self._extract_detailed_data()
                        
                        # Merge card and detailed data
                        for key, value in detailed_data.items():
                            if value and (key not in card_data or not card_data[key]):
                                card_data[key] = value
                        
                        # Navigate back to results
                        self.human.human_navigate_back()
                        self.human.random_delay(2.0, 3.0)
                        
                        # Re-find result cards after navigating back
                        listing_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    except Exception as e:
                        print(f"Error processing listing details: {e}")
                    
                    results.append(card_data)
                    total_processed += 1
                    
                    # Update status line with more detailed info
                    elapsed = time.time() - start_time
                    rate = total_processed / elapsed if elapsed > 0 else 0
                    status_msg = f"[ {LOADING_BLUE}PROCESS{RESET} ] Extracting: {progress_chars[progress_idx]} {i+1}/{len(listing_cards)} - Found: {total_processed} - Rate: {rate:.2f}/sec"
                    sys.stdout.write(f"\r{status_msg}")
                    sys.stdout.flush()
                    
                    # Check if we've reached the maximum results (0 = unlimited)
                    if max_results > 0 and len(results) >= max_results:
                        print(f"\n[ {SUCCESS_GREEN}SUCCESS{RESET} ] Maximum result limit reached ({max_results}). Extraction complete.")
                        break
                    
                    # Simulate human behavior with random delays between listings
                    self.human.random_delay(1.0, 3.0)
                    
                except Exception as e:
                    print(f"\n[ {ALERT_RED}ERROR{RESET} ] Failed to extract data from listing {i+1}: {str(e)}")
                    continue
                
                # Scroll to load more results if needed
                if i == len(listing_cards) - 5 and (max_results == 0 or len(results) < max_results):
                    print(f"\n[ {LOADING_BLUE}SYSTEM{RESET} ] Scrolling to reveal more hidden data...")
                    self.human.human_scroll()
                    scroll_count += 1
                    time.sleep(random.uniform(1.0, 2.0))
                    
                    # Get updated listing cards
                    new_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
                    if len(new_cards) > len(listing_cards):
                        print(f"[ {SUCCESS_GREEN}SUCCESS{RESET} ] Found {len(new_cards) - len(listing_cards)} additional targets.")
                        listing_cards = new_cards
            
            # Clear the status line
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()
            
            # Show final status
            elapsed = time.time() - start_time
            print(f"[ {SUCCESS_GREEN}COMPLETE{RESET} ] Extracted {len(results)} listings in {elapsed:.1f} seconds ({len(results)/elapsed:.2f}/sec)")
                
        except Exception as e:
            print(f"[ {ALERT_RED}ERROR{RESET} ] Failed to extract listing results: {str(e)}")
        
        return results
