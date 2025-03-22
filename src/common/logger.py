import time
from typing import Any

# ANSI color codes
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

def format_message(message_type: str, message: Any) -> str:
    """
    Format a message with timestamp and type prefix.
    
    Args:
        message_type: Type of message
        message: Message content
        
    Returns:
        Formatted message string
    """
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    return f"[{timestamp}] {message_type}: {message}"

def print_system_message(message: Any) -> None:
    """Print a system message in blue."""
    formatted = format_message("SYSTEM", message)
    print(f"{BLUE}{BOLD}{formatted}{RESET}")

def print_info_message(message: Any) -> None:
    """Print an info message in cyan."""
    formatted = format_message("INFO", message)
    print(f"{CYAN}{formatted}{RESET}")

def print_success_message(message: Any) -> None:
    """Print a success message in green."""
    formatted = format_message("SUCCESS", message)
    print(f"{GREEN}{BOLD}{formatted}{RESET}")

def print_warning_message(message: Any) -> None:
    """Print a warning message in yellow."""
    formatted = format_message("WARNING", message)
    print(f"{YELLOW}{formatted}{RESET}")

def print_error_message(message: Any) -> None:
    """Print an error message in red."""
    formatted = format_message("ERROR", message)
    print(f"{RED}{BOLD}{formatted}{RESET}")
