#!/usr/bin/env python3
"""
TryloByte - A retro-styled Google Maps scraping tool.
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
import threading
import click

# Import the centralized console output module
from src.console_output import (
    print_message, print_with_typing_effect,
    print_system_message, print_info_message, print_warning_message,
    print_error_message, print_success_message, print_mission_message,
    system_message, info_message, warning_message, error_message, success_message,
    NEON_GREEN, INFO_CYAN, WARNING_YELLOW, ALERT_RED, SUCCESS_GREEN, RESET
)

# ASCII Art for the retro terminal interface
TRYLOBYTE_ASCII = r"""
 ████████╗██████╗ ██╗   ██╗██╗      ██████╗ ██████╗ ██╗   ██╗████████╗███████╗
 ╚══██╔══╝██╔══██╗╚██╗ ██╔╝██║     ██╔═══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝
    ██║   ██████╔╝ ╚████╔╝ ██║     ██║   ██║██████╔╝ ╚████╔╝    ██║   █████╗  
    ██║   ██╔══██╗  ╚██╔╝  ██║     ██║   ██║██╔══██╗  ╚██╔╝     ██║   ██╔══╝  
    ██║   ██║  ██║   ██║   ███████╗╚██████╔╝██████╔╝   ██║      ██║   ███████╗
    ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝    ╚═╝      ╚═╝   ╚══════╝
                                                                             
