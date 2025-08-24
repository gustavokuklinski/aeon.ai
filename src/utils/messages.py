# core/utils/messages.py

def print_boot_message(message: str):
    """Prints a boot-time message with yellow color."""
    print(f"\033[1;93m[BOOT]\033[0m {message}")

def print_info_message(message: str):
    """Prints an informational message with blue color."""
    print(f"\033[1;34m[INFO]\033[0m {message}")

def print_command_message(message: str):
    """Prints a command-related message with green color."""
    print(f"\033[1;32m[CMD]\033[0m {message}")

def print_note_message(message: str):
    """Prints a note or warning message with yellow color."""
    print(f"\033[1;33m[NOTE]\033[0m {message}")

def print_error_message(message: str):
    """Prints an error message with red color."""
    print(f"\033[1;91m[ERROR]\033[0m {message}")

def print_aeon_message(message: str):
    """Prints Aeon message with red color."""
    print(f"\033[91m[AEON]:\033[0m {message}")

def print_success_message(message: str):
    """Prints SUCCESS message with red color."""
    print(f"\033[1;32m[SUCCESS]:\033[0m {message}")

def print_warning_message(message: str):
    """Prints SUCCESS message with red color."""
    print(f"\033[1;33m[WARN]\033[0m {message}")
