import os
import sys
import psutil
import subprocess
import time
from pathlib import Path

# Get the absolute path to the project root directory
project_root = Path(__file__).resolve().parent

# Add the project root to the system path to allow imports from subdirectories
sys.path.insert(0, str(project_root))

PYTHON_SCRIPT_DIR = "src"
PYTHON_MAIN_MODULE = "main"
FLASK_APP_PATH = "src/web.py"
SCRIPTS_DIR = "scripts"

def colored_print(message, color_code):
    """Prints a message with ANSI color codes."""
    print(f"\033[{color_code}m{message}\033[0m")

def print_boot_msg(message, msg_type="BOOT", color="93"):
    """Prints a standardized boot message."""
    colored_print(f"[{msg_type}]{message}", f"1;{color}")

def print_info_msg(message):
    """Prints an info message."""
    colored_print(f"[INFO]{message}", "1;34")

def print_ok_msg(message):
    """Prints an OK message."""
    colored_print(f"[OK]{message}", "1;32")

def print_error_msg(message, exit_script=True):
    """Prints an error message and optionally exits the script."""
    colored_print(f"[ERROR]{message}", "91")
    if exit_script:
        sys.exit(1)

def get_resource_path(relative_path):
    """Gets the correct path for a resource, handling PyInstaller's temp directory."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return os.path.join(base_path, relative_path)

def run_terminal_mode():
    """Starts the application in terminal mode."""
    print_boot_msg(" Running AEON in Terminal mode...")
    try:
        # This assumes src/main.py is a runnable script
        subprocess.run([sys.executable, "src/main.py"], check=True)
        print_ok_msg("Terminal mode finished.")
    except subprocess.CalledProcessError as e:
        print_error_msg(f"Terminal mode exited with an error: {e}")

def run_web_mode():
    """Starts the application in web mode."""
    print_boot_msg(" Running AEON in Web mode...")
    print_boot_msg(" Access the web interface at: http://0.0.0.0:7860")
    try:
        # This assumes src/web.py contains a server that starts on its own
        # and listens on 0.0.0.0:7860
        subprocess.run([sys.executable, "src/web.py"], check=True)
    except Exception as e:
        print_error_msg(f"Web mode exited with an error: {e}")

def display_menu_and_execute():
    """Displays the main menu and handles user input."""
    print("\033[38;5;160m___________________________________________________\033[0m")
    print("")
    print("\033[38;5;160m      ###       #######     #######    ###     ### \033[0m")
    print("\033[38;5;160m    ### ###     ##        ###     ###  ######  ### \033[0m")
    print("\033[38;5;160m   ###   ###    #######   ###     ###  ###  ## ### \033[0m")
    print("\033[38;5;160m  ###     ###   ##        ###     ###  ###   ##### \033[0m")
    print("\033[38;5;160m ##         ##  #######     #######    ###     ### \033[0m")
    print("\033[38;5;160m___________________________________________________\033[0m")
    print("")
    print(f"SYSM: {sys.platform}")
    print(f"RAM TTL: {round(psutil.virtual_memory().total / (1024**3), 2)} GB | USED: {round(psutil.virtual_memory().used / (1024**3), 2)} GB | FREE: {round(psutil.virtual_memory().available / (1024**3), 2)} GB")
    print("Type the \033[1;1;91m[NUMBER]\033[0m option:")
    print("\033[1;1;33m[1] Terminal\033[0m")
    print("\033[1;1;33m[2] WebGPT - https://:4303\033[0m")
    print("\033[1;1;33m[3] Exit\033[0m")
    print("")

    try:
        choice = input("\033[1;91m[NUMBER]\033[0m \033[1;33m>> \033[0m").strip()
    except EOFError:
        choice = "4"

    if choice == "1":
        run_terminal_mode()
    elif choice == "2":
        run_web_mode()
    elif choice == "3":
        print_boot_msg(" Exiting AEON. Goodbye!")
        sys.exit(0)
    else:
        print_error_msg(" Invalid choice. Please enter a number from 1 to 3.")
    
    return choice

if __name__ == "__main__":
    print_boot_msg(" Booting AEON")
    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

    # Check for command-line arguments to bypass the menu
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "terminal":
            run_terminal_mode()
        elif command == "web":
            run_web_mode()
        else:
            print_error_msg(f"Invalid command-line argument: '{command}'. Please use 'terminal' or 'web'.", exit_script=False)
            display_menu_and_execute()
    else:
        # No arguments, show the menu
        display_menu_and_execute()
