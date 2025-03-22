import os
import sys
import json
import time
import random
import argparse
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.proxy_manager import ProxyManager
from src.browser_manager import BrowserManager
from src.console_output import (
    print_system_message, 
    print_info_message, 
    print_warning_message, 
    print_error_message, 
    print_success_message
)
from src.human_behavior import HumanBehavior
from src.data_extractor import DataExtractor
from src.error_handler import ErrorHandler


class GoogleMapsScraper:
    """Main class for Google Maps scraping tool."""
    
    def __init__(
        self,
        output_dir: str = "../data",
        headless: bool = False,
        browser_type: str = "chrome",
        max_results: int = 0,
        listings_per_proxy: int = 0,
        proxy_test_url: str = "http://httpbin.org/ip",
        target_proxy_count: int = 10
    ):
        """
        Initialize GoogleMapsScraper.
        
        Args:
            output_dir: Directory to save scraped data
            headless: Whether to run the browser in headless mode
            browser_type: Type of browser to use ('chrome', 'firefox')
            max_results: Maximum number of results to scrape (0 for unlimited)
            listings_per_proxy: Number of listings to scrape per proxy (0 for unlimited)
            proxy_test_url: URL to use for testing proxies
            target_proxy_count: Number of working proxies to maintain
        """
        # Setup data directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser and scraping settings
        self.headless = headless
        self.browser_type = browser_type
        self.max_results = max_results
        self.listings_per_proxy = listings_per_proxy
        
        # Initialize managers
        self.proxy_manager = ProxyManager(
            proxy_test_url=proxy_test_url, 
            target_proxy_count=target_proxy_count,
            proxy_cache_dir=output_dir
        )
        self.browser_manager = BrowserManager(headless=headless, browser_type=browser_type)
        
        # Internal state
        self.current_browser = None
        self.current_proxy = None
        self.proxy_change_count = 0
        self.listings_count = 0
        self.skip_count = 0
        
        # Debug info
        self.debug_mode = False
        
        # Random retro hacker messages
        self.hacker_messages = [
            "[ STATUS ] Breaking through firewall layer {layer}...",
            "[ STATUS ] Bypassing security checkpoint {layer}...",
            "[ STATUS ] Decrypting node {layer} of {total}...",
            "[ STATUS ] Accessing data sector {layer}...",
            "[ STATUS ] Extracting mainframe record {layer}...",
            "[ STATUS ] Downloading neural pattern {layer}...",
            "[ STATUS ] Scanning quantum signature {layer}...",
            "[ STATUS ] Cracking encrypted bundle {layer}...",
            "[ STATUS ] Analyzing digital footprint {layer}...",
            "[ STATUS ] Processing cyber-telemetry {layer}..."
        ]
    
    def get_status_message(self, current: int, total: int) -> str:
        """
        Generate a random hacker status message.
        
        Args:
            current: Current item number
            total: Total number of items
            
        Returns:
            Formatted status message
        """
        message = random.choice(self.hacker_messages)
        return message.format(layer=current, total=total)
    
    def refresh_proxy(self) -> bool:
        """
        Get a new proxy from the proxy manager.
        
        Returns:
            True if successful, False otherwise
        """
        # Close any existing browser
        if self.current_browser:
            try:
                self.current_browser.quit()
            except Exception as e:
                print_warning_message(f"Error closing browser: {e}")
            finally:
                self.current_browser = None
        
        # Get a new proxy
        self.current_proxy = self.proxy_manager.get_next_proxy()
        if not self.current_proxy:
            print_error_message("No proxies available. Cannot continue scraping.")
            return False
            
        # If we've switched to direct connection, report it
        if self.current_proxy.get('direct', False):
            print_warning_message("Using direct connection (no proxy)")
        else:
            proxy_str = self.current_proxy.get('http', 'unknown')
            print_system_message(f"Deploying digital proxy: {proxy_str}")
            
        # Try to get a browser with the new proxy
        try:
            self.current_browser = self.browser_manager.get_browser(self.current_proxy)
            return True
        except Exception as e:
            print_error_message(f"Failed to initialize browser with proxy: {e}")
            # Report this proxy failure
            self.proxy_manager.report_proxy_failure(self.current_proxy)
            return False
    
    def handle_search_error(self, error, query):
        """
        Handle errors that occur during search.
        
        Args:
            error: The exception that occurred
            query: The search query that was being processed
            
        Returns:
            True if the error was handled and scraping should continue,
            False if scraping should stop
        """
        print(f"Error during search: {error}")
        
        # Report proxy failure if using a proxy
        if self.current_proxy:
            self.proxy_manager.report_proxy_failure(self.current_proxy)
        
        # Check for proxy-related errors
        proxy_errors = [
            "ERR_TUNNEL_CONNECTION_FAILED",
            "ERR_PROXY_CONNECTION_FAILED",
            "ERR_CONNECTION_REFUSED",
            "ERR_CONNECTION_TIMED_OUT",
            "ERR_CONNECTION_CLOSED",
            "ERR_CONNECTION_RESET",
            "ERR_INTERNET_DISCONNECTED"
        ]
        
        for proxy_error in proxy_errors:
            if proxy_error in str(error):
                print_warning_message(f"Search algorithm compromised. Switching neural pathways...")
                # Try with a new proxy
                if self.refresh_proxy():
                    return True
                else:
                    return False
        
        # Check for Google detection
        detection_indicators = [
            "automated queries",
            "unusual traffic",
            "captcha",
            "CAPTCHA",
            "security check"
        ]
        
        for indicator in detection_indicators:
            if indicator in str(error):
                print_warning_message(f"Identity compromised! Switching digital mask...")
                if self.refresh_proxy():
                    return True
                else:
                    return False
        
        # Other unknown errors
        print_error_message(f"Search algorithm persistently failing. Mission aborted.")
        return False
    
    def scrape(self, query: str, output_filename: Optional[str] = None) -> List[Dict]:
        """
        Scrape Google Maps for the given query.
        
        Args:
            query: Search query (e.g., "restaurants in New York")
            output_filename: Optional filename to save results (without extension)
            
        Returns:
            List of dictionaries containing business data
        """
        if not output_filename:
            # Generate filename from query
            output_filename = query.replace(" ", "_").lower()[:30]
        
        output_file = self.output_dir / f"{output_filename}.json"
        
        # Initialize browser if not already initialized
        if not self.current_browser and not self.refresh_proxy():
            print_error_message("Failed to initialize digital reconnaissance systems.")
            return []
        
        all_results = []
        
        try:
            # Search for the query
            print_system_message("Initiating search algorithm...")
            search_success = self.data_extractor.search_for_query(query)
            
            if not search_success:
                print_warning_message("Search algorithm compromised. Switching neural pathways...")
                if self.handle_search_error("Search failure", query):
                    search_success = self.data_extractor.search_for_query(query)
                    if not search_success:
                        print_error_message("Search algorithm persistently failing. Mission aborted.")
                        return []
                else:
                    print_error_message("Failed to establish new digital identity. Aborting mission.")
                    return []
            
            # Scrape results
            if self.max_results > 0:
                print_system_message(f"Target acquired. Extracting {self.max_results} data nodes for: '{query}'")
            else:
                print_system_message(f"Target acquired. Extracting ALL available data nodes for: '{query}'")
            results = self.data_extractor.get_listing_results(max_results=self.max_results)
            
            print_success_message(f"Digital heist complete! Extracted {len(results)} data packages.")
            all_results.extend(results)
            
            # Save results to file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print_system_message(f"Data saved to encrypted storage: {output_file}")
            
            # Report proxy success
            self.proxy_manager.report_proxy_success(self.current_proxy)
            
        except Exception as e:
            print_error_message(f"Unexpected system failure during extraction: {e}")
            self.proxy_manager.report_proxy_failure(self.current_proxy)
        finally:
            # Close the browser
            if self.current_browser:
                self.current_browser.quit()
                self.current_browser = None
        
        return all_results
    
    def scrape_multiple_queries(self, queries: List[str], output_prefix: str = "gmaps_results", max_workers: int = None) -> Dict[str, List[Dict]]:
        """
        Scrape multiple queries using multithreading.
        
        Args:
            queries: List of search queries
            output_prefix: Prefix for output filenames
            max_workers: Maximum number of worker threads (default: CPU count)
            
        Returns:
            Dictionary mapping queries to their results
        """
        results = {}
        
        # Determine the maximum number of worker threads (default to CPU count)
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), len(queries))
        
        print_system_message(f"Deploying {max_workers} parallel neural interfaces for {len(queries)} queries.")
        
        def scrape_query(args):
            """Worker function for thread pool"""
            i, query = args
            print(f"\n{self.get_status_message(i+1, len(queries))}")
            
            # Generate unique filename
            filename = f"{output_prefix}_{i+1}"
            
            # Create a new scraper instance for each thread
            scraper = GoogleMapsScraper(
                output_dir=self.output_dir,
                headless=self.headless,
                browser_type=self.browser_type,
                max_results=self.max_results,
                listings_per_proxy=self.listings_per_proxy,
                proxy_test_url=self.proxy_test_url,
                target_proxy_count=self.target_proxy_count
            )
            
            # Scrape the query
            query_results = scraper.scrape(query, filename)
            return query, query_results
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for query, query_results in executor.map(scrape_query, enumerate(queries)):
                results[query] = query_results
                print_system_message(f"Query completed: {query} - {len(query_results)} results")
        
        print_success_message(f"All {len(queries)} queries successfully processed!")
        return results


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="TryloByte - Google Maps Scraper with free proxies and human-like behavior")
    
    parser.add_argument("query", nargs="?", default=None, help="Search query (e.g., 'restaurants in New York')")
    parser.add_argument("--queries-file", "-f", type=str, help="File containing search queries, one per line")
    parser.add_argument("--output-dir", "-o", type=str, default="data", help="Directory to save output data")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--browser", "-b", type=str, default="chrome", choices=["chrome", "firefox"], help="Browser to use")
    parser.add_argument("--max-results", "-m", type=int, default=0, help="Maximum number of results to scrape per query (0 = unlimited)")
    parser.add_argument("--listings-per-proxy", "-l", type=int, default=0, help="Number of listings to scrape before rotating proxy (0 = unlimited)")
    parser.add_argument("--proxy-test-url", "-p", type=str, default="http://httpbin.org/ip", help="URL to use for testing proxies")
    parser.add_argument("--threads", "-t", type=int, default=None, help="Number of threads for parallel scraping (default: CPU count)")
    parser.add_argument("--target-proxy-count", "-c", type=int, default=10, help="Number of working proxies to find (default: 10)")
    
    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_arguments()
    
    # Validate arguments
    if not args.query and not args.queries_file:
        print_error_message("Either a query or a queries file must be provided.")
        sys.exit(1)
    
    # Initialize scraper
    scraper = GoogleMapsScraper(
        output_dir=args.output_dir,
        headless=args.headless,
        browser_type=args.browser,
        max_results=args.max_results,
        listings_per_proxy=args.listings_per_proxy,
        proxy_test_url=args.proxy_test_url,
        target_proxy_count=args.target_proxy_count
    )
    
    if args.queries_file:
        # Read queries from file
        try:
            with open(args.queries_file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print_error_message(f"Failed to read queries file: {e}")
            sys.exit(1)
        
        # Scrape multiple queries
        scraper.scrape_multiple_queries(queries, max_workers=args.threads)
    else:
        # Scrape single query
        scraper.scrape(args.query)


if __name__ == "__main__":
    main()