"""

HACKER_MESSAGES = [
    "Initializing cyber protocols...",
    "Bypassing security measures...",
    "Establishing neural connection...",
    "Decrypting access codes...",
    "Scanning digital perimeter...",
    "Loading stealth algorithms...",
    "Activating ghost protocol...",
    "Engaging quantum interface...",
    "Bypassing neural firewalls...",
    "Initializing data extraction routines...",
]

HACKER_SUCCESS_MESSAGES = [
    "Access granted! System compromised.",
    "Matrix connection established successfully.",
    "Digital barriers neutralized.",
    "Mainframe access achieved.",
    "Security protocols bypassed.",
    "System penetration complete.",
    "Neural interface synchronized.",
    "Quantum entanglement successful.",
    "Digital footprint minimized.",
    "Stealth protocols engaged.",
]

class TryloByteCLI:
    """Interactive command-line interface for TryloByte"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.running = True
        self.scraper_class = None
        self.config = {
            "headless": False,
            "browser": "chrome",
            "max_results": 0,
            "listings_per_proxy": 0,
            "output_dir": "data",
            "proxy_test_url": "http://httpbin.org/ip",
            "target_proxy_count": 10
        }
        
        # Create data directory if it doesn't exist
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        # Try to load config from file
        config_path = Path("config.json")
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    saved_config = json.load(f)
                    for key, value in saved_config.items():
                        if key in self.config:
                            self.config[key] = value
            except json.JSONDecodeError:
                pass
    
    def save_config(self):
        """Save configuration to a file"""
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    
    def start(self):
        """Start the CLI interface"""
        # Print ASCII art
        self.print_ascii_header()
        
        # Print welcome message
        print_system_message("Neural interface established. Welcome to the Matrix.")
        print_info_message("Type 'help' for command list or 'exit' to terminate session.")
        
        # Main command loop
        self.running = True
        while self.running:
            try:
                # Get user input with styled prompt
                command = input(f"{NEON_GREEN}>>{RESET} ")
                
                # Process command
                if command.strip():
                    self.process_command(command.strip())
            except KeyboardInterrupt:
                self.exit_handler()
                sys.exit(0)
            except EOFError:
                print("\nEnd of input. Terminating session...")
                self.running = False
                sys.exit(0)
            except Exception as e:
                print_with_typing_effect(f"{error_message} Unexpected exception: {e}", color=ALERT_RED)
    
    def print_ascii_header(self):
        """Print the ASCII art header for the application."""
        print()
        print(f"{NEON_GREEN}{TRYLOBYTE_ASCII}{RESET}")
        print()
        print(f"{NEON_GREEN}    [ Digital Reconnaissance System v1.0 ]{RESET}")
        print(f"{NEON_GREEN}    [ Initiating cyber-infiltration sequence... ]{RESET}")
        print(f"{NEON_GREEN}    [ Target: Google Maps | Status: ACTIVE ]{RESET}")
        print()
    
    def process_command(self, command_str):
        """Process a given command"""
        # Split command and args
        parts = command_str.strip().split(' ', 1)
        command = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        # Look up command in the command map
        if command in self.get_command_map():
            return self.get_command_map()[command](args)
        elif command:
            print_error_message(f"Unknown command: {command}", typing_effect=True)
            print_info_message("Type 'help' for available commands.", typing_effect=True)
        
        return True

    def cmd_harvest_proxies(self, args):
        """Harvest and test proxies for later use"""
        print_system_message("Initializing proxy harvesting sequence...", typing_effect=True)
        
        try:
            from src.proxy_harvester import ProxyHarvester
            
            # Parse arguments
            country = "US"  # Default to US
            
            if " --country=" in f" {args}":
                for part in args.split():
                    if part.startswith("--country="):
                        country = part.split("=")[1].strip()
                        print_info_message(f"Targeting proxies from: {country}")
            
            # Create and run the harvester
            harvester = ProxyHarvester(
                output_dir=self.config.get("output_dir", "../data"),
                country_filter=country
            )
            
            print_system_message("Dispatching digital scouts to locate proxies...")
            working_proxies, csv_path, json_path = harvester.run()
            
            if working_proxies:
                print_success_message(f"Proxy harvest successful: {len(working_proxies)} operational proxies identified")
                print_info_message(f"Data saved to:")
                print_info_message(f"  CSV: {csv_path}")
                print_info_message(f"  JSON: {json_path}")
                
                # Show some stats about the proxies
                if working_proxies:
                    fastest = min(working_proxies, key=lambda x: float(x.get('response_time', 999)))
                    print_success_message(f"Fastest proxy: {fastest.get('http', 'unknown')} ({fastest.get('country', 'unknown')}) - {fastest.get('response_time', 'unknown')}s")
            else:
                print_warning_message("Harvesting operation yielded no viable proxies")
                print_info_message("Try running again later or with a different country filter")
                
        except ImportError as e:
            print_error_message(f"Neural pathways corrupted: {e}", typing_effect=True)
            print_info_message("Run the 'setup' command to install dependencies", typing_effect=True)
        except Exception as e:
            print_error_message(f"Proxy harvesting operation failed: {e}", typing_effect=True)
    
    def get_command_map(self):
        """Get the command map for this instance"""
        return {
            "help": self.cmd_help,
            "exit": self.exit_handler,
            "quit": self.exit_handler,
            "bye": self.exit_handler,
            "setup": self.cmd_setup,
            "scrape": self.cmd_scrape,
            "search": self.cmd_scrape,  # Alias for scrape
            "version": self.cmd_version,
            "update": self.cmd_update,
            "config": self.cmd_config,
            "about": self.cmd_about,
            "clear": self.cmd_clear,
            "cls": self.cmd_clear,  # Alias for clear
            "info": self.cmd_info,
            "dance": self.cmd_easter_egg,
            "harvest": self.cmd_harvest_proxies,
            "proxies": self.cmd_harvest_proxies  # Alias for harvest
        }
    
    def cmd_help(self, args):
        """Show help information"""
        help_text = """
Available commands:
  help           - Show this help information
  scrape "query" - Scrape Google Maps for a query
                   Options: --no-headless, --debug, --disable-proxies
  harvest        - Harvest and test proxies for later use
                   Options: --country=XX (default: US)
  setup          - Install required dependencies
  config         - View or edit configuration
  update         - Check for updates
  version        - Show version information
  about          - About this program
  clear          - Clear the screen
  info           - System information
  exit           - Exit the program
"""
        print_info_message(help_text, typing_effect=False)
        return True
    
    def exit_handler(self):
        """Handle the exit command"""
        print_system_message("Terminating connection to the Matrix...", typing_effect=True)
        print_system_message("Disconnecting neural interface...", typing_effect=True)
        time.sleep(0.5)
        print_system_message("TryloByte shutting down. Connection terminated.", typing_effect=True)
        self.running = False
    
    def cmd_setup(self):
        """Setup the dependencies"""
        # Check if we're on a Debian-based system
        debian_based = is_debian_based()
        
        if check_environment():
            print_system_message("Digital environment already established.", typing_effect=True)
            
            # Check if our required modules are installed
            missing_modules = []
            required_modules = [
                "selenium", "beautifulsoup4", "requests", "urllib3", 
                "fake_useragent", "colorama", "tqdm", "webdriver_manager"
            ]
            
            # Map package names to import names (for cases where they differ)
            import_name_map = {
                "beautifulsoup4": "bs4",
                "webdriver_manager": "webdriver_manager.chrome"  # This is how it's imported in code
            }
            
            # For Debian systems, check system packages first
            if debian_based:
                for module in required_modules:
                    # Map module names for import checking
                    if module in import_name_map:
                        import_name = import_name_map[module]
                    else:
                        import_name = module.split('[')[0]
                    
                    code = f"try:\n    import {import_name}\n    print('True')\nexcept ImportError:\n    print('False')"
                    result = run_python_code(code)
                    
                    if result.strip() != 'True':
                        missing_modules.append(module)
            else:
                # For non-Debian, check in virtual environment
                for module in required_modules:
                    if module in import_name_map:
                        import_name = import_name_map[module]
                    else:
                        import_name = module.split('[')[0]
                        
                    success, _ = run_in_venv(f"import {import_name}")
                    if not success:
                        missing_modules.append(module)
            
            if missing_modules:
                print_warning_message(f"Neural interface detected these missing components: {', '.join(missing_modules)}", typing_effect=True)
                
                if debian_based:
                    print_system_message("Debian-based system detected.", typing_effect=True)
                    
                    # Separate apt packages and pip packages
                    apt_packages = []
                    pip_packages = []
                    
                    for module in missing_modules:
                        apt_package = get_apt_package_name(module)
                        if check_apt_package_exists(apt_package):
                            apt_packages.append(apt_package)
                        else:
                            # These packages might need to be installed via pip
                            pip_packages.append(module)
                    
                    if apt_packages:
                        print_info_message("To install available system packages, run:", typing_effect=True)
                        print_system_message(f"sudo apt-get install -y {' '.join(apt_packages)}", typing_effect=True)
                    
                    if pip_packages:
                        print_info_message("Some packages are not available in the Debian repositories.", typing_effect=True)
                        print_info_message("To install them with pip (in an externally managed environment), run:", typing_effect=True)
                        print_system_message(f"sudo pip3 install {' '.join(pip_packages)} --break-system-packages", typing_effect=True)
                        print_warning_message("Note: Using --break-system-packages is generally discouraged but may be necessary.", typing_effect=True)
                        print_info_message("Alternatively, you can set up a virtual environment:", typing_effect=True)
                        print_system_message("python3 -m venv venv", typing_effect=True)
                        print_system_message("source venv/bin/activate", typing_effect=True)
                        print_system_message(f"pip install {' '.join(pip_packages)}", typing_effect=True)
                    
                    print_info_message("After installing the packages, run this program again.", typing_effect=True)
                else:
                    print_system_message("Attempting to install missing components...", typing_effect=True)
                    # Use virtual environment's pip
                    if os.name == 'nt':
                        pip_path = os.path.join("venv", "Scripts", "pip")
                    else:
                        pip_path = os.path.join("venv", "bin", "pip")
                        
                    for module in missing_modules:
                        print_info_message(f"Installing module: {module}", typing_effect=True)
                        try:
                            subprocess.run([pip_path, "install", module], check=True, capture_output=True)
                            print_info_message(f"Successfully installed: {module}", typing_effect=True)
                        except subprocess.CalledProcessError as e:
                            print_error_message(f"Failed to install {module}: {e.stderr}", typing_effect=True)
                
                print_success_message("Neural interface components setup complete.", typing_effect=True)
            else:
                print_success_message("All neural interface components are installed.", typing_effect=True)
        elif debian_based:
            # Set up Debian system with apt
            print_system_message("Debian-based system detected.", typing_effect=True)
            
            # Required packages
            required_modules = [
                "selenium", "beautifulsoup4", "requests", "urllib3", 
                "fake_useragent", "colorama", "tqdm", "webdriver_manager"
            ]
            
            # Separate apt packages and pip packages
            apt_packages = []
            pip_packages = []
            
            for module in required_modules:
                apt_package = get_apt_package_name(module)
                if check_apt_package_exists(apt_package):
                    apt_packages.append(apt_package)
                else:
                    # These packages might need to be installed via pip
                    pip_packages.append(module)
            
            if apt_packages:
                print_info_message("To install available system packages, run:", typing_effect=True)
                print_system_message(f"sudo apt-get install -y {' '.join(apt_packages)}", typing_effect=True)
            
            if pip_packages:
                print_info_message("Some packages are not available in the Debian repositories.", typing_effect=True)
                print_info_message("To install them with pip (in an externally managed environment), run:", typing_effect=True)
                print_system_message(f"sudo pip3 install {' '.join(pip_packages)} --break-system-packages", typing_effect=True)
                print_warning_message("Note: Using --break-system-packages is generally discouraged but may be necessary.", typing_effect=True)
            
            print_info_message("After installing the packages, run this program again.", typing_effect=True)
            
            # Alternative: try with venv
            print_info_message("Alternatively, you can set up a virtual environment:", typing_effect=True)
            print_system_message("python3 -m venv venv", typing_effect=True)
            print_system_message("source venv/bin/activate", typing_effect=True)
            print_system_message(f"pip install {' '.join(required_modules)}", typing_effect=True)
        else:
            # Fall back to virtual environment setup for non-Debian systems
            if setup_environment():
                print_system_message("Neural interface activated. Ready for data extraction.", typing_effect=True)
        
        # Import the GoogleMapsScraper class after setup
        try:
            # Try directly importing first
            from src.main import GoogleMapsScraper
            self.scraper_class = GoogleMapsScraper
            print_success_message("Neural interface libraries loaded successfully.", typing_effect=True)
        except ImportError as e:
            print_error_message(f"Failed to import required modules: {e}", typing_effect=True)
            print_info_message("You may need to restart the program after setup.", typing_effect=True)
            
            # Import error details
            module_name = str(e).split("'")[-2] if "'" in str(e) else str(e)
            if module_name == "webdriver_manager":
                print_info_message("The webdriver_manager package is required for Selenium to work properly.", typing_effect=True)
                if debian_based:
                    print_info_message("Install it with:", typing_effect=True)
                    print_system_message("sudo pip3 install webdriver-manager --break-system-packages", typing_effect=True)
    
    def cmd_set(self, args: str):
        """Set a configuration option"""
        parts = args.split(' ', 1)
        if len(parts) != 2:
            print_error_message("Invalid syntax. Use: set <option> <value>", typing_effect=True)
            return
            
        option, value = parts
        option = option.strip().lower()
        value = value.strip()
        
        if option == "headless":
            if value.lower() == "true":
                self.config["headless"] = True
                print_system_message(f"Set headless mode to: {self.config['headless']}", typing_effect=True)
            elif value.lower() == "false":
                self.config["headless"] = False
                print_system_message(f"Set headless mode to: {self.config['headless']}", typing_effect=True)
            else:
                print_error_message("Invalid value for headless. Use true/false.", typing_effect=True)
                
        elif option == "browser":
            if value.lower() in ["chrome", "firefox"]:
                self.config["browser"] = value.lower()
                print_system_message(f"Set browser to: {self.config['browser']}", typing_effect=True)
            else:
                print_error_message("Invalid browser. Use chrome/firefox.", typing_effect=True)
        
        elif option == "max_results":
            try:
                max_results = int(value)
                if max_results >= 0:
                    self.config["max_results"] = max_results
                    if max_results == 0:
                        print_system_message("Set max results to: UNLIMITED", typing_effect=True)
                    else:
                        print_system_message(f"Set max results to: {self.config['max_results']}", typing_effect=True)
                else:
                    print_error_message("Max results must be greater than or equal to 0.", typing_effect=True)
            except ValueError as e:
                print_error_message("Max results must be a number.", typing_effect=True)
        
        elif option == "listings_per_proxy":
            try:
                listings_per_proxy = int(value)
                if listings_per_proxy >= 0:
                    self.config["listings_per_proxy"] = listings_per_proxy
                    if listings_per_proxy == 0:
                        print_system_message("Set listings per proxy to: UNLIMITED", typing_effect=True)
                    else:
                        print_system_message(f"Set listings per proxy to: {self.config['listings_per_proxy']}", typing_effect=True)
                else:
                    print_error_message("Listings per proxy must be greater than or equal to 0.", typing_effect=True)
            except ValueError as e:
                print_error_message("Listings per proxy must be a number.", typing_effect=True)
        
        elif option == "output_dir":
            self.config["output_dir"] = value
            print_system_message(f"Set output directory to: {self.config['output_dir']}", typing_effect=True)
        
        elif option == "proxy_test_url":
            self.config["proxy_test_url"] = value
            print_system_message(f"Set proxy test URL to: {self.config['proxy_test_url']}", typing_effect=True)
        
        elif option == "target_proxy_count":
            try:
                target_proxy_count = int(value)
                if target_proxy_count >= 0:
                    self.config["target_proxy_count"] = target_proxy_count
                    if target_proxy_count == 0:
                        print_system_message("Set target proxy count to: UNLIMITED", typing_effect=True)
                    else:
                        print_system_message(f"Set target proxy count to: {self.config['target_proxy_count']}", typing_effect=True)
                else:
                    print_error_message("Target proxy count must be greater than or equal to 0.", typing_effect=True)
            except ValueError as e:
                print_error_message("Target proxy count must be a number.", typing_effect=True)
        
        else:
            print_error_message(f"Unknown configuration option: {option}", typing_effect=True)
            
        # Save the updated configuration
        self.save_config()
    
    def cmd_config(self):
        """Show current configuration"""
        print_system_message("Current neural interface configuration:", typing_effect=True)
        for key, value in self.config.items():
            if key in ["max_results", "listings_per_proxy", "target_proxy_count"] and value == 0:
                print_info_message(f"  {key}: UNLIMITED", typing_effect=True)
            else:
                print_info_message(f"  {key}: {value}", typing_effect=True)
    
    def cmd_scrape(self, args: str):
        """Scrape Google Maps for a query"""
        if not args:
            print_error_message("No search query provided. Use: scrape \"<query>\"", typing_effect=True)
            return
        
        # Parse arguments
        query = args
        
        # Check for flags (they would come after the query with spaces)
        headless_override = None
        disable_proxies = False
        debug_mode = False
        
        if " --no-headless" in query:
            query = query.replace(" --no-headless", "")
            headless_override = False
            print_info_message("Forcing browser to be visible (no-headless mode)")
            
        if " --debug" in query:
            query = query.replace(" --debug", "")
            debug_mode = True
            print_info_message("Debug mode enabled - showing detailed logging")
            
        if " --disable-proxies" in query:
            query = query.replace(" --disable-proxies", "")
            disable_proxies = True
            print_warning_message("Proxy usage disabled - using direct connection")
        
        # Clean up query (remove quotes)
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
        
        # Check if the environment is set up
        if not check_environment():
            print_system_message("Virtual realm not detected. Initializing setup sequence...", typing_effect=True)
            if not setup_environment():
                print_error_message("Failed to materialize digital environment. Aborting.", typing_effect=True)
                return
        
        # Import required modules if not already imported
        if self.scraper_class is None:
            # Check if modules exist in the virtual environment
            success, output = run_in_venv("import src.main")
            if not success:
                print_error_message("Critical modules missing. Neural pathways corrupted.", typing_effect=True)
                print_info_message("Run the 'setup' command to install dependencies.", typing_effect=True)
                return
                
            try:
                from src.main import GoogleMapsScraper
                self.scraper_class = GoogleMapsScraper
            except ImportError as e:
                print_error_message("Critical modules missing. Neural pathways corrupted.", typing_effect=True)
                print_info_message("Run the 'setup' command to install dependencies.", typing_effect=True)
                print_info_message(f"Technical details: {str(e)}", typing_effect=True)
                return
        
        print_mission_message(f"Target acquired: \"{query}\"", typing_effect=True)
        print_system_message("Initializing neural interface...", typing_effect=True)
        
        # Create a thread to handle scraping
        def scrape_thread():
            try:
                # Initialize the scraper with status messages
                print_system_message("Breaking through digital barriers...")
                
                # Override headless mode if specified
                config_copy = self.config.copy()
                if headless_override is not None:
                    config_copy["headless"] = headless_override
                    print_info_message(f"Headless mode: {'ON' if headless_override else 'OFF (browser will be visible)'}")
                
                # Initialize the scraper
                scraper = self.scraper_class(
                    output_dir=config_copy["output_dir"],
                    headless=config_copy["headless"],
                    browser_type=config_copy["browser"],
                    max_results=config_copy["max_results"],
                    listings_per_proxy=config_copy["listings_per_proxy"],
                    proxy_test_url=config_copy["proxy_test_url"],
                    target_proxy_count=config_copy["target_proxy_count"]
                )
                
                # Disable proxies if requested
                if disable_proxies:
                    scraper.proxy_manager.allow_direct_connection = True
                    scraper.proxy_manager.consecutive_proxy_failures = 999  # Force direct connection
                
                # Enable debug mode if requested
                if debug_mode:
                    print_info_message(f"Configuration: {json.dumps(config_copy, indent=2)}")
                    # Method to print current system environment info
                    print_info_message(f"Current display: {os.environ.get('DISPLAY', 'Not set')}")
                
                # Scrape the query
                results = scraper.scrape(query)
                
                if results:
                    result_count = len(results)
                    print_success_message(f"Extraction complete! Harvested {result_count} data packets.", typing_effect=True)
                    print_system_message(f"Data saved to: {config_copy['output_dir']}/{query.replace(' ', '_').lower()[:30]}.json", typing_effect=True)
                else:
                    print_warning_message("Extraction yielded zero results. Security measures may be active.", typing_effect=True)
            
            except Exception as e:
                print_error_message(f"Digital heist failed: {e}", typing_effect=True)
                if debug_mode:
                    import traceback
                    print_error_message(traceback.format_exc(), typing_effect=True)
        
        threading.Thread(target=scrape_thread).start()
            
        # Rest of the code remains the same...

    def cmd_version(self, args):
        """Show version information"""
        print_system_message("TryloByte Digital Reconnaissance System", typing_effect=True)
        print_info_message("Version: 1.0.0", typing_effect=True)
        print_info_message("Release Date: 2025-03-22", typing_effect=True)
        print_info_message("Codename: Digital Recon", typing_effect=True)
        return True
    
    def cmd_update(self, args):
        """Check for updates"""
        print_system_message("Scanning deep web for upgrades...", typing_effect=True)
        time.sleep(1)
        print_success_message("You are running the latest version of TryloByte.", typing_effect=True)
        return True
    
    def cmd_about(self, args):
        """Show information about the program"""
        about_text = """
TryloByte - Digital Reconnaissance System
-----------------------------------------
A retro-styled Google Maps scraping tool with intelligent proxy management 
for gathering data while avoiding detection.

Features:
- Scrapes business listings from Google Maps
- Automatically harvests and tests proxies
- Smart proxy rotation to avoid detection
- Collects detailed business information
- Handles rate limiting and detection avoidance

Developed with cyberpunk aesthetics, TryloByte presents complex operations
in a fun, hacker-movie style interface while performing serious data collection.
"""
        print_info_message(about_text, typing_effect=False)
        return True
    
    def cmd_clear(self, args):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_ascii_header()
        return True
    
    def cmd_info(self, args):
        """Show system information"""
        print_system_message("System diagnostics:", typing_effect=True)
        
        # Python version
        print_info_message(f"Python version: {sys.version.split()[0]}", typing_effect=True)
        
        # OS info
        import platform
        os_info = platform.platform()
        print_info_message(f"Operating system: {os_info}", typing_effect=True)
        
        # Check for virtual environment
        in_venv = sys.prefix != sys.base_prefix
        print_info_message(f"Virtual environment: {'Active' if in_venv else 'Inactive'}", typing_effect=True)
        
        # Configuration
        print_info_message(f"Configuration file: {'Found' if Path('config.json').exists() else 'Not found'}", typing_effect=True)
        
        # Data directory
        data_path = Path(self.config.get("output_dir", "data"))
        print_info_message(f"Data directory: {data_path.absolute()}", typing_effect=True)
        print_info_message(f"Data directory exists: {'Yes' if data_path.exists() else 'No'}", typing_effect=True)
        
        return True
    
    def cmd_easter_egg(self, args):
        """Easter egg command"""
        print_system_message("Initiating dance protocol...", typing_effect=True)
        time.sleep(0.5)
        
        dance_frames = [
            """
   o
  /|\\
  / \\
""",
            """
    o
   /|\\
   / \\
""",
            """
     o
    /|\\
    / \\
""",
            """
    o
   /|\\
   / \\
""",
            """
   o
  /|\\
  / \\
""",
            """
  o
 /|\\
 / \\
"""
        ]
        
        for _ in range(3):
            for frame in dance_frames:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(f"{NEON_GREEN}{frame}{RESET}")
                time.sleep(0.2)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_ascii_header()
        print_success_message("Dance protocol executed successfully!", typing_effect=True)
        return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        "selenium", "beautifulsoup4", "requests", "urllib3", 
        "fake_useragent", "colorama", "tqdm", "webdriver_manager"
    ]
    
    missing_modules = []
    
    # Map package names to import names
    import_name_map = {
        "beautifulsoup4": "bs4",
        "webdriver_manager": "webdriver_manager.chrome"
    }
    
    for module in required_modules:
        try:
            if module in import_name_map:
                import_name = import_name_map[module]
            else:
                import_name = module.split('[')[0]
                
            code = f"try:\n    import {import_name}\n    print('True')\nexcept ImportError:\n    print('False')"
            result = run_python_code(code)
            
            if result.strip() != 'True':
                missing_modules.append(module)
        except Exception:
            missing_modules.append(module)
    
    return missing_modules

