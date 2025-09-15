import os
import sys
import psutil
import platform
import subprocess
import time
from importlib import import_module
from pathlib import Path

project_root = Path(__file__).resolve().parent
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
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return os.path.join(base_path, relative_path)

def build_and_run_docker_image():
    container_name = "aeon-container"
    image_name = "aeon"
    
    print_boot_msg(" Building Docker image...")
    dockerfile_path = project_root / "Dockerfile"
    if not dockerfile_path.exists():
        print_error_msg(f"Dockerfile not found at '{dockerfile_path}'. Aborting.")
        return

    try:
        subprocess.run(["docker", "build", "-t", image_name, "."], check=True)
        print_ok_msg(f"Docker image '{image_name}' built successfully.")

        print_info_msg("Cleaning up any previous container...")
        subprocess.run(["docker", "stop", container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", container_name], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print_boot_msg(" Running Docker container...")
        subprocess.run(
            ["docker", "run", "--name", container_name, "-d", "-p", "4303:4303", image_name],
            check=True
        )
        print_ok_msg(f"Container '{container_name}' is running. Access the web interface at: http://0.0.0.0:4303")
        
        input("\nPress Enter to stop the container and exit...")
        
    except FileNotFoundError:
        print_error_msg("Docker command not found. Please ensure Docker is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print_error_msg(f"Docker operation failed with an error: {e}")
    finally:
        print_info_msg("\nStopping and removing container...")
        try:
            subprocess.run(["docker", "stop", container_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["docker", "rm", container_name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print_ok_msg("Container stopped and removed.")
        except subprocess.CalledProcessError:
            print_error_msg(f"Failed to stop or remove container '{container_name}'. It may not have been running.")
        
        print_info_msg("Removing Docker image...")
        try:
            subprocess.run(["docker", "rmi", image_name], check=True)
            print_ok_msg(f"Docker image '{image_name}' removed.")
        except subprocess.CalledProcessError:
            print_error_msg(f"Failed to remove image '{image_name}'. It might be in use by another container.")


def install_for_hacking():
    """Runs the installation script for hacking tools."""
    print_boot_msg(" Running installation for h4ck1ng...")
    h4ck1ng_script_path = Path(SCRIPTS_DIR) / "install.py"
    if not h4ck1ng_script_path.exists():
        print_error_msg(f"Installation script not found at '{h4ck1ng_script_path}'. Aborting.")
        return
    try:
        subprocess.run([sys.executable, str(h4ck1ng_script_path)], check=True)
        print_ok_msg("Hacking tools installed successfully.")
    except subprocess.CalledProcessError as e:
        print_error_msg(f"Installation script failed with an error: {e}")

def display_menu_and_execute():
    
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
    print("\033[1;1;33m[1] Terminal               | [4] Install for developers\033[0m")
    print("\033[1;1;33m[2] WebGPT - https://:4303 | [5] Exit\033[0m")
    print("\033[1;1;33m[3] Build and Run Docker\033[0m")
    print("")

    try:
        choice = input("\033[1;91m[NUMBER@aeon]\033[0m \033[1;33m>> \033[0m").strip()
    except EOFError:
        choice = "6"

    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

    if choice == "1":
        print_boot_msg(" Running AEON in Terminal mode...")
        try:
            subprocess.run([sys.executable, "-m", "src.main"], check=True)
            print_ok_msg("Terminal mode finished.")
        except subprocess.CalledProcessError as e:
            print_error_msg(f"Terminal mode exited with an error: {e}")

    elif choice == "2":
        print_boot_msg(" Running AEON in Web mode...")
        print_boot_msg(" Access the web interface at: http://0.0.0.0:4303")
        try:
            web_module = subprocess.run([sys.executable, "-m", "src.web"], check=True)
            web_module.app.run(host="0.0.0.0", port=4303, debug=False)
        except ImportError:
            print_error_msg(f"Could not import module: '{PYTHON_SCRIPT_DIR}.{Path(FLASK_APP_PATH).stem}'")
        except Exception as e:
            print_error_msg(f"Web mode exited with an error: {e}")

    elif choice == "3":
        build_and_run_docker_image()

    elif choice == "4":
        install_for_hacking()

    elif choice == "5":
        print_boot_msg(" Exiting AEON. Goodbye!")
        sys.exit(0)
    else:
        print_error_msg(" Invalid choice. Please enter a number from 1 to 6.", exit_script=False)
    
    return choice

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    print_boot_msg(" Booting AEON")
    display_menu_and_execute()
