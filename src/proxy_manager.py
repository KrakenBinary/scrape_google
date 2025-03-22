#!/usr/bin/env python3
"""Proxy manager for handling proxy rotation and testing."""

import os
import time
import random
import requests
import json
import csv
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

# Import the new proxy harvester
from src.proxy_harvester import ProxyHarvester

class ProxyManager:
    """Manages proxy retrieval, testing, and rotation."""

    def __init__(self, proxy_test_url: str = "http://httpbin.org/ip", target_proxy_count: int = 5,
                 proxy_cache_dir: str = "../data"):
        """
        Initialize the proxy manager.
        
        Args:
            proxy_test_url: URL to use for testing proxies
            target_proxy_count: Desired number of working proxies
            proxy_cache_dir: Directory to store/read cached proxies
        """
        self.proxy_test_url = proxy_test_url
        self.target_proxy_count = target_proxy_count
        self.proxy_cache_dir = Path(proxy_cache_dir)
        
        self.proxy_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize proxy lists
        self.working_proxies = []
        self.blacklisted_proxies = []
        self.proxy_index = 0
        
        # Loading proxy settings
        self.consecutive_proxy_failures = 0
        self.max_proxy_failures = 3  # After this many failures, try direct connection
        self.allow_direct_connection = True  # Whether to allow direct connection if all proxies fail
        
        # Try to load proxies from cache first
        self._load_proxies_from_cache()

    def _load_proxies_from_cache(self):
        """Load proxies from previously saved CSV or JSON files."""
        # Look for proxy files in the cache directory, newest first
        proxy_files = list(self.proxy_cache_dir.glob("working_proxies_*.csv")) + \
                     list(self.proxy_cache_dir.glob("working_proxies_*.json"))
        
        if not proxy_files:
            print("No cached proxy files found.")
            return False
        
        # Sort by modification time, newest first
        proxy_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        newest_proxy_file = proxy_files[0]
        
        # Check if the file is recent (less than 24 hours old)
        file_age = time.time() - newest_proxy_file.stat().st_mtime
        if file_age > 86400:  # 24 hours in seconds
            print(f"Cached proxy file {newest_proxy_file.name} is older than 24 hours.")
            return False
        
        # Load the proxies
        if newest_proxy_file.suffix == '.csv':
            return self._load_from_csv(newest_proxy_file)
        elif newest_proxy_file.suffix == '.json':
            return self._load_from_json(newest_proxy_file)
        
        return False

    def _load_from_csv(self, csv_path: Path) -> bool:
        """Load proxies from a CSV file."""
        try:
            with open(csv_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                proxies = list(reader)
                
                if not proxies:
                    return False
                
                # Convert to our format
                self.working_proxies = proxies
                print(f"Loaded {len(self.working_proxies)} proxies from {csv_path}")
                return True
        except Exception as e:
            print(f"Error loading proxies from CSV: {e}")
            return False

    def _load_from_json(self, json_path: Path) -> bool:
        """Load proxies from a JSON file."""
        try:
            with open(json_path, 'r') as jsonfile:
                data = json.load(jsonfile)
                
                if 'working_proxies' in data:
                    self.working_proxies = data['working_proxies']
                    
                if 'blacklisted_proxies' in data:
                    self.blacklisted_proxies = data['blacklisted_proxies']
                
                print(f"Loaded {len(self.working_proxies)} proxies from {json_path}")
                return len(self.working_proxies) > 0
        except Exception as e:
            print(f"Error loading proxies from JSON: {e}")
            return False

    def refresh_proxies(self) -> bool:
        """
        Refresh the proxy list by running the proxy harvester.
        
        Returns:
            True if successful, False otherwise
        """
        print("Running proxy harvester to refresh proxy list...")
        harvester = ProxyHarvester(output_dir=str(self.proxy_cache_dir))
        working_proxies, csv_path, json_path = harvester.run()
        
        if working_proxies:
            self.working_proxies = working_proxies
            self.proxy_index = 0
            return True
        
        return False

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get the next working proxy to use.
        
        Returns:
            Proxy dictionary or None if no proxies are available
        """
        # Check if we should use direct connection
        if self.consecutive_proxy_failures >= self.max_proxy_failures and self.allow_direct_connection:
            print(f"Using direct connection after {self.consecutive_proxy_failures} consecutive proxy failures")
            return {"direct": True}
        
        # If no working proxies, try to refresh
        if not self.working_proxies:
            proxies_loaded = self._load_proxies_from_cache()
            if not proxies_loaded:
                if not self.refresh_proxies():
                    if self.allow_direct_connection:
                        print("No working proxies available. Using direct connection.")
                        return {"direct": True}
                    return None
        
        # Return None if there are still no working proxies
        if not self.working_proxies:
            return None
        
        # Get the next proxy
        if self.proxy_index >= len(self.working_proxies):
            self.proxy_index = 0
        
        proxy = self.working_proxies[self.proxy_index]
        self.proxy_index += 1
        
        return proxy

    def test_proxy(self, proxy: Dict[str, str]) -> bool:
        """
        Test if a proxy is working.
        
        Args:
            proxy: Proxy dictionary
            
        Returns:
            True if the proxy is working, False otherwise
        """
        # If direct connection, no need to test
        if proxy.get('direct', False):
            return True
            
        proxies = {}
        if 'http' in proxy:
            proxies['http'] = proxy['http']
        if 'https' in proxy:
            proxies['https'] = proxy['https']
        
        try:
            response = requests.get(self.proxy_test_url, proxies=proxies, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def blacklist_proxy(self, proxy: Dict[str, str]):
        """
        Blacklist a non-working proxy.
        
        Args:
            proxy: Proxy dictionary to blacklist
        """
        # If direct connection, nothing to blacklist
        if proxy.get('direct', False):
            return
            
        # Add to blacklist if not already there
        if proxy not in self.blacklisted_proxies:
            self.blacklisted_proxies.append(proxy)
        
        # Remove from working proxies
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            
        # Save the updated blacklist
        self._save_proxy_lists()

    def _save_proxy_lists(self):
        """Save the current proxy lists to a JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"proxy_state_{timestamp}.json"
            filepath = self.proxy_cache_dir / filename
            
            data = {
                "working_proxies": self.working_proxies,
                "blacklisted_proxies": self.blacklisted_proxies,
                "timestamp": timestamp
            }
            
            with open(filepath, "w") as jsonfile:
                json.dump(data, jsonfile, indent=2)
        except Exception as e:
            print(f"Error saving proxy lists: {e}")

    def report_proxy_failure(self, proxy: Dict[str, str]):
        """
        Report a proxy failure and increment the consecutive failure counter.
        
        Args:
            proxy: The failed proxy
        """
        self.consecutive_proxy_failures += 1
        self.blacklist_proxy(proxy)
        
    def report_proxy_success(self):
        """Reset the consecutive failure counter after a successful proxy use."""
        self.consecutive_proxy_failures = 0
