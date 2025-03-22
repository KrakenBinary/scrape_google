#!/usr/bin/env python3
import json
import argparse
import random
from pathlib import Path
from typing import Dict, Optional, List

from src.proxy_harvester import ProxyHarvester
from src.scrapers.google_maps_scraper import GoogleMapsScraper
from src.common.logger import (
    print_system_message,
    print_info_message,
    print_success_message,
    print_warning_message,
    print_error_message
)

def load_proxies(proxy_file: str, proxy_type: str = "elite") -> List[Dict[str, str]]:
    """
    Load proxies from a JSON file.
    
    Args:
        proxy_file: Path to the proxy JSON file
        proxy_type: Type of proxies to filter for ('elite', 'anonymous', 'all')
        
    Returns:
        List of proxy dictionaries
    """
    try:
        with open(proxy_file, 'r') as f:
            data = json.load(f)
        
        if "working_proxies" in data:
            proxies = data["working_proxies"]
            
            # Filter proxies by anonymity level if requested
            if proxy_type != "all":
                filtered_proxies = [p for p in proxies if p.get("anonymity") == proxy_type]
                print_info_message(f"Filtered {len(filtered_proxies)} {proxy_type} proxies from {len(proxies)} total proxies")
                return filtered_proxies
            
            return proxies
        else:
            print_warning_message(f"No working proxies found in {proxy_file}")
            return []
    except Exception as e:
        print_error_message(f"Failed to load proxies: {e}")
        return []

def run_with_proxy(
    query: str,
    location: Optional[str],
    output_dir: str,
    headless: bool,
    max_results: int,
    proxy: Optional[Dict[str, str]] = None
) -> bool:
    """
    Run the Google Maps scraper with an optional proxy.
    
    Args:
        query: Search query
        location: Location for the search
        output_dir: Output directory
        headless: Run in headless mode
        max_results: Maximum results to scrape
        proxy: Optional proxy to use
        
    Returns:
        True if scraping was successful, False otherwise
    """
    try:
        # Initialize the scraper with our new modular architecture
        scraper = GoogleMapsScraper(
            output_dir=output_dir,
            headless=headless,
            proxy=proxy,
            max_results=max_results
        )
        
        # Run the scraper with the setup and cleanup handled internally
        data, output_file = scraper.run(query, location)
        
        return len(data) > 0 and output_file != ""
    except Exception as e:
        print_error_message(f"Error running scraper: {e}")
        return False

def main():
    """Main function to run the Google Maps scraper with proxy support."""
    parser = argparse.ArgumentParser(description="Run Google Maps Scraper with optional proxy support")
    parser.add_argument("query", help="Search query for Google Maps")
    parser.add_argument("--location", "-l", help="Location for the search")
    parser.add_argument("--output", "-o", default="../data", help="Output directory for scraped data")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-results", "-m", type=int, default=100, help="Maximum number of results to scrape")
    parser.add_argument("--use-proxy", "-p", action="store_true", help="Use a proxy from the proxy harvester")
    parser.add_argument("--proxy-file", help="Load proxies from this file instead of harvesting new ones")
    parser.add_argument("--proxy-type", choices=["elite", "anonymous", "all"], default="elite", 
                        help="Type of proxy to use (elite, anonymous, all)")
    parser.add_argument("--harvest-only", action="store_true", help="Only harvest proxies, do not run scraper")
    parser.add_argument("--country-filter", default="US", help="Country filter for proxy harvesting")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure proxy usage
    proxy = None
    proxies = []
    
    if args.use_proxy or args.harvest_only:
        print_system_message("Initializing proxy harvesting process...")
        
        if args.proxy_file:
            # Load proxies from file
            print_info_message(f"Loading proxies from file: {args.proxy_file}")
            proxies = load_proxies(args.proxy_file, args.proxy_type)
        else:
            # Harvest new proxies
            print_info_message(f"Harvesting new proxies with country filter: {args.country_filter}")
            harvester = ProxyHarvester(
                output_dir=str(output_dir),
                country_filter=args.country_filter
            )
            
            print_system_message("Launching proxy harvester...")
            found_proxies, csv_path, json_path = harvester.run()
            
            if found_proxies:
                print_success_message(f"Successfully harvested {len(found_proxies)} proxies")
                print_info_message(f"Proxies saved to: {json_path}")
                
                # Filter proxies by requested type
                if args.proxy_type != "all":
                    proxies = [p for p in found_proxies if p.get("anonymity") == args.proxy_type]
                    print_info_message(f"Using {len(proxies)} {args.proxy_type} proxies from {len(found_proxies)} total")
                else:
                    proxies = found_proxies
            else:
                print_warning_message("No working proxies found during harvesting")
    
    # Exit if we're only harvesting proxies
    if args.harvest_only:
        print_success_message("Proxy harvesting completed successfully")
        return
    
    # Select a proxy if available and requested
    if args.use_proxy and proxies:
        # Choose the best proxy by response time (with a touch of randomness)
        sorted_proxies = sorted(proxies, key=lambda x: float(x.get("response_time", 999)))
        
        # Select from the top 3 proxies (or all if less than 3)
        top_n = min(3, len(sorted_proxies))
        selected_index = random.randint(0, top_n - 1) if top_n > 1 else 0
        proxy = sorted_proxies[selected_index]
        
        print_success_message(f"Selected proxy: {proxy.get('http', 'unknown')} - Response time: {proxy.get('response_time', 'unknown')}s")
    
    # Run the scraper
    print_system_message(f"Starting Google Maps scraper for query: {args.query}")
    if args.location:
        print_info_message(f"Location filter: {args.location}")
    print_info_message(f"Browser mode: {'Headless' if args.headless else 'Visible'}")
    print_info_message(f"Maximum results: {args.max_results if args.max_results > 0 else 'Unlimited'}")
    
    success = run_with_proxy(
        query=args.query,
        location=args.location,
        output_dir=str(output_dir),
        headless=args.headless,
        max_results=args.max_results,
        proxy=proxy
    )
    
    if success:
        print_success_message("Google Maps scraping completed successfully")
    else:
        print_error_message("Google Maps scraping failed")
        
        # Try without proxy if using proxy and failed
        if args.use_proxy and proxy:
            print_warning_message("Trying again without proxy...")
            success = run_with_proxy(
                query=args.query,
                location=args.location,
                output_dir=str(output_dir),
                headless=args.headless,
                max_results=args.max_results,
                proxy=None
            )
            
            if success:
                print_success_message("Google Maps scraping completed successfully without proxy")
            else:
                print_error_message("Google Maps scraping failed even without proxy")


if __name__ == "__main__":
    main()
