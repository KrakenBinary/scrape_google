import time
import sys
from typing import Any, Optional

# ANSI color codes
NEON_GREEN = "\033[38;5;46m"  # Bright green (neon)
INFO_CYAN = "\033[36m"
WARNING_YELLOW = "\033[33m"
ALERT_RED = "\033[31m"
SUCCESS_GREEN = "\033[32m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_with_typing_effect(message: str, delay: float = 0.02, color: str = RESET) -> None:
    """
    Print text with a typing effect.
    
    Args:
        message: Message to print
        delay: Delay between characters in seconds
        color: ANSI color code to use
    """
    for char in message:
        sys.stdout.write(f"{color}{char}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")

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

def print_message(message: Any, message_type: str = "INFO", color: str = RESET, 
                 typing_effect: bool = False, delay: float = 0.02) -> None:
    """
    Generic message printer with optional typing effect.
    
    Args:
        message: Message to print
        message_type: Type of message
        color: ANSI color code to use
        typing_effect: Whether to use typing effect
        delay: Delay between characters for typing effect
    """
    formatted = format_message(message_type, message)
    
    if typing_effect:
        print_with_typing_effect(formatted, delay, color)
    else:
        print(f"{color}{formatted}{RESET}")

def print_system_message(message: Any, typing_effect: bool = False) -> None:
    """
    Print a system message in blue.
    
    Args:
        message: Message to print
        typing_effect: Whether to use typing effect
    """
    if typing_effect:
        print_with_typing_effect(format_message("SYSTEM", message), color=BLUE)
    else:
        formatted = format_message("SYSTEM", message)
        print(f"{BLUE}{BOLD}{formatted}{RESET}")

def print_info_message(message: Any, typing_effect: bool = False) -> None:
    """
    Print an info message in cyan.
    
    Args:
        message: Message to print
        typing_effect: Whether to use typing effect
    """
    if typing_effect:
        print_with_typing_effect(format_message("INFO", message), color=CYAN)
    else:
        formatted = format_message("INFO", message)
        print(f"{CYAN}{formatted}{RESET}")

def print_success_message(message: Any, typing_effect: bool = False) -> None:
    """
    Print a success message in green.
    
    Args:
        message: Message to print
        typing_effect: Whether to use typing effect
    """
    if typing_effect:
        print_with_typing_effect(format_message("SUCCESS", message), color=GREEN)
    else:
        formatted = format_message("SUCCESS", message)
        print(f"{GREEN}{BOLD}{formatted}{RESET}")

def print_warning_message(message: Any, typing_effect: bool = False) -> None:
    """
    Print a warning message in yellow.
    
    Args:
        message: Message to print
        typing_effect: Whether to use typing effect
    """
    if typing_effect:
        print_with_typing_effect(format_message("WARNING", message), color=YELLOW)
    else:
        formatted = format_message("WARNING", message)
        print(f"{YELLOW}{formatted}{RESET}")

def print_error_message(message: Any, typing_effect: bool = False) -> None:
    """
    Print an error message in red.
    
    Args:
        message: Message to print
        typing_effect: Whether to use typing effect
    """
    if typing_effect:
        print_with_typing_effect(format_message("ERROR", message), color=RED)
    else:
        formatted = format_message("ERROR", message)
        print(f"{RED}{BOLD}{formatted}{RESET}")

# Shorthand functions without formatting, for use in other functions
def system_message(message: str) -> str:
    """Return a system message string with color formatting."""
    return f"{BLUE}{BOLD}{message}{RESET}"

def info_message(message: str) -> str:
    """Return an info message string with color formatting."""
    return f"{CYAN}{message}{RESET}"

def success_message(message: str) -> str:
    """Return a success message string with color formatting."""
    return f"{GREEN}{BOLD}{message}{RESET}"

def warning_message(message: str) -> str:
    """Return a warning message string with color formatting."""
    return f"{YELLOW}{message}{RESET}"

def error_message(message: str) -> str:
    """Return an error message string with color formatting."""
    return f"{RED}{BOLD}{message}{RESET}"
