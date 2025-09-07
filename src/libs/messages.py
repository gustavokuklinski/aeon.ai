# core/libs/messages.py

def print_boot_message(message: str):
    print(f"\033[1;93m[BOOT]\033[0m {message}")


def print_info_message(message: str):
    print(f"\033[1;34m[INFO]\033[0m {message}")


def print_command_message(message: str):
    print(f"\033[1;32m[CMMD]\033[0m {message}")


def print_note_message(message: str):
    print(f"\033[1;33m[NOTE]\033[0m {message}")


def print_error_message(message: str):
    print(f"\033[1;91m[ERRR]\033[0m {message}")


def print_aeon_message(message: str):
    print(f"\033[91m[AEON]:\033[0m {message}")


def print_success_message(message: str):
    print(f"\033[1;32m[SUCS]:\033[0m {message}")


def print_warning_message(message: str):
    print(f"\033[1;33m[WARN]\033[0m {message}")

def print_plugin_message(message: str):
    print(f"\033[1;33m[PLUG]\033[0m {message}")


def print_chat_message(message: str):
    print(f"\033[1;33m[CHAT]\033[0m {message}")

def print_source_message(message: str):
    print(f"\033[1;32m[SOURCE]:\033[0m {message}")

def print_think_message(message: str):
    print(f"\033[91m[...]:\033[0m {message}")