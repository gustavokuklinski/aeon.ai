# install.py
import os
import sys
import subprocess
import shutil
import textwrap

# --- Configuration ---
VENV_DIR = "./.venv"
REQUIREMENTS_FILE = "requirements.txt"
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

# --- Virtual Environment and Dependency Management ---
def manage_virtual_environment():
    """Checks, creates, and prepares the virtual environment."""
    print_boot_msg(" Checking virtual environment...")
    
    # Determine the correct virtual environment executable path based on OS
    if sys.platform == "win32":
        python_executable = os.path.join(VENV_DIR, "Scripts", "python.exe")
        bin_dir = "Scripts"
    else:
        python_executable = os.path.join(VENV_DIR, "bin", "python")
        bin_dir = "bin"
    
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

    # Check for the executable before proceeding
    if not os.path.exists(python_executable):
        print_error_msg(f" Python executable not found in virtual environment at '{python_executable}'. Aborting.")
        
    print_info_msg(" Installing dependencies from 'requirements.txt'...")
    try:
        subprocess.run([python_executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], check=True)
        print_ok_msg(" Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print_error_msg(" Failed to install dependencies. Aborting.")
    except FileNotFoundError:
        print_error_msg(f" '{python_executable}' not found. Virtual environment creation might have failed. Aborting.")

    return python_executable, bin_dir

def run_preflight_checks(python_executable):
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
        subprocess.run(
            [python_executable, "-c", "import llama_cpp, langchain_chroma, diffusers, torch"],
            check=True,
            capture_output=True,
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

    print_boot_msg(" All pre-flight checks passed. Installation is complete.")


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print_boot_msg(" AEON Installer")
    
    python_executable, _ = manage_virtual_environment()
    run_preflight_checks(python_executable)