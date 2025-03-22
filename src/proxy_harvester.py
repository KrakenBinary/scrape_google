#!/usr/bin/env python3
"""Standalone proxy harvester module for TryloByte.

This module scrapes free proxies from various sources, tests them,
and saves working proxies to a CSV file for later use.
"""

import csv
import time
import threading
import requests
from bs4 import BeautifulSoup
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime

# Import the console output module for consistent styling
try:
    from console_output import (
        print_system_message, print_info_message, print_warning_message,
        print_error_message, print_success_message
    )
except ImportError:
    # Fallback console output functions if not running inside TryloByte
    def print_system_message(message): print(f"[ SYSTEM ] {message}")
    def print_info_message(message): print(f"[ INFO ] {message}")
    def print_warning_message(message): print(f"[ WARNING ] {message}")
    def print_error_message(message): print(f"[ ERROR ] {message}")
    def print_success_message(message): print(f"[ SUCCESS ] {message}")

class ProxyHarvester:
    """Harvests working proxies from various free proxy sources."""
    
    def __init__(self, output_dir: str = "../data", country_filter: str = "US"):
        """
        Initialize the proxy harvester.
        
        Args:
            output_dir: Directory to save the CSV file
            country_filter: Only include proxies from this country ('ALL' for no filter)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.country_filter = country_filter
        self.proxy_sources = [
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            "https://www.sslproxies.org/"
        ]
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://icanhazip.com",
            "https://api.myip.com"
        ]
        self.timeout = 5  # Timeout in seconds for proxy tests
        self.max_workers = 20  # Number of concurrent proxy tests
        
        # Timestamp for output files
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _scrape_free_proxy_list(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape proxies from free-proxy-list.net and similar sites.
        
        Args:
            url: URL of the proxy list website
            
        Returns:
            List of proxy dictionaries with format {'http': 'http://ip:port'}
        """
        proxies = []
        try:
            print_info_message(f"Intercepting digital signals from {url}")
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the proxy table
            table = soup.find("table", {"id": "proxylisttable"})
            if not table:
                table = soup.find("table", class_="table")
            
            if not table:
                print_warning_message(f"No proxy data detected at {url}")
                return []
                
            # Parse rows
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 8:  # Ensure row has enough data
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    country_code = cols[2].text.strip()
                    https = cols[6].text.strip().lower() == 'yes'
                    
                    # Apply country filter if specified
                    if self.country_filter != "ALL" and country_code != self.country_filter:
                        continue
                    
                    proxy_str = f"{ip}:{port}"
                    proxy_dict = {
                        "ip": ip,
                        "port": port,
                        "country": country_code,
                        "https": https,
                        "source": url,
                        "http": f"http://{proxy_str}"
                    }
                    if https:
                        proxy_dict["https"] = f"https://{proxy_str}"
                    
                    proxies.append(proxy_dict)
            
            print_info_message(f"Decoded {len(proxies)} potential {self.country_filter} proxies from {url}")
            return proxies
            
        except Exception as e:
            print_error_message(f"Digital signal interception failed at {url}: {e}")
            return []
    
    def scrape_all_sources(self) -> List[Dict[str, str]]:
        """
        Scrape proxies from all configured sources.
        
        Returns:
            Combined list of proxies from all sources
        """
        all_proxies = []
        print_system_message(f"Commencing proxy extraction from {len(self.proxy_sources)} digital endpoints...")
        
        for source in self.proxy_sources:
            proxies = self._scrape_free_proxy_list(source)
            all_proxies.extend(proxies)
        
        # Remove duplicates based on IP:port
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            key = proxy['http']
            if key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print_success_message(f"Extracted {len(unique_proxies)} unique proxies for testing")
        return unique_proxies
    
    def test_proxy(self, proxy: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Test if a proxy is working by making a request through it.
        
        Args:
            proxy: Proxy dictionary with format {'http': 'http://ip:port'}
            
        Returns:
            Updated proxy dict with 'working' and 'response_time' fields if working, None otherwise
        """
        # Select a random test URL
        test_url = random.choice(self.test_urls)
        proxies = {
            "http": proxy["http"]
        }
        if "https" in proxy:
            proxies["https"] = proxy["https"]
            
        start_time = time.time()
        try:
            response = requests.get(test_url, proxies=proxies, timeout=self.timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # For httpbin.org, check if the origin IP matches the proxy IP
                if "httpbin.org" in test_url:
                    returned_ip = response.json().get('origin', '').split(',')[0]
                # For icanhazip.com
                elif "icanhazip.com" in test_url:
                    returned_ip = response.text.strip()
                # For api.myip.com
                elif "myip.com" in test_url:
                    returned_ip = response.json().get('ip', '')
                else:
                    returned_ip = "unknown"
                
                proxy["working"] = True
                proxy["returned_ip"] = returned_ip
                proxy["response_time"] = round(response_time, 2)
                return proxy
        except Exception:
            pass  # Proxy failed
            
        return None
    
    def test_proxies(self, proxies: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Test multiple proxies in parallel.
        
        Args:
            proxies: List of proxy dictionaries
            
        Returns:
            List of working proxy dictionaries
        """
        working_proxies = []
        proxy_count = len(proxies)
        
        print_system_message(f"Testing {proxy_count} digital proxies for viability...")
        print_info_message(f"Expected completion time: ~{max(1, proxy_count // self.max_workers)} seconds")
        
        # Use ThreadPoolExecutor for concurrent testing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_proxy = {executor.submit(self.test_proxy, proxy): proxy for proxy in proxies}
            
            tested = 0
            for future in as_completed(future_to_proxy):
                tested += 1
                if tested % 10 == 0 or tested == proxy_count:
                    print_info_message(f"Tested {tested}/{proxy_count} proxies")
                    
                result = future.result()
                if result:
                    working_proxies.append(result)
                    print_success_message(f"Found working proxy: {result['http']} ({result['country']}) - {result['response_time']}s")
        
        # Sort by response time (fastest first)
        working_proxies.sort(key=lambda x: x.get('response_time', 999))
        
        if working_proxies:
            print_success_message(f"Validation complete: {len(working_proxies)}/{proxy_count} proxies operational")
        else:
            print_warning_message("No operational proxies found during testing phase")
            
        return working_proxies
    
    def save_to_csv(self, proxies: List[Dict[str, str]]) -> str:
        """
        Save working proxies to a CSV file.
        
        Args:
            proxies: List of working proxy dictionaries
            
        Returns:
            Path to the saved CSV file
        """
        if not proxies:
            print_warning_message("No proxies to save")
            return ""
            
        # Create filename with timestamp
        filename = f"working_proxies_{self.country_filter.lower()}_{self.timestamp}.csv"
        filepath = self.output_dir / filename
        
        # Define CSV fields
        fieldnames = ["http", "https", "ip", "port", "country", "returned_ip", "response_time", "source"]
        
        try:
            with open(filepath, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for proxy in proxies:
                    # Only write specified fields
                    row = {field: proxy.get(field, "") for field in fieldnames}
                    writer.writerow(row)
            
            print_success_message(f"Proxy data exported to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print_error_message(f"Failed to save proxy data: {e}")
            return ""
    
    def save_to_json(self, proxies: List[Dict[str, str]]) -> str:
        """
        Save working proxies to a JSON file for use with TryloByte.
        
        Args:
            proxies: List of working proxy dictionaries
            
        Returns:
            Path to the saved JSON file
        """
        if not proxies:
            print_warning_message("No proxies to save")
            return ""
            
        # Create filename with timestamp
        filename = f"working_proxies_{self.country_filter.lower()}_{self.timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, "w") as jsonfile:
                data = {
                    "working_proxies": proxies,
                    "blacklisted_proxies": [],
                    "timestamp": self.timestamp,
                    "country_filter": self.country_filter
                }
                json.dump(data, jsonfile, indent=2)
            
            print_success_message(f"Proxy data exported to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print_error_message(f"Failed to save proxy data: {e}")
            return ""
    
    def run(self) -> Tuple[List[Dict[str, str]], str, str]:
        """
        Run the full proxy harvesting process.
        
        Returns:
            Tuple of (working_proxies, csv_path, json_path)
        """
        print_system_message("Initializing proxy harvesting sequence...")
        
        # Step 1: Scrape proxies from all sources
        all_proxies = self.scrape_all_sources()
        
        if not all_proxies:
            print_error_message("Proxy harvesting failed: No proxies found")
            return [], "", ""
        
        # Step 2: Test proxies
        working_proxies = self.test_proxies(all_proxies)
        
        if not working_proxies:
            print_warning_message("Proxy harvesting completed with no working proxies")
            return [], "", ""
        
        # Step 3: Save to CSV and JSON
        csv_path = self.save_to_csv(working_proxies)
        json_path = self.save_to_json(working_proxies)
        
        print_success_message(f"Proxy harvesting complete: {len(working_proxies)} operational proxies identified")
        return working_proxies, csv_path, json_path


def main():
    """Run the proxy harvester as a standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TryloByte Proxy Harvester")
    parser.add_argument("--output-dir", default="../data", help="Directory to save output files")
    parser.add_argument("--country", default="US", help="Country filter (use 'ALL' for no filter)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds for proxy tests")
    parser.add_argument("--workers", type=int, default=20, help="Maximum number of concurrent proxy tests")
    
    args = parser.parse_args()
    
    harvester = ProxyHarvester(
        output_dir=args.output_dir,
        country_filter=args.country
    )
    harvester.timeout = args.timeout
    harvester.max_workers = args.workers
    
    working_proxies, csv_path, json_path = harvester.run()
    
    if working_proxies:
        fastest = working_proxies[0]
        print_info_message(f"Fastest proxy: {fastest['http']} ({fastest['country']}) - {fastest['response_time']}s")


if __name__ == "__main__":
    main()
