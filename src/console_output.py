"""
Console output module for TryloByte.
Centralizes all text output and formatting to ensure consistent styling and color.
"""

import sys
import time
import threading
from typing import Optional

try:
    from colorama import init, Fore, Style
    # Initialize colorama for cross-platform ANSI support
    init(autoreset=True)
    
    # Color definitions
    NEON_GREEN = Fore.LIGHTGREEN_EX
    INFO_CYAN = Fore.LIGHTCYAN_EX
    WARNING_YELLOW = Fore.LIGHTYELLOW_EX
    ALERT_RED = Fore.LIGHTRED_EX
    SUCCESS_GREEN = Fore.LIGHTGREEN_EX
    RESET = Style.RESET_ALL
    
    # Color mapping
    COLOR_MAP = {
        'green': Fore.GREEN,
        'red': Fore.RED,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'cyan': Fore.CYAN,
        'magenta': Fore.MAGENTA,
        'white': Fore.WHITE,
        'black': Fore.BLACK,
    }
    
    COLOR_ENABLED = True
except ImportError:
    # Fallback if colorama is not available
    NEON_GREEN = INFO_CYAN = WARNING_YELLOW = ALERT_RED = SUCCESS_GREEN = RESET = ""
    COLOR_MAP = {
        'green': '',
        'red': '',
        'yellow': '',
        'blue': '',
        'cyan': '',
        'magenta': '',
        'white': '',
        'black': '',
    }
    COLOR_ENABLED = False

# Message prefixes
system_message = f"{NEON_GREEN}[ SYSTEM ]{RESET}"
info_message = f"{INFO_CYAN}[ INFO ]{RESET}"
warning_message = f"{WARNING_YELLOW}[ WARNING ]{RESET}"
error_message = f"{ALERT_RED}[ ERROR ]{RESET}"
success_message = f"{SUCCESS_GREEN}[ SUCCESS ]{RESET}"
mission_message = f"{NEON_GREEN}[ MISSION ]{RESET}"
testing_message = f"{WARNING_YELLOW}[ TESTING ]{RESET}"
timeout_message = f"{WARNING_YELLOW}[ TIMEOUT ]{RESET}"

# Lock to prevent interleaved print output from multiple threads
print_lock = threading.Lock()

def print_message(message: str, color: Optional[str] = None, prefix: Optional[str] = None):
    """
    Print a message with optional color and prefix
    
    Args:
        message: The message to print
        color: Optional color to apply (e.g. 'red', 'green')
        prefix: Optional prefix to add to the message
    """
    with print_lock:
        if prefix:
            message = f"{prefix} {message}"
            
        if color and COLOR_ENABLED:
            color_code = COLOR_MAP.get(color.lower(), '')
            print(f"{color_code}{message}{RESET}")
        else:
            print(message)

def print_with_typing_effect(message: str, delay: float = 0.002, prefix: Optional[str] = None, color: Optional[str] = None):
    """
    Print a message with a typewriter effect
    
    Args:
        message: The message to print
        delay: Delay between characters (in seconds)
        prefix: Optional prefix to add to the message
        color: Optional color to apply to the message
    """
    if prefix:
        sys.stdout.write(f"{prefix} ")
        sys.stdout.flush()
        
    color_code = COLOR_MAP.get(color.lower(), '') if color and COLOR_ENABLED else ''
    reset_code = RESET if color and COLOR_ENABLED else ''
    
    for char in message:
        sys.stdout.write(f"{color_code}{char}{reset_code}")
        sys.stdout.flush()
        time.sleep(delay)
    
    sys.stdout.write("\n")
    sys.stdout.flush()

def print_spinner(stop_event, message: str, color: Optional[str] = None):
    """
    Print a spinner animation with a message.
    For simplicity, this just prints the message with no animation.
    
    Args:
        stop_event: Event to signal when to stop the spinner
        message: Message to display with the spinner
        color: Optional color to apply to the message
    """
    print_message(message, color=color)

def print_loading_bar(prefix: str = None, duration: int = 3, width: int = 40, color: Optional[str] = None):
    """
    Print a loading bar animation.
    For simplicity, this just prints a completed loading bar.
    
    Args:
        prefix: Optional prefix to add before the loading bar
        duration: Duration of the animation in seconds (ignored)
        width: Width of the loading bar in characters
        color: Optional color to apply to the loading bar
    """
    with print_lock:
        if prefix:
            print(prefix)
            
        bar = "█" * width
        percentage = "100%"
        
        if color and COLOR_ENABLED:
            color_code = COLOR_MAP.get(color.lower(), '')
            print(f"{color_code}[{bar}] {percentage}{RESET}")
        else:
            print(f"[{bar}] {percentage}")

def print_system_message(message: str, typing_effect: bool = False):
    """Print a system message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=system_message, color='green')
    else:
        print_message(message, prefix=system_message, color='green')

def print_info_message(message: str, typing_effect: bool = False):
    """Print an info message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=info_message, color='cyan')
    else:
        print_message(message, prefix=info_message, color='cyan')

def print_warning_message(message: str, typing_effect: bool = False):
    """Print a warning message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=warning_message, color='yellow')
    else:
        print_message(message, prefix=warning_message, color='yellow')

def print_error_message(message: str, typing_effect: bool = False):
    """Print an error message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=error_message, color='red')
    else:
        print_message(message, prefix=error_message, color='red')

def print_success_message(message: str, typing_effect: bool = False):
    """Print a success message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=success_message, color='green')
    else:
        print_message(message, prefix=success_message, color='green')

def print_mission_message(message: str, typing_effect: bool = False):
    """Print a mission message."""
    if typing_effect:
        print_with_typing_effect(message, prefix=mission_message, color='green')
    else:
        print_message(message, prefix=mission_message, color='green')

def print_testing_message(message: str):
    """Print a testing message."""
    print_message(message, prefix=testing_message, color='yellow')

def print_timeout_message(message: str):
    """Print a timeout message."""
    print_message(message, prefix=timeout_message, color='yellow')

def print_table(headers: list, data: list, color: Optional[str] = None):
    """
    Print a formatted table.
    
    Args:
        headers: List of column headers
        data: List of rows, where each row is a list of values
        color: Optional color to apply to the table
    """
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header row
    header = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)
    
    # Print header
    with print_lock:
        if color and COLOR_ENABLED:
            print(f"{COLOR_MAP.get(color.lower(), '')}{header}{RESET}")
            print(f"{COLOR_MAP.get(color.lower(), '')}{separator}{RESET}")
        else:
            print(header)
            print(separator)
        
        # Print data rows
        for row in data:
            row_str = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            if color and COLOR_ENABLED:
                print(f"{COLOR_MAP.get(color.lower(), '')}{row_str}{RESET}")
            else:
                print(row_str)
