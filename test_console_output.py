#!/usr/bin/env python3
"""
Test script for the console_output module
"""

from src.console_output import (
    print_message, print_with_typing_effect,
    print_system_message, print_info_message, print_warning_message,
    print_error_message, print_success_message,
    system_message, info_message, warning_message, error_message, success_message
)

print("\nTesting console_output module...")

# Test basic message printing
print("\nBasic message printing:")
print_message("This is a plain message")
print_message("This is a blue message", color="blue")
print_message("This is a green message", color="green")
print_message("This is a yellow message", color="yellow")
print_message("This is a red message", color="red")

# Test message prefixes
print("\nMessage prefixes:")
print(system_message + " System message prefix")
print(info_message + " Info message prefix")
print(warning_message + " Warning message prefix")
print(error_message + " Error message prefix")
print(success_message + " Success message prefix")

# Test specialized message functions
print("\nSpecialized message functions:")
print_system_message("This is a system message")
print_info_message("This is an information message")
print_warning_message("This is a warning message")
print_error_message("This is an error message")
print_success_message("This is a success message")

# Test typed message functions
print("\nTyped message functions:")
print_system_message("This is a typed system message", typing_effect=True)
print_info_message("This is a typed info message", typing_effect=True)
print_warning_message("This is a typed warning message", typing_effect=True)
print_error_message("This is a typed error message", typing_effect=True)
print_success_message("This is a typed success message", typing_effect=True)

print("\nAll tests completed!")
