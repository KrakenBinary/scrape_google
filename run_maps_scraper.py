#!/usr/bin/env python3
"""
Entry point script for running the Google Maps scraper.
This script ensures proper import paths regardless of how it's invoked.
"""
import sys
import os
import argparse
import traceback
import json
import random
from pathlib import Path

# Add the project root to the Python path to ensure all imports work correctly
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.scrapers.google_maps_scraper import GoogleMapsScraper
from src.proxy_harvester import ProxyHarvester
from src.common.logger import (
    print_system_message,
    print_info_message,
    print_success_message,
    print_warning_message,
    print_error_message
)

def main():
    """Main function to run Google Maps scraper with command line arguments"""
    parser = argparse.ArgumentParser(description="Google Maps Scraper")
    parser.add_argument("query", help="Search query for Google Maps")
    parser.add_argument("--location", "-l", help="Location for the search")
    parser.add_argument("--output", "-o", default="data", help="Output directory for scraped data")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--max-results", "-m", type=int, default=0, help="Maximum number of results to scrape (0 = unlimited)")
    parser.add_argument("--use-proxy", "-p", action="store_true", help="Use a proxy from the proxy harvester")
    parser.add_argument("--proxy-file", help="Load proxies from this file instead of harvesting new ones")
    parser.add_argument("--proxy-type", choices=["elite", "anonymous", "all"], default="elite", 
                        help="Type of proxy to use (elite, anonymous, all)")
    
    args = parser.parse_args()
    
    # Set process title to help with identification
    try:
        import setproctitle
        setproctitle.setproctitle(f"tryloByte_scraper-{args.query}")
    except ImportError:
        # Not critical if this fails, just continue without setting the process title
        pass
    
    print_system_message(f"Initializing Google Maps scraper for query: {args.query}")
    
    # Handle proxy configuration
    proxy = None
    proxy_config = None
    
    if args.use_proxy:
        print_info_message("Setting up proxy configuration...")
        
        if args.proxy_file:
            # Load proxies from file
            proxy_file = Path(args.proxy_file)
            
            if proxy_file.exists():
                try:
                    with open(proxy_file, "r") as f:
                        proxies = json.load(f)
                        
                    if isinstance(proxies, list) and len(proxies) > 0:
                        # Filter by proxy type if needed
                        if args.proxy_type != "all":
                            proxies = [p for p in proxies if p.get("type", "").lower() == args.proxy_type.lower()]
                        
                        if proxies:
                            # Choose a random proxy
                            proxy_data = random.choice(proxies)
                            proxy = {"http": f"http://{proxy_data['ip']}:{proxy_data['port']}"}
                            print_info_message(f"Using proxy: {proxy['http']}")
                        else:
                            print_warning_message(f"No {args.proxy_type} proxies found in the file")
                    else:
                        print_warning_message("Invalid proxy file format or empty proxy list")
                
                except Exception as e:
                    print_warning_message(f"Error loading proxies from file: {str(e)}")
            else:
                print_warning_message(f"Proxy file not found: {args.proxy_file}")
        
        if not proxy:
            # Harvest new proxies
            print_info_message("Harvesting proxies...")
            
            try:
                harvester = ProxyHarvester()
                proxies = harvester.harvest_and_test(limit=5, proxy_type=args.proxy_type)
                
                if proxies:
                    # Use the best proxy
                    best_proxy = proxies[0]
                    proxy = {"http": f"http://{best_proxy['ip']}:{best_proxy['port']}"}
                    proxy_config = {"http": f"http://{best_proxy['ip']}:{best_proxy['port']}"}
                    print_info_message(f"Using harvested proxy: {best_proxy['ip']}:{best_proxy['port']}")
                else:
                    print_warning_message("No working proxies found. Running without proxy.")
            except Exception as e:
                print_warning_message(f"Error harvesting proxies: {str(e)}")
                print_warning_message("Running without proxy.")
    
    # Configure browser options for optimal stability
    browser_options = {
        'undetected': True,  # Use undetected Chrome driver
        'chrome_arguments': {
            'disable-features': 'VizDisplayCompositor,IsolateOrigins,site-per-process'
        }
    }
    
    # Configure scraper
    try:
        # Initialize the scraper
        scraper = GoogleMapsScraper(
            output_dir=args.output,
            headless=args.headless,
            max_results=args.max_results,
            proxy=proxy_config  # Pass proxy during initialization
        )
        
        # Setup the scraper with appropriate options
        success = scraper.setup(
            headless=args.headless,
            proxy=proxy,
            location=args.location,
            **browser_options
        )
        
        if success:
            # Run the scraper
            data, output_file = scraper.run(args.query, args.location)
            
            if data:
                print_success_message(f"Successfully scraped {len(data)} businesses")
                print_success_message(f"Data saved to: {output_file}")
                return 0
            else:
                print_error_message("Scraping failed or no results found")
                return 1
        else:
            print_error_message("Failed to setup scraper")
            return 1
        
    except KeyboardInterrupt:
        print_warning_message("\nScraping interrupted by user")
        
        # Save any data collected so far
        if 'scraper' in locals() and hasattr(scraper, 'data') and scraper.data:
            try:
                # Generate output filename
                output_file = scraper.save_data(scraper.data)
                print_success_message(f"Successfully saved {len(scraper.data)} businesses collected before interruption")
                print_success_message(f"Data saved to: {output_file}")
            except Exception as e:
                print_error_message(f"Error saving data before exit: {str(e)}")
        
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print_error_message(f"Error during scraping: {str(e)}")
        print_error_message(traceback.format_exc())
        return 1
    finally:
        # Ensure resources are cleaned up
        try:
            if 'scraper' in locals():
                scraper.cleanup()
        except Exception:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
