# aeon.py
import os
import sys
import subprocess
import shutil
import textwrap

# --- Configuration ---
# Path to your virtual environment directory
VENV_DIR = "./.venv"

# Name of your Python script and its directory (as a package) for terminal mode
PYTHON_SCRIPT_DIR = "core"
PYTHON_MAIN_MODULE = "aeon"

# Path to the Flask app for web mode
FLASK_APP_PATH = "core/web.py"

# Path to requirements.txt
REQUIREMENTS_FILE = "requirements.txt"

# Path to config.json (not directly used by this script, but kept for consistency)
CONFIG_FILE = "config.yml"

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

# --- Virtual Environment Management ---
def manage_virtual_environment():
    """Checks, creates, and prepares the virtual environment."""
    print_boot_msg(" Checking virtual environment...")

    if not os.path.isdir(VENV_DIR):
        print_error_msg(f" Virtual environment not found at '{VENV_DIR}'.", exit_script=False)
        print_info_msg(" Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)
            print_ok_msg(" Virtual environment created.")
        except subprocess.CalledProcessError:
            print_error_msg(" Failed to create virtual environment. Aborting.")
        except FileNotFoundError:
            print_error_msg(" 'python3' command not found. Ensure Python 3 is installed and in your PATH. Aborting.")

        # Set the virtual environment's Python path for subsequent calls
        python_in_venv = os.path.join(VENV_DIR, "bin", "python")
        if not os.path.exists(python_in_venv):
            print_error_msg(f" Python executable not found in virtual environment at '{python_in_venv}'. Aborting.")

        print_info_msg(" Installing dependencies from 'requirements.txt'...")
        try:
            subprocess.run([python_in_venv, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True)
            print_ok_msg(" Dependencies installed successfully.")
        except subprocess.CalledProcessError:
            print_error_msg(" Failed to install dependencies. Aborting.")
        except FileNotFoundError:
            print_error_msg(f" '{python_in_venv}' not found. Virtual environment creation might have failed. Aborting.")
    else:
        print_ok_msg(" Virtual environment found. Preparing to use it...")

    # Ensure the virtual environment's python is used for subsequent commands
    # This modifies the PATH for this script's subprocesses
    os.environ["PATH"] = os.path.join(VENV_DIR, "bin") + os.pathsep + os.environ["PATH"]

    # Add the current directory to PYTHONPATH so Python can find the 'core' package
    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

# --- Pre-flight Checks ---
# --- Pre-flight Checks ---
def run_preflight_checks():
    """Runs checks for external tools and Python dependencies."""
    print_boot_msg(" Running pre-flight checks...")

    # 1. Verify 'config.yml' exists
    print_info_msg(f" Checking for '{CONFIG_FILE}'...")
    if not os.path.exists(CONFIG_FILE):
        print_error_msg(f" Configuration file '{CONFIG_FILE}' not found. Please create it based on the example provided in the documentation.")
    print_ok_msg(f" '{CONFIG_FILE}' found.")
    
    # 2. Verify core Python libraries (`llama-cpp-python` and others)
    print_info_msg(" Checking for core Python dependencies...")
    try:
        # Use the python executable from the virtual environment
        python_executable = os.path.join(VENV_DIR, "bin", "python")
        subprocess.run(
            [python_executable, "-c", "import llama_cpp, llama_cpp.llama_cpp, langchain_chroma, diffusers, torch"],
            check=True,
            capture_output=True, # Suppress stdout/stderr
            text=True
        )
        print_ok_msg(" All core dependencies found.")
    except subprocess.CalledProcessError as e:
        print_error_msg(textwrap.dedent(f"""
            Core dependencies are not installed or are incomplete within the virtual environment.
            Error: {e.stderr.strip()}
            Please ensure you have run: 'pip install -r {REQUIREMENTS_FILE}' successfully.
        """))
    except FileNotFoundError:
        print_error_msg(f"Python executable not found at '{python_executable}'. Virtual environment might be corrupted.")

    print_boot_msg(" All pre-flight checks passed. Launching AEON...")

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
        choice = "3" # Handle cases where input is redirected/piped
    print("\n")

    python_in_venv = os.path.join(VENV_DIR, "bin", "python")

    if choice == "1":
        # Run in terminal mode
        main_module_path = os.path.join(PYTHON_SCRIPT_DIR, f"{PYTHON_MAIN_MODULE}.py")
        if not os.path.isfile(main_module_path):
            print_error_msg(f" Python main module '{main_module_path}' not found.\n"
                            " Make sure the 'core' directory and 'aeon.py' exist within it.")
        print_boot_msg(" Running AEON in Terminal mode...")
        try:
            subprocess.run([python_in_venv, "-m", f"{PYTHON_SCRIPT_DIR}.{PYTHON_MAIN_MODULE}"], check=True)
        except subprocess.CalledProcessError as e:
            print_error_msg(f" Terminal mode exited with an error: {e}")
    elif choice == "2":
        # Run in web mode
        if not os.path.isfile(FLASK_APP_PATH):
            print_error_msg(f" Flask app file '{FLASK_APP_PATH}' not found.\n"
                            " Make sure 'web.py' exists within the 'core' directory.")
        print_boot_msg(" Running AEON in Web mode...")
        print_boot_msg(" Access the web interface at: http://127.0.0.1:4303")
        try:
            subprocess.run([python_in_venv, FLASK_APP_PATH], check=True)
        except subprocess.CalledProcessError as e:
            print_error_msg(f" Web mode exited with an error: {e}")
    elif choice == "3":
        print_boot_msg(" Exiting AEON. Goodbye!")
    else:
        print_error_msg(" Invalid choice. Please enter 1, 2, or 3.", exit_script=False)

    return choice # Return the choice to handle final messages

# --- Main Execution Flow ---
if __name__ == "__main__":
    os.environ["LLAMA_LOG_LEVEL"] = "0"
    os.system("clear" if os.name == "posix" else "cls") # Clear screen
    print_boot_msg(" Booting AEON")

    manage_virtual_environment()
    run_preflight_checks()
    final_choice = display_menu_and_execute()

    print_boot_msg(" Virtual environment scope ended (not explicitly 'deactivated' in Python, but process exits).")
    if final_choice != "3":
        print_boot_msg(" Nothing will be remembered (conversation state is stateless).", msg_type="WRN", color="31")
    print_boot_msg(" AEON Ended.")
