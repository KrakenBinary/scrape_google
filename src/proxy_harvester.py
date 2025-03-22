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
import json
import re
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
        
        # HTML table-based proxy sources
        self.html_proxy_sources = [
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            "https://www.sslproxies.org/",
            "https://www.proxy-list.download/HTTP",
            "https://hidemy.name/en/proxy-list/?type=s&anon=1",
            "https://spys.one/en/free-proxy-list/"
        ]
        
        # JSON API-based proxy sources
        self.api_proxy_sources = [
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&country=US",
            "https://www.proxyscan.io/api/proxy?format=json&country=US&limit=20"
        ]
        
        # Raw text-based proxy sources (GitHub repositories, etc.)
        self.text_proxy_sources = [
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt"
        ]
        
        # Default timeout and test URLs
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://icanhazip.com",
            "https://api.myip.com"
        ]
        self.timeout = 5  # Timeout in seconds for proxy tests
        self.max_workers = 50  # Number of concurrent proxy tests - increased from 20
        self.max_proxies_per_source = 100  # Limit proxies per source to avoid processing too many
        self.min_speed_threshold = 5.0  # Max seconds for a proxy to be considered "fast"
        
        # Use user-agents to mimic real browsers when testing proxies
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]
        
        # For external anonymity checking
        self.proxy_judge_urls = [
            "https://www.whatismyip.com/",
            "https://www.whatismyip.com/my-ip-information/"
        ]
        
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
        print_system_message(f"Commencing proxy extraction from {len(self.html_proxy_sources) + len(self.api_proxy_sources) + len(self.text_proxy_sources)} digital endpoints...")
        
        # Process HTML table-based sources
        print_system_message("Extracting proxies from HTML sources...")
        for source in self.html_proxy_sources:
            proxies = self._scrape_free_proxy_list(source)
            if len(proxies) > self.max_proxies_per_source:
                print_info_message(f"Limiting proxies from {source} to {self.max_proxies_per_source}")
                proxies = proxies[:self.max_proxies_per_source]
            all_proxies.extend(proxies)
            
        # Process API-based sources
        print_system_message("Extracting proxies from API sources...")
        for source in self.api_proxy_sources:
            proxies = self._scrape_api_source(source)
            if len(proxies) > self.max_proxies_per_source:
                proxies = proxies[:self.max_proxies_per_source]
            all_proxies.extend(proxies)
            
        # Process text-based sources
        print_system_message("Extracting proxies from text-based sources...")
        for source in self.text_proxy_sources:
            proxies = self._scrape_text_source(source)
            if len(proxies) > self.max_proxies_per_source:
                proxies = proxies[:self.max_proxies_per_source]
            all_proxies.extend(proxies)
        
        # Remove duplicates based on IP:port
        unique_proxies = []
        seen = set()
        for proxy in all_proxies:
            key = proxy.get('http', '')
            if key and key not in seen:
                seen.add(key)
                unique_proxies.append(proxy)
        
        print_success_message(f"Extracted {len(unique_proxies)} unique proxies for testing")
        return unique_proxies
    
    def _scrape_api_source(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape proxies from API endpoint sources that return JSON.
        
        Args:
            url: URL of the API endpoint
            
        Returns:
            List of proxy dictionaries
        """
        proxies = []
        try:
            print_info_message(f"Intercepting digital signals from API: {url}")
            
            # Random user agent for request
            headers = {"User-Agent": random.choice(self.user_agents)}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print_warning_message(f"API returned status {response.status_code} for {url}")
                return []
                
            # Parse JSON response - handle different API structures
            data = response.json()
            
            # Handle GeoNode API structure
            if "geonode" in url:
                if isinstance(data, dict) and "data" in data:
                    items = data["data"]
                    for item in items:
                        # Skip if not matching country filter
                        if self.country_filter != "ALL" and item.get("country", "").upper() != self.country_filter:
                            continue
                            
                        ip = item.get("ip")
                        port = item.get("port")
                        if ip and port:
                            proxy_str = f"{ip}:{port}"
                            proxy_dict = {
                                "ip": ip,
                                "port": port,
                                "country": item.get("country", "Unknown"),
                                "https": item.get("protocols", {}).get("https", False),
                                "source": url,
                                "http": f"http://{proxy_str}"
                            }
                            if proxy_dict["https"]:
                                proxy_dict["https"] = f"https://{proxy_str}"
                            
                            proxies.append(proxy_dict)
            
            # Handle ProxyScan API structure
            elif "proxyscan" in url:
                if isinstance(data, list):
                    for item in data:
                        ip = item.get("Ip")
                        port = item.get("Port")
                        country = item.get("Country", {}).get("Code", "Unknown")
                        
                        # Skip if not matching country filter
                        if self.country_filter != "ALL" and country != self.country_filter:
                            continue
                            
                        if ip and port:
                            proxy_str = f"{ip}:{port}"
                            proxy_dict = {
                                "ip": ip,
                                "port": port,
                                "country": country,
                                "https": "Https" in item.get("Type", []),
                                "source": url,
                                "http": f"http://{proxy_str}"
                            }
                            if proxy_dict["https"]:
                                proxy_dict["https"] = f"https://{proxy_str}"
                            
                            proxies.append(proxy_dict)
            
            # Handle generic JSON structures
            else:
                # Try to extract proxies with best-effort parsing
                if isinstance(data, list):
                    for item in data:
                        # Try to find IP and port in the item
                        ip = item.get("ip", item.get("host", item.get("addr", None)))
                        port = item.get("port", None)
                        
                        if ip and port:
                            proxy_str = f"{ip}:{port}"
                            proxy_dict = {
                                "ip": ip,
                                "port": port,
                                "country": item.get("country", "Unknown"),
                                "https": item.get("https", False) or item.get("ssl", False),
                                "source": url,
                                "http": f"http://{proxy_str}"
                            }
                            if proxy_dict["https"]:
                                proxy_dict["https"] = f"https://{proxy_str}"
                            
                            proxies.append(proxy_dict)
                            
            print_info_message(f"Decoded {len(proxies)} potential proxies from API: {url}")
            
        except Exception as e:
            print_error_message(f"API interception failed at {url}: {e}")
            
        return proxies
    
    def _scrape_text_source(self, url: str) -> List[Dict[str, str]]:
        """
        Scrape proxies from plain text sources (usually GitHub repositories).
        
        Args:
            url: URL of the plain text proxy list
            
        Returns:
            List of proxy dictionaries
        """
        proxies = []
        try:
            print_info_message(f"Intercepting digital signals from text source: {url}")
            
            # Random user agent for request
            headers = {"User-Agent": random.choice(self.user_agents)}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print_warning_message(f"Text source returned status {response.status_code} for {url}")
                return []
            
            # Common patterns for proxy strings
            ip_port_pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)')
            
            # Process each line
            for line in response.text.splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Try to match IP:PORT pattern
                match = ip_port_pattern.search(line)
                if match:
                    ip, port = match.groups()
                    proxy_str = f"{ip}:{port}"
                    
                    # Try to extract country if present
                    country = "Unknown"
                    if " " in line and len(line.split()) >= 3:
                        # Some formats have country after IP:PORT
                        parts = line.split()
                        for part in parts:
                            if len(part) == 2 and part.isupper():
                                country = part
                                break
                    
                    proxy_dict = {
                        "ip": ip,
                        "port": port,
                        "country": country,
                        "https": False,  # Default to HTTP only
                        "source": url,
                        "http": f"http://{proxy_str}"
                    }
                    
                    # Check if HTTPS is mentioned in the line
                    if "https" in line.lower() or "ssl" in line.lower():
                        proxy_dict["https"] = f"https://{proxy_str}"
                        proxy_dict["https"] = True
                    
                    proxies.append(proxy_dict)
            
            print_info_message(f"Decoded {len(proxies)} potential proxies from text source: {url}")
            
        except Exception as e:
            print_error_message(f"Text source interception failed at {url}: {e}")
            
        return proxies
    
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
            
        # Randomly select a user-agent
        user_agent = random.choice(self.user_agents)
        headers = {
            "User-Agent": user_agent
        }
        
        start_time = time.time()
        try:
            response = requests.get(test_url, proxies=proxies, headers=headers, timeout=self.timeout)
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
                
                # Perform anonymity check
                anonymity_level = self._check_anonymity(proxy, returned_ip)
                
                # Update proxy with test results
                proxy["working"] = True
                proxy["returned_ip"] = returned_ip
                proxy["response_time"] = round(response_time, 2)
                proxy["anonymity"] = anonymity_level
                proxy["speed_category"] = self._categorize_speed(response_time)
                proxy["last_checked"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                return proxy
        except requests.exceptions.ConnectTimeout:
            # Specific timeout error
            return None
        except requests.exceptions.ProxyError:
            # Specific proxy error
            return None
        except Exception as e:
            # Log specific error type for debugging
            # print_error_message(f"Proxy test failed: {type(e).__name__}: {str(e)}")
            pass
            
        return None
        
    def _check_anonymity(self, proxy: Dict[str, str], returned_ip: str) -> str:
        """
        Determine the anonymity level of a proxy based on returned IP.
        
        Args:
            proxy: Proxy dictionary
            returned_ip: IP returned from test request
            
        Returns:
            Anonymity level: 'elite', 'anonymous', 'transparent'
        """
        proxy_ip = proxy.get("ip", "")
        
        # If returned IP is different from proxy IP and not our real IP
        # (we can't easily determine our real IP here, but we can check if it's different)
        if returned_ip != proxy_ip and returned_ip != "unknown":
            return "elite"  # Elite proxy: origin IP not revealed
        elif returned_ip == proxy_ip:
            return "anonymous"  # Anonymous proxy: uses its own IP
        else:
            return "transparent"  # Transparent proxy: reveals original IP
            
    def _categorize_speed(self, response_time: float) -> str:
        """
        Categorize proxy speed based on response time.
        
        Args:
            response_time: Response time in seconds
            
        Returns:
            Speed category: 'fast', 'medium', 'slow'
        """
        if response_time < 1.0:
            return "fast"
        elif response_time < 3.0:
            return "medium"
        else:
            return "slow"
    
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
        fieldnames = ["http", "https", "ip", "port", "country", "returned_ip", "response_time", "anonymity", "speed_category", "last_checked", "source"]
        
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
                    "metadata": {
                        "timestamp": self.timestamp,
                        "country_filter": self.country_filter,
                        "total_count": len(proxies),
                        "fast_count": len([p for p in proxies if p.get("speed_category") == "fast"]),
                        "elite_count": len([p for p in proxies if p.get("anonymity") == "elite"]),
                        "https_count": len([p for p in proxies if p.get("https")]),
                        "sources": list(set(p.get("source", "unknown") for p in proxies))
                    }
                }
                json.dump(data, jsonfile, indent=2)
                
            print_success_message(f"Digital asset secured: {len(proxies)} proxies saved to {filepath}")
            print_info_message(f"Speed metrics: {data['metadata']['fast_count']} fast, {len(proxies) - data['metadata']['fast_count']} standard")
            print_info_message(f"Security metrics: {data['metadata']['elite_count']} elite, {data['metadata']['https_count']} HTTPS-capable")
            
            # Also save to the standard location for TryloByte
            standard_path = self.output_dir / "proxies.json"
            with open(standard_path, "w") as std_file:
                json.dump(data, std_file, indent=2)
                
            print_info_message(f"Proxy database updated: {standard_path}")
            
            return str(filepath)
        except Exception as e:
            print_error_message(f"Failed to save JSON: {e}")
            return ""
    
    def select_best_proxies(self, proxies: List[Dict[str, str]], count: int = 10) -> List[Dict[str, str]]:
        """
        Select the best proxies based on speed, anonymity, and HTTPS support.
        
        Args:
            proxies: List of working proxy dictionaries
            count: Number of proxies to select
            
        Returns:
            List of the best proxies
        """
        if not proxies:
            return []
            
        # Create a scoring system
        for proxy in proxies:
            score = 0
            
            # Speed score (0-50 points)
            response_time = proxy.get("response_time", 999)
            if response_time < 0.5:
                score += 50
            elif response_time < 1.0:
                score += 40
            elif response_time < 2.0:
                score += 30
            elif response_time < 3.0:
                score += 20
            else:
                score += 10
                
            # Anonymity score (0-30 points)
            anonymity = proxy.get("anonymity", "transparent")
            if anonymity == "elite":
                score += 30
            elif anonymity == "anonymous":
                score += 20
            else:
                score += 10
                
            # HTTPS support (0-20 points)
            if proxy.get("https"):
                score += 20
                
            proxy["score"] = score
            
        # Sort by score (highest first)
        sorted_proxies = sorted(proxies, key=lambda x: x.get("score", 0), reverse=True)
        
        # Take the top 'count' proxies
        best_proxies = sorted_proxies[:count]
        
        print_success_message(f"Selected {len(best_proxies)} optimal proxies from pool of {len(proxies)}")
        return best_proxies

    def run(self) -> Tuple[List[Dict[str, str]], str, str]:
        """
        Run the full proxy harvesting process.
        
        Returns:
            Tuple of (working_proxies, csv_path, json_path)
        """
        try:
            print_system_message("Initializing proxy harvesting sequence...")
            print_system_message("Dispatching digital scouts to locate proxies...")
            
            # Scrape proxies from all sources
            all_proxies = self.scrape_all_sources()
            
            if not all_proxies:
                print_error_message("No proxies found from any source. Extraction failed.")
                return [], "", ""
                
            # Test all proxies
            working_proxies = self.test_proxies(all_proxies)
            
            if not working_proxies:
                print_error_message("No working proxies found. All tested proxies failed validation.")
                return [], "", ""
                
            # Select best proxies for TryloByte
            best_proxies = self.select_best_proxies(working_proxies)
                
            # Save results to CSV and JSON
            csv_path = self.save_to_csv(working_proxies)
            json_path = self.save_to_json(best_proxies)
            
            print_system_message("Proxy harvesting sequence completed!")
            print_success_message(f"Final results: {len(working_proxies)} working proxies, {len(best_proxies)} optimal proxies selected for TryloByte")
            
            return best_proxies, csv_path, json_path
            
        except Exception as e:
            print_error_message(f"Proxy harvesting operation failed: {str(e)}")
            return [], "", ""
    
def main():
    """Run the proxy harvester as a standalone script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="TryloByte Proxy Harvester")
    parser.add_argument("--output-dir", default="../data", help="Directory to save output files")
    parser.add_argument("--country", default="US", help="Country filter (use 'ALL' for no filter)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds for proxy tests")
    parser.add_argument("--workers", type=int, default=50, help="Maximum number of concurrent proxy tests")
    
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
