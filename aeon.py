import os
import sys
import psutil
import platform
from importlib import import_module
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

PYTHON_SCRIPT_DIR = "src"
PYTHON_MAIN_MODULE = "main"
FLASK_APP_PATH = "src/web.py"

def colored_print(message, color_code):
    print(f"\033[{color_code}m{message}\033[0m")

def print_boot_msg(message, msg_type="BOOT", color="93"):
    colored_print(f"[{msg_type}]{message}", f"1;{color}")

def print_info_msg(message):
    colored_print(f"[INFO]{message}", "1;34")

def print_ok_msg(message):
    colored_print(f"[OK]{message}", "1;32")

def print_error_msg(message, exit_script=True):
    colored_print(f"[ERROR]{message}", "91")
    if exit_script:
        sys.exit(1)

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return os.path.join(base_path, relative_path)


def display_menu_and_execute():
    
    print("")
    print("\033[38;5;160m_______________________________________________________\033[0m")
    print("")
    print("\033[38;5;160m      ###       #########      ######     ###      ### \033[0m")
    print("\033[38;5;160m    ### ###     ##          ###      ###  ######   ### \033[0m")
    print("\033[38;5;160m   ###   ###    #########  ###       ###  ###  ### ### \033[0m")
    print("\033[38;5;160m  ###     ###   ##          ##       ###  ###   ###### \033[0m")
    print("\033[38;5;160m ##         ##  #########     #######     ###      ### \033[0m")
    print("\033[38;5;160m_______________________________________________________\033[0m")
    print("")
    print(f"SYSM:     {sys.platform} - {platform.processor()}")
    print(f"RAM TTL:  {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    print(f"RAM USD:  {round(psutil.virtual_memory().used / (1024**3), 2)} GB")
    print(f"RAM AVL:  {round(psutil.virtual_memory().available / (1024**3), 2)} GB")
    print("")
    print("Type the \033[1;1;91m[NUMBER]\033[0m option:")
    print("- \033[1;1;33m[1] Terminal\033[0m")
    print("- \033[1;1;33m[2] Web - https://localhost:4303\033[0m")
    print("- \033[1;1;33m[3] Exit\033[0m")
    print("")

    try:
        choice = input("\033[1;91m[PROMPT]\033[0m \033[1;33m>> \033[0m").strip()
    except EOFError:
        choice = "3"

    os.environ["PYTHONPATH"] = os.getcwd() + os.pathsep + os.environ.get("PYTHONPATH", "")

    if choice == "1":
        print_boot_msg(" Running AEON in Terminal mode...")
        try:
            main_module = import_module(f"{PYTHON_SCRIPT_DIR}.{PYTHON_MAIN_MODULE}")
            main_module.main()
        except ImportError:
            print_error_msg(f"Could not import module: '{PYTHON_SCRIPT_DIR}.{PYTHON_MAIN_MODULE}'")
        except Exception as e:
            print_error_msg(f"Terminal mode exited with an error: {e}")

    elif choice == "2":
        print_boot_msg(" Running AEON in Web mode...")
        print_boot_msg(" Access the web interface at: http://0.0.0.0:4303")
        try:
            web_module = import_module(f"{PYTHON_SCRIPT_DIR}.{Path(FLASK_APP_PATH).stem}")
            web_module.app.run(host="0.0.0.0", port=4303, debug=False)
        except ImportError:
            print_error_msg(f"Could not import module: '{PYTHON_SCRIPT_DIR}.{Path(FLASK_APP_PATH).stem}'")
        except Exception as e:
            print_error_msg(f"Web mode exited with an error: {e}")

    elif choice == "3":
        print_boot_msg(" Exiting AEON. Goodbye!")
    else:
        print_error_msg(" Invalid choice. Please enter 1, 2, or 3.", exit_script=False)
    
    return choice


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    
    print_boot_msg(" Booting AEON")
    display_menu_and_execute()
