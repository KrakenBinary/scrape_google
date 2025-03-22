#!/usr/bin/env python3
import json
import argparse
import random
from pathlib import Path
from typing import Dict, Optional, List

from proxy_harvester import ProxyHarvester
from google_maps_scraper import GoogleMapsScraper
from common.logger import (
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
        scraper = GoogleMapsScraper(
            output_dir=output_dir,
            headless=headless,
            proxy=proxy,
            max_results=max_results
        )
        
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
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle proxy options
    if args.use_proxy or args.harvest_only:
        print_system_message("Initializing proxy handling...")
        
        # Load proxies from file if specified
        if args.proxy_file:
            print_info_message(f"Loading proxies from {args.proxy_file}")
            proxies = load_proxies(args.proxy_file, args.proxy_type)
        else:
            # Harvest new proxies
            print_info_message(f"Harvesting new proxies with country filter: {args.country_filter}")
            harvester = ProxyHarvester(output_dir=str(output_dir), country_filter=args.country_filter)
            proxies, _, _ = harvester.run()
        
        if args.harvest_only:
            print_success_message("Proxy harvesting complete. Exiting.")
            return
        
        if not proxies:
            print_error_message("No usable proxies found. Running without proxy.")
            proxy = None
        else:
            # Select a random proxy
            proxy = random.choice(proxies)
            print_success_message(f"Selected proxy: {proxy.get('http', 'Unknown')} (Speed: {proxy.get('speed_category', 'Unknown')}, Anonymity: {proxy.get('anonymity', 'Unknown')})")
    else:
        proxy = None
    
    # Run the scraper
    print_system_message(f"Starting Google Maps scraper for: {args.query}" + (f" in {args.location}" if args.location else ""))
    
    success = run_with_proxy(
        query=args.query,
        location=args.location,
        output_dir=str(output_dir),
        headless=args.headless,
        max_results=args.max_results,
        proxy=proxy
    )
    
    if success:
        print_success_message("Google Maps scraping completed successfully!")
    else:
        print_error_message("Google Maps scraping failed.")
        
        # If using proxy and it failed, try without proxy
        if proxy:
            print_info_message("Trying again without proxy...")
            success = run_with_proxy(
                query=args.query,
                location=args.location,
                output_dir=str(output_dir),
                headless=args.headless,
                max_results=args.max_results,
                proxy=None
            )
            
            if success:
                print_success_message("Google Maps scraping completed successfully without proxy!")
            else:
                print_error_message("Google Maps scraping failed even without proxy.")

if __name__ == "__main__":
    main()