def check_environment():
    """Check if virtual environment is set up"""
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    
    # First check if we're running in the virtual environment
    in_venv = sys.prefix != sys.base_prefix
    
    # If we're not in a venv, check if the venv directory exists
    if not in_venv and os.path.exists(venv_path):
        return True
    
    # If we're on Debian and not in a venv, check if apt packages are installed
    if not in_venv and is_debian_based():
        # Try to import key modules to confirm system-wide installation
        try:
            import_attempt = run_python_code(
                "try:\n"
                "    import selenium\n"
                "    import bs4\n"
                "    import requests\n"
                "    import colorama\n"
                "    print('True')\n"
                "except ImportError:\n"
                "    print('False')\n"
            )
            if import_attempt.strip() == 'True':
                return True
        except Exception:
            pass
    
    return in_venv

def run_python_code(code):
    """Run Python code and return the output"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True
    )
    return result.stdout

def run_in_venv(command):
    """Run a command in the virtual environment"""
    if os.name == 'nt':
        python_path = os.path.join("venv", "Scripts", "python")
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        python_path = os.path.join("venv", "bin", "python")
        pip_path = os.path.join("venv", "bin", "pip")
    
    if command.startswith("pip"):
        cmd_parts = command.split()
        cmd = [pip_path] + cmd_parts[1:]
    else:
        cmd = [python_path, "-c", command]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_environment():
    """Set up the virtual environment"""
    try:
        print_system_message("Setting up neural interface. Please wait...", typing_effect=True)
        
        # Required packages
        required_modules = [
            "selenium", "beautifulsoup4", "requests", "urllib3", 
            "fake_useragent", "colorama", "tqdm", "webdriver_manager"
        ]
        
        # Check if we're on a Debian-based system
        if is_debian_based():
            print_system_message("Debian-based system detected. Using apt package manager.", typing_effect=True)
            
            # Install modules with apt
            apt_success_count = 0
            apt_failed_modules = []
            
            for module in required_modules:
                if install_with_apt(module):
                    apt_success_count += 1
                else:
                    apt_failed_modules.append(module)
            
            if apt_success_count == len(required_modules):
                print_success_message("All neural interface components installed successfully via apt.", typing_effect=True)
                return True
            elif apt_success_count > 0:
                print_warning_message(f"Installed {apt_success_count} out of {len(required_modules)} components via apt.", typing_effect=True)
                print_info_message(f"Failed modules: {', '.join(apt_failed_modules)}", typing_effect=True)
                
                # Try with pip for remaining packages
                print_system_message("Attempting to install failed modules with pip...", typing_effect=True)
                
                pip_success = True
                for module in apt_failed_modules:
                    try:
                        print_info_message(f"Installing {module} with pip...", typing_effect=True)
                        subprocess.run([sys.executable, "-m", "pip", "install", "--user", module], check=True)
                        print_success_message(f"Successfully installed {module} with pip", typing_effect=True)
                    except subprocess.CalledProcessError:
                        print_error_message(f"Failed to install {module} with pip", typing_effect=True)
                        pip_success = False
                
                return pip_success
        
        # Fall back to virtual environment setup if not Debian or apt install failed
        print_system_message("Setting up Python virtual environment...", typing_effect=True)
        
        # Create virtual environment
        print_system_message("Initializing quantum environment...", typing_effect=True)
        try:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        except subprocess.CalledProcessError:
            print_error_message("Failed to create virtual environment. Trying with user permissions...", typing_effect=True)
            subprocess.run([sys.executable, "-m", "venv", "--user", "venv"], check=True)
        
        # Upgrade pip in the virtual environment
        print_system_message("Upgrading neural connectors...", typing_effect=True)
        if os.name == 'nt':
            pip_path = os.path.join("venv", "Scripts", "pip")
        else:
            pip_path = os.path.join("venv", "bin", "pip")
            
        try:
            subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        except subprocess.CalledProcessError:
            print_warning_message("Failed to upgrade pip. Continuing with installation...", typing_effect=True)
        
        # Install required packages
        print_system_message("Installing core neural interface components...", typing_effect=True)
        success_count = 0
        for module in required_modules:
            print_info_message(f"Installing module: {module}", typing_effect=True)
            try:
                subprocess.run([pip_path, "install", "--user", module], check=True)
                success_count += 1
                print_info_message(f"Successfully installed: {module}", typing_effect=True)
            except subprocess.CalledProcessError as e:
                try:
                    # Try without --user flag
                    subprocess.run([pip_path, "install", module], check=True)
                    success_count += 1
                    print_info_message(f"Successfully installed: {module}", typing_effect=True)
                except subprocess.CalledProcessError:
                    print_error_message(f"Failed to install {module}. You may need admin privileges.", typing_effect=True)
        
        if success_count == len(required_modules):
            print_success_message("All neural interface components installed successfully.", typing_effect=True)
        else:
            print_warning_message(f"Installed {success_count} out of {len(required_modules)} components.", typing_effect=True)
            print_info_message("You may need to run this script with administrator privileges.", typing_effect=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error_message(f"Failed to set up neural interface: {str(e)}", typing_effect=True)
        print_info_message("Try running this script with administrator privileges (sudo).", typing_effect=True)
        return False

def is_debian_based():
    """Check if the system is Debian/Ubuntu based"""
    return os.path.exists("/etc/debian_version")

def get_apt_package_name(module_name):
    """Map Python package names to apt package names"""
    apt_package_map = {
        "selenium": "python3-selenium",
        "beautifulsoup4": "python3-bs4",
        "requests": "python3-requests",
        "urllib3": "python3-urllib3",
        "fake_useragent": "python3-fake-useragent",
        "colorama": "python3-colorama",
        "tqdm": "python3-tqdm",
        "webdriver_manager": "python3-webdriver-manager"  # This may not exist in all repos
    }
    return apt_package_map.get(module_name, f"python3-{module_name.replace('_', '-')}")

def check_apt_package_exists(package_name):
    """Check if a package exists in apt repository"""
    try:
        result = subprocess.run(
            ["apt-cache", "show", package_name],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False

def install_with_apt(package_name):
    """Install a package using apt"""
    try:
        print_system_message(f"Installing {package_name} using apt...", typing_effect=True)
        
        # Map Python package names to apt package names
        apt_package = get_apt_package_name(package_name)
        
        # Print command for user to run manually if sudo fails
        print_info_message(f"You can manually install this package with: sudo apt-get install -y {apt_package}", typing_effect=True)
        
        # We'll attempt a non-interactive check to see if packages exist
        try:
            check_cmd = ["apt-cache", "show", apt_package]
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print_warning_message(f"Package {apt_package} not found in apt repository", typing_effect=True)
                return False
                
            print_info_message(f"Package {apt_package} is available in apt repository", typing_effect=True)
            print_info_message("Run the following command to install it:", typing_effect=True)
            print_info_message(f"sudo apt-get install -y {apt_package}", typing_effect=True)
                
            return False  # We're not actually installing it automatically anymore
        except Exception as e:
            print_error_message(f"Error checking apt repository: {str(e)}", typing_effect=True)
            return False
            
    except Exception as e:
        print_error_message(f"Error during apt installation: {str(e)}", typing_effect=True)
        return False

def main():
    """Main entry point"""
    if not check_environment():
        if not setup_environment():
            print_error_message("Failed to set up environment.")
    
    cli = TryloByteCLI()
    cli.start()

if __name__ == "__main__":
    main()
