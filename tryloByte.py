#!/usr/bin/env python3
"""
TryloByte - A retro-styled Google Maps scraping tool.
"""
import os
import sys
import time
import json
import subprocess
import termios
import tty
import signal
from pathlib import Path
import argparse
import threading
import re
from typing import List, Dict, Optional, Callable, Any, Tuple

# Import the centralized console output module
from src.common.logger import (
    print_message, print_with_typing_effect,
    print_system_message, print_info_message, print_warning_message,
    print_error_message, print_success_message, 
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

# List of configuration options that can be set
CONFIG_OPTIONS = {
    "headless": {"type": bool, "default": False, "help": "Run browser in headless mode"},
    "browser": {"type": str, "default": "chrome", "help": "Browser to use (chrome/firefox)"},
    "max_results": {"type": int, "default": 0, "help": "Maximum number of results to scrape (0 = unlimited)"},
    "output_dir": {"type": str, "default": "data", "help": "Directory to store output files"},
    "proxy_test_url": {"type": str, "default": "http://httpbin.org/ip", "help": "URL to test proxies against"},
    "target_proxy_count": {"type": int, "default": 10, "help": "Target number of working proxies to find"},
    "use_proxy": {"type": bool, "default": False, "help": "Use proxies for scraping"},
    "proxy_file": {"type": str, "default": None, "help": "File containing proxies (one per line)"},
    "proxy_type": {"type": str, "default": "elite", "help": "Type of proxy to use: elite, anonymous, transparent"}
}


class TryloByteCLI:
    """Interactive command-line interface for TryloByte"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.running = True
        
        # Initialize default configuration
        self.config = {option: details["default"] for option, details in CONFIG_OPTIONS.items()}
        
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
        
        # Command history for up/down arrow navigation
        self.command_history: List[str] = []
        self.history_position = 0
        self.max_history = 50  # Maximum number of commands to remember
    
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
                command = self.get_command_with_history(f"{NEON_GREEN}>>{RESET} ")
                
                # Process command
                if command.strip():
                    self.process_command(command.strip())
            except KeyboardInterrupt:
                print("")
                print_warning_message("Received Ctrl+C")
                if self._confirm_exit():
                    self.cmd_exit()
            except EOFError:
                print("")
                self.cmd_exit()
            except Exception as e:
                print_error_message(f"Unexpected exception: {e}")
    
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
            result = self.get_command_map()[command](args)
            if result == "EXIT":
                self.running = False
        elif command:
            print_error_message(f"Unknown command: {command}", typing_effect=True)
            print_info_message("Type 'help' for available commands.", typing_effect=True)
        
        return True
    
    def cmd_harvest_proxies(self, args: str = ""):
        """Harvest and test proxies for later use"""
        # Import the proxy harvester
        try:
            from src.proxy_harvester import ProxyHarvester
            
            print_system_message("Initializing proxy harvester...")
            
            # Parse country filter
            country = "US"  # Default to US
            if "--country=" in args:
                country = args.split("--country=")[1].split(" ")[0].strip()
            
            harvester = ProxyHarvester(output_dir=self.config["output_dir"])
            print_info_message(f"Harvesting proxies for country: {country}...")
            print_info_message("This may take a few minutes as we test each proxy...")
            
            # Run the harvester with all the specialized capabilities
            working_proxies, tested_count, total_count = harvester.run(country_filter=country)
            
            # Display results
            print_success_message(f"Proxy harvesting complete!")
            print_info_message(f"Tested {tested_count} out of {total_count} proxies")
            print_info_message(f"Found {len(working_proxies)} working proxies")
            
            # Display some sample proxies
            if working_proxies:
                print_system_message("Sample of working proxies:")
                for i, proxy in enumerate(working_proxies[:5]):
                    anonymity = proxy.get("anonymity", "unknown").upper()
                    speed = proxy.get("speed", 0)
                    print_info_message(f"  {i+1}. {proxy['ip']}:{proxy['port']} - {anonymity} - Response: {speed:.2f}s")
                
                print_info_message(f"Proxies saved to: {self.config['output_dir']}/proxies.json")
            else:
                print_warning_message("No working proxies found")
            
            return True
            
        except ImportError:
            print_error_message("Failed to import proxy harvester. Make sure all dependencies are installed.")
            return False
        except Exception as e:
            print_error_message(f"Error harvesting proxies: {str(e)}")
            return False
    
    def get_command_map(self):
        """Get the command map for this instance"""
        return {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "bye": self.cmd_exit,
            "setup": self.cmd_setup,
            "scrape": self.cmd_scrape,
            "search": self.cmd_scrape,  # Alias for scrape
            "config": self.cmd_config,
            "settings": self.cmd_config,  # Alias for config
            "set": self.cmd_set,
            "clear": self.cmd_clear,
            "cls": self.cmd_clear,  # Alias for clear
            "harvest": self.cmd_harvest_proxies,
            "proxies": self.cmd_harvest_proxies  # Alias for harvest
        }
    
    def cmd_exit(self, args: str = ""):
        """
        Exit the application after cleaning up resources.
        Usage: exit
        """
        print_system_message("Terminating connection to the Matrix...")
        
        # Clean up any resources
        self._cleanup_browser_processes()
        
        print_system_message("Disconnecting neural interface...")
        time.sleep(2)
        print_system_message("TryloByte shutting down. Connection terminated.")
        self.running = False
        return "EXIT"
    
    def _cleanup_browser_processes(self):
        """
        Clean up any browser processes that might be running.
        This helps prevent zombie processes and resource leaks.
        Uses standard system tools to avoid dependencies.
        """
        import subprocess
        import os
        import signal
        
        try:
            print_info_message("Running browser cleanup...")
            
            # Clean up Chrome/Chromium processes using pgrep and pkill
            browser_process_patterns = [
                "chrome", "chromium", "chromedriver", 
                "google-chrome", "chromium-browser",
                "firefox", "geckodriver"
            ]
            
            # First, check if there are any matching processes
            for pattern in browser_process_patterns:
                try:
                    # Use pgrep to find processes matching our pattern
                    result = subprocess.run(
                        ["pgrep", "-f", pattern], 
                        capture_output=True, 
                        text=True,
                        check=False
                    )
                    
                    # If we found matching processes
                    if result.returncode == 0 and result.stdout.strip():
                        pids = result.stdout.strip().split('\n')
                        
                        for pid_str in pids:
                            try:
                                pid = int(pid_str)
                                
                                # Try to check if this process has our tryloByte in its command line
                                # to avoid killing unrelated browser processes
                                cmd_result = subprocess.run(
                                    ["ps", "-p", str(pid), "-o", "cmd="],
                                    capture_output=True,
                                    text=True,
                                    check=False
                                )
                                
                                cmd_line = cmd_result.stdout.lower()
                                
                                # Only kill if it seems to be related to our application
                                if ("trylobyte" in cmd_line or 
                                    "google_maps_scraper" in cmd_line or
                                    "chromedriver" in cmd_line or
                                    "--remote-debugging-port" in cmd_line):
                                    
                                    print_info_message(f"Terminating browser process: {pattern} (PID: {pid})")
                                    
                                    # Try graceful termination first
                                    try:
                                        os.kill(pid, signal.SIGTERM)
                                    except:
                                        # If graceful termination fails, force kill
                                        try:
                                            os.kill(pid, signal.SIGKILL)
                                        except:
                                            pass
                            except ValueError:
                                # Skip invalid PIDs
                                pass
                except subprocess.SubprocessError:
                    pass
            
            # Additional cleanup for any zombie Chromedriver or debugging ports
            for cleanup_pattern in ["chromedriver", "chrome --remote-debugging-port"]:
                try:
                    subprocess.run(["pkill", "-f", cleanup_pattern], check=False)
                except subprocess.SubprocessError:
                    pass
            
            print_success_message("Browser cleanup completed")
            
        except Exception as e:
            print_warning_message(f"Error during browser cleanup: {str(e)}")
            # Not critical if this fails, so continue with shutdown
    
    def cmd_help(self, args):
        """Show help information"""
        help_text = """
Available commands:
  help           - Show this help information
  scrape <query> - Scrape Google Maps for a query
                   Options: --location="New York" --max-results=50 --headless|--visible --use-proxy --proxy-file=<file> --proxy-type=<type>
  harvest        - Harvest and test proxies for later use
                   Options: --country=XX (default: US)
  setup          - Install required dependencies
  config         - View current configuration
  set <option> <value> - Set a configuration option
  clear          - Clear the screen
  exit           - Exit the program
"""
        print_info_message(help_text, typing_effect=False)
        return True
    
    def cmd_setup(self, args=None):
        """Setup the dependencies"""
        print_system_message("Setting up TryloByte environment...", typing_effect=True)
        
        try:
            # Check for required Python packages
            required_packages = [
                "selenium", "beautifulsoup4", "requests", "urllib3",
                "fake_useragent", "colorama", "tqdm", "webdriver_manager"
            ]
            
            # Check which packages are missing
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package.split('[')[0].replace('-', '_'))
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                print_warning_message(f"Missing packages: {', '.join(missing_packages)}")
                
                # Ask user if they want to install
                print_info_message("Install missing packages? (y/n)")
                choice = input(f"{NEON_GREEN}>>{RESET} ").lower()
                
                if choice.startswith('y'):
                    print_system_message("Installing missing packages...")
                    
                    # Use pip to install packages
                    try:
                        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, check=True)
                        print_success_message("All packages installed successfully!")
                    except subprocess.CalledProcessError as e:
                        print_error_message(f"Failed to install packages: {e}")
                        print_info_message("You may need to install them manually:")
                        print_info_message(f"pip install {' '.join(missing_packages)}")
                else:
                    print_warning_message("Skipping package installation. Some features may not work.")
            else:
                print_success_message("All required packages are already installed!")
                
            # Check for browser drivers
            print_system_message("Checking for browser drivers...")
            
            # WebDriver Manager will handle driver installation automatically
            # when the browser is first used, so we just need to inform the user
            print_info_message("Browser drivers will be installed automatically when needed.")
            print_success_message("TryloByte setup complete!")
            
        except Exception as e:
            print_error_message(f"Setup failed: {e}")
    
    def cmd_set(self, args: str):
        """Set a configuration option"""
        if not args:
            print_error_message("Missing option and value. Usage: set <option> <value>")
            return True
        
        parts = args.strip().split(' ', 1)
        if len(parts) < 2:
            print_error_message("Missing value. Usage: set <option> <value>")
            return True
        
        option, value = parts
        option = option.lower()
        
        if option not in CONFIG_OPTIONS:
            print_error_message(f"Unknown option: {option}")
            print_info_message(f"Available options: {', '.join(CONFIG_OPTIONS.keys())}")
            return True
        
        # Convert value to the correct type
        option_type = CONFIG_OPTIONS[option]["type"]
        try:
            if option_type == bool:
                value = value.lower() in ('true', 'yes', 'y', '1', 'on')
            elif option_type == int:
                value = int(value)
            # String type doesn't need conversion
            
            # Update the config
            self.config[option] = value
            
            # Save the config
            self.save_config()
            
            print_success_message(f"Set {option} = {value}")
            
        except ValueError:
            print_error_message(f"Invalid value for {option}. Expected {option_type.__name__}.")
        
        return True
    
    def cmd_config(self, args=None):
        """Show current configuration"""
        print_system_message("Current configuration:")
        
        for option, value in self.config.items():
            # Get help text if available
            help_text = CONFIG_OPTIONS.get(option, {}).get("help", "")
            print_info_message(f"  {option} = {value}{' - ' + help_text if help_text else ''}")
        
        print_info_message("\nUse 'set <option> <value>' to change a setting.")
        return True
    
    def cmd_clear(self, args=None):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_ascii_header()
        return True
    
    def cmd_scrape(self, args: str = ""):
        """
        Run the Google Maps scraper with the given query.
        Usage: scrape [query] [--location=City,State] [--visible] [--max=N] [--proxy] [--proxy-file=FILE]
        """
        import subprocess
        import shlex
        import sys
        from pathlib import Path
        import os
        
        # Parse out the query and location
        quoted_query = None
        location = None
        max_results = self.config.get("max_results", 0)  # Use config setting by default
        visible_mode = not self.config.get("headless", False)  # Use config setting
        use_proxy = self.config.get("use_proxy", False)  # Use config setting
        proxy_file = self.config.get("proxy_file", None)  # Use config setting
        proxy_type = self.config.get("proxy_type", "elite")  # Use config setting
        
        # Check for quoted query first
        if '"' in args:
            parts = args.split('"')
            if len(parts) >= 3:
                quoted_query = parts[1]
                remaining_args = parts[0] + parts[2]
            else:
                remaining_args = args
        else:
            remaining_args = args
        
        # Handle the remaining arguments
        parts = shlex.split(remaining_args)
        
        # If we don't have a quoted query yet, use first non-option as query
        if not quoted_query and parts:
            non_options = [p for p in parts if not p.startswith("--") and not p.startswith("-")]
            if non_options:
                quoted_query = non_options[0]
                parts.remove(quoted_query)
        
        # Process other options - these override config settings
        for part in parts:
            if part.startswith("--location="):
                location = part.split("=", 1)[1]
            elif part == "--visible":
                visible_mode = True
            elif part == "--headless":
                visible_mode = False
            elif part.startswith("--max="):
                try:
                    max_results = int(part.split("=", 1)[1])
                except ValueError:
                    print_warning_message(f"Invalid max results value: {part}")
            elif part == "--proxy":
                use_proxy = True
            elif part == "--no-proxy":
                use_proxy = False
            elif part.startswith("--proxy-file="):
                proxy_file = part.split("=", 1)[1]
                use_proxy = True
            elif part.startswith("--proxy-type="):
                proxy_type = part.split("=", 1)[1]
                if proxy_type not in ["elite", "anonymous", "all"]:
                    print_warning_message(f"Invalid proxy type: {proxy_type}. Using elite.")
                    proxy_type = "elite"
        
        if not quoted_query:
            print_error_message("No query specified")
            print_info_message("Usage: scrape [query] [--location=City,State] [--visible/--headless] [--max=N] [--proxy/--no-proxy] [--proxy-file=FILE]")
            return False
        
        # Prepare command line arguments
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_maps_scraper.py"),
            quoted_query
        ]
        
        if location:
            cmd.extend(["--location", location])
        
        if not visible_mode:
            cmd.append("--headless")
        
        if max_results > 0:
            cmd.extend(["--max-results", str(max_results)])
        
        if use_proxy:
            cmd.append("--use-proxy")
            
            if proxy_file:
                cmd.extend(["--proxy-file", proxy_file])
            
            cmd.extend(["--proxy-type", proxy_type])
        
        output_dir = self.config.get("output_dir", "data")
        cmd.extend(["--output", output_dir])
        
        print_system_message(f"Starting Google Maps scraping for: {quoted_query}")
        print_info_message("Press Ctrl+C to stop the scraper at any time")
        
        if visible_mode:
            print_info_message("Running in visible mode - a browser window will open")
        else:
            print_info_message("Running in headless mode - no visible browser window")
        
        if use_proxy:
            if proxy_file:
                print_info_message(f"Using proxies from file: {proxy_file}")
            else:
                print_info_message("Using auto-harvested proxies with specialized harvesting capabilities")
                print_info_message(f"Proxy type: {proxy_type}")
        
        try:
            # Run the scraper with the current environment
            result = subprocess.run(cmd, check=False)
            
            if result.returncode == 0:
                print_success_message("Scraping completed successfully")
                return True
            elif result.returncode == 130:
                print_warning_message("Scraping was interrupted by user")
                return False
            else:
                print_error_message(f"Scraping failed with exit code: {result.returncode}")
                return False
                
        except KeyboardInterrupt:
            print_warning_message("\nScraping interrupted by user")
            return False
        except Exception as e:
            print_error_message(f"Error running scraper: {str(e)}")
            return False

    def get_key(self) -> str:
        """Get a single keypress from the user."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            
            # Handle special key sequences (arrow keys, etc.)
            if ch == '\x1b':  # ESC character
                # Could be an escape sequence
                ch1 = sys.stdin.read(1)
                if ch1 == '[':  # ESC + [ indicates arrow key
                    ch2 = sys.stdin.read(1)
                    # Return special key codes
                    if ch2 == 'A': return 'UP'
                    if ch2 == 'B': return 'DOWN'
                    if ch2 == 'C': return 'RIGHT'
                    if ch2 == 'D': return 'LEFT'
                    if ch2 == 'H': return 'HOME'
                    if ch2 == 'F': return 'END'
                    
                    # Handle Delete key (ESC [ 3 ~)
                    if ch2 == '3' and sys.stdin.read(1) == '~':
                        return 'DELETE'
                        
                    return f'ESC[{ch2}'
                return f'ESC{ch1}'
            
            # Handle control characters
            if ch == '\x7f':  # Backspace
                return 'BACKSPACE'
            if ch == '\r' or ch == '\n':  # Enter
                return 'ENTER'
            if ch == '\x04':  # Ctrl+D
                return 'EOF'
            if ch == '\x03':  # Ctrl+C
                return 'SIGINT'
            
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def get_command_with_history(self, prompt: str = ">> ") -> str:
        """
        Enhanced input handling with command history and cursor movement.
        Supports:
        - Up/down arrows to navigate command history
        - Left/right arrows to move cursor within line
        - Home/End keys to jump to start/end of line
        
        Args:
            prompt: Text prompt to display
            
        Returns:
            User entered command
        """
        current_line = ""
        cursor_pos = 0
        history_index = len(self.command_history)
        saved_current_line = ""
        
        # Print initial prompt
        sys.stdout.write(f"{NEON_GREEN}{prompt}{RESET}")
        sys.stdout.flush()
        
        while True:
            key = self.get_key()
            
            if key == 'ENTER':
                # Add command to history if not empty and not a duplicate of the most recent command
                if current_line and (not self.command_history or current_line != self.command_history[-1]):
                    self.command_history.append(current_line)
                    # Limit history size
                    if len(self.command_history) > self.max_history:
                        self.command_history = self.command_history[-self.max_history:]
                
                sys.stdout.write('\n')
                return current_line
                
            elif key == 'UP':
                # Go back in history
                if history_index > 0:
                    # If at the end of history, save current line
                    if history_index == len(self.command_history):
                        saved_current_line = current_line
                    
                    history_index -= 1
                    current_line = self.command_history[history_index]
                    cursor_pos = len(current_line)
                    
                    # Redraw the entire line
                    sys.stdout.write('\r' + ' ' * (len(prompt) + len(current_line) + 10))  # Clear line
                    sys.stdout.write(f'\r{NEON_GREEN}{prompt}{RESET}{current_line}')
                    sys.stdout.flush()
                    
            elif key == 'DOWN':
                # Go forward in history
                if history_index < len(self.command_history):
                    history_index += 1
                    if history_index == len(self.command_history):
                        current_line = saved_current_line
                    else:
                        current_line = self.command_history[history_index]
                    cursor_pos = len(current_line)
                    
                    # Redraw the entire line
                    sys.stdout.write('\r' + ' ' * (len(prompt) + len(current_line) + 10))  # Clear line
                    sys.stdout.write(f'\r{NEON_GREEN}{prompt}{RESET}{current_line}')
                    sys.stdout.flush()
                    
            elif key == 'LEFT':
                # Move cursor left
                if cursor_pos > 0:
                    cursor_pos -= 1
                    sys.stdout.write('\b')
                    sys.stdout.flush()
                    
            elif key == 'RIGHT':
                # Move cursor right
                if cursor_pos < len(current_line):
                    sys.stdout.write(current_line[cursor_pos])
                    cursor_pos += 1
                    sys.stdout.flush()
                    
            elif key == 'HOME':
                # Move to beginning of line
                sys.stdout.write('\r' + f"{NEON_GREEN}{prompt}{RESET}")
                cursor_pos = 0
                sys.stdout.flush()
                
            elif key == 'END':
                # Move to end of line
                if cursor_pos < len(current_line):
                    sys.stdout.write(current_line[cursor_pos:])
                    cursor_pos = len(current_line)
                    sys.stdout.flush()
                    
            elif key == 'BACKSPACE':
                # Delete character before cursor
                if cursor_pos > 0:
                    # Remove the character from the string
                    current_line = current_line[:cursor_pos-1] + current_line[cursor_pos:]
                    cursor_pos -= 1
                    
                    # Redraw the entire line
                    sys.stdout.write('\r' + ' ' * (len(prompt) + len(current_line) + 1))  # Clear line
                    sys.stdout.write(f'\r{NEON_GREEN}{prompt}{RESET}{current_line}')
                    
                    # Move cursor back to position
                    sys.stdout.write('\r' + f"{NEON_GREEN}{prompt}{RESET}" + current_line[:cursor_pos])
                    sys.stdout.flush()
                    
            elif key == 'DELETE':
                # Delete character at cursor
                if cursor_pos < len(current_line):
                    # Remove the character from the string
                    current_line = current_line[:cursor_pos] + current_line[cursor_pos+1:]
                    
                    # Redraw the entire line
                    sys.stdout.write('\r' + ' ' * (len(prompt) + len(current_line) + 1))  # Clear line
                    sys.stdout.write(f'\r{NEON_GREEN}{prompt}{RESET}{current_line}')
                    
                    # Move cursor back to position
                    sys.stdout.write('\r' + f"{NEON_GREEN}{prompt}{RESET}" + current_line[:cursor_pos])
                    sys.stdout.flush()
                    
            elif key == 'SIGINT':
                # Handle Ctrl+C
                sys.stdout.write('\n')
                raise KeyboardInterrupt()
                
            elif key == 'EOF':
                # Handle Ctrl+D
                sys.stdout.write('\n')
                raise EOFError()
                
            elif len(key) == 1:  # Regular character
                # Insert character at cursor position
                current_line = current_line[:cursor_pos] + key + current_line[cursor_pos:]
                cursor_pos += 1
                
                # Write the new character and the rest of the line
                sys.stdout.write(current_line[cursor_pos-1:])
                
                # Move cursor back to position
                if cursor_pos < len(current_line):
                    sys.stdout.write('\b' * (len(current_line) - cursor_pos))
                
                sys.stdout.flush()
    
    def _confirm_exit(self):
        """Ask for confirmation before exiting"""
        try:
            print_warning_message("Do you really want to exit? (y/n)")
            response = self.get_command_with_history(f"{NEON_GREEN}>>{RESET} ")
            return response.lower().startswith('y')
        except (KeyboardInterrupt, EOFError):
            return True


def main():
    """Main function to run the TryloByte CLI or process command line args"""
    # Check if arguments were provided
    if len(sys.argv) > 1:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="TryloByte - Google Maps scraper with retro terminal interface")
        parser.add_argument("--setup", action="store_true", help="Set up the environment")
        parser.add_argument("--scrape", metavar="QUERY", help="Scrape Google Maps for the given query")
        parser.add_argument("--location", help="Location for the search")
        parser.add_argument("--headless", action="store_true", help="Run in headless mode")
        parser.add_argument("--visible", action="store_true", help="Run with visible browser window")
        parser.add_argument("--use-proxy", action="store_true", help="Use proxies for scraping")
        parser.add_argument("--proxy-file", help="File containing proxies (one per line)")
        parser.add_argument("--proxy-type", default="elite", help="Type of proxy to use: elite, anonymous, transparent")
        parser.add_argument("--max-results", type=int, default=0, help="Maximum number of results (0 = unlimited)")
        parser.add_argument("--harvest", action="store_true", help="Harvest proxies")
        parser.add_argument("--country", default="US", help="Country filter for proxy harvesting")
        
        args = parser.parse_args()
        
        # Create CLI instance for configuration
        cli = TryloByteCLI()
        
        # Run requested command
        if args.setup:
            cli.cmd_setup()
        elif args.harvest:
            cli.cmd_harvest_proxies(f"--country={args.country}")
        elif args.scrape:
            # Build scrape command
            cmd = f'"{args.scrape}"'
            
            if args.location:
                cmd += f' --location="{args.location}"'
                
            if args.headless:
                cmd += " --headless"
            elif args.visible:
                cmd += " --visible"
                
            if args.max_results > 0:
                cmd += f" --max-results={args.max_results}"
                
            if args.use_proxy:
                cmd += " --use-proxy"
                
                if args.proxy_file:
                    cmd += f" --proxy-file={args.proxy_file}"
                
                cmd += f" --proxy-type={args.proxy_type}"
            
            cli.cmd_scrape(cmd)
            
            # Keep the script running until the scrape is done
            try:
                while threading.active_count() > 1:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nExiting...")
    else:
        # Start interactive CLI
        cli = TryloByteCLI()
        cli.start()


if __name__ == "__main__":
    main()
