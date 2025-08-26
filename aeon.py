# aeon.py
import os
import sys
import subprocess
import textwrap

# --- Configuration ---
VENV_DIR = "./.venv"
PYTHON_SCRIPT_DIR = "src"
PYTHON_MAIN_MODULE = "main"
FLASK_APP_PATH = "src/libs/webServer.py"

# --- Helper Functions for Colored Output ---
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

# --- Main Menu and Execution ---
def display_menu_and_execute():
    """Displays the main menu and executes the chosen mode."""
    print("\n")
    print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
    print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
    print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
    print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
    print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
    print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")
    colored_print("[1] Terminal", "91")
    colored_print("[2] Web Chat", "91")
    colored_print("[3] Exit", "91")
    print("\n-------------------------------------")
    try:
        choice = input("\033[1;36m[PROMPT]\033[0m \033[1;92m>> \033[0m").strip()
    except EOFError:
        choice = "3"
    print("\n")
    
    # Check if the virtual environment exists before proceeding
    if not os.path.isdir(VENV_DIR):
        print_error_msg(f"Virtual environment not found at '{VENV_DIR}'. Please run install.py first.")
    
    # Determine the correct virtual environment executable path based on OS
    if sys.platform == "win32":
        python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
    else:
        python_executable = os.path.join(VENV_DIR, "bin", "python")

    # Add the current directory to PYTHONPATH for package discovery
    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

    if choice == "1":
        # Run in terminal mode
        main_module_path = os.path.join(PYTHON_SCRIPT_DIR, f"{PYTHON_MAIN_MODULE}.py")
        if not os.path.isfile(main_module_path):
            print_error_msg(f" Python main module '{main_module_path}' not found.\n"
                             " Make sure the 'src' directory and 'aeon.py' exist within it.")
        print_boot_msg(" Running AEON in Terminal mode...")
        try:
            subprocess.run([python_executable, "-m", f"{PYTHON_SCRIPT_DIR}.{PYTHON_MAIN_MODULE}"], check=True)
        except subprocess.CalledProcessError as e:
            print_error_msg(f" Terminal mode exited with an error: {e}")
    elif choice == "2":
        # Run in web mode
        if not os.path.isfile(FLASK_APP_PATH):
            print_error_msg(f" Flask app file '{FLASK_APP_PATH}' not found.\n"
                             " Make sure 'webServer.py' exists within the 'src/libs' directory.")
        print_boot_msg(" Running AEON in Web mode...")
        print_boot_msg(" Access the web interface at: http://127.0.0.1:4303")
        try:
            subprocess.run([python_executable, FLASK_APP_PATH], check=True)
        except subprocess.CalledProcessError as e:
            print_error_msg(f" Web mode exited with an error: {e}")
    elif choice == "3":
        print_boot_msg(" Exiting AEON. Goodbye!")
    else:
        print_error_msg(" Invalid choice. Please enter 1, 2, or 3.", exit_script=False)
    
    return choice

# --- Main Execution Flow ---
if __name__ == "__main__":
    os.environ["LLAMA_LOG_LEVEL"] = "0"
    os.system("cls" if os.name == "nt" else "clear")
    
    print_boot_msg(" Booting AEON")
    final_choice = display_menu_and_execute()

    print_boot_msg(" Virtual environment scope ended (not explicitly 'deactivated' in Python, but process exits).")
    if final_choice != "3":
        print_boot_msg(" You conversation is stored at: /data/memory/.", msg_type="BOOT", color="93")
    print_boot_msg(" AEON Ended.")