import os
import sys
import subprocess
import shutil
from pathlib import Path

# --- Constants and Helper Functions ---
PLUGINS_DIR = Path("./plugins")

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

# --- Core Plugin Management Functions ---

def list_plugins():
    """Lists all currently installed plugins."""
    print_boot_msg("\nListing installed plugins...")
    
    if not PLUGINS_DIR.is_dir() or not any(PLUGINS_DIR.iterdir()):
        print_info_msg("No plugins found.")
        return []

    plugins = [p for p in PLUGINS_DIR.iterdir() if p.is_dir()]
    if not plugins:
        print_info_msg("No plugins found.")
        return []

    for i, plugin in enumerate(plugins, 1):
        print_info_msg(f" {i}. {plugin.name}")
    
    return plugins

def add_plugin(repo_url, name=None):
    """
    Adds a new plugin as a Git submodule.

    Args:
        repo_url (str): The Git repository URL of the plugin.
        name (str, optional): The name for the plugin directory.
                              If not provided, it's inferred from the URL.
    """
    if name is None:
        name = repo_url.split('/')[-1].replace('.git', '')

    plugins_dir = 'plugins'
    target_path = os.path.join(plugins_dir, name)

    # Ensure the plugins directory exists
    if not os.path.exists(plugins_dir):
        print(f"[INFO] Creating plugins directory: {plugins_dir}")
        os.makedirs(plugins_dir)

    # Check if the target directory already exists
    force_flag = ''
    if os.path.exists(target_path):
        print(f"[WARNING] Directory '{target_path}' already exists. Attempting to reuse with '--force'.")
        force_flag = '--force'
    
    try:
        print(f"[INFO] Adding plugin from '{repo_url}' into '{target_path}'...")
        cmd = ['git', 'submodule', 'add', repo_url, target_path]
        if force_flag:
            cmd.insert(3, force_flag)

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[INFO] Plugin added successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to add plugin. Git command failed: {e.stderr}")
        print(f"[DEBUG] Full command: {' '.join(e.cmd)}")
    except FileNotFoundError:
        print("[ERROR] 'git' command not found. Please ensure Git is installed and in your system's PATH.")

def delete_plugin():
    """Deletes a selected plugin."""
    plugins = list_plugins()
    if not plugins:
        return

    try:
        choice = int(input("\nEnter the number of the plugin to delete: "))
        if 1 <= choice <= len(plugins):
            plugin_to_delete = plugins[choice - 1]
            confirm = input(f"Are you sure you want to delete '{plugin_to_delete.name}'? (yes/no): ").lower()
            
            if confirm == "yes":
                print_info_msg(f"Removing plugin '{plugin_to_delete.name}'...")
                
                # Deinitialize submodule and remove from git index
                try:
                    subprocess.run(
                        ["git", "submodule", "deinit", "-f", str(plugin_to_delete)],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    subprocess.run(
                        ["git", "rm", "-f", str(plugin_to_delete)],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    
                    # Manually remove the directory as git rm may fail to delete it
                    if plugin_to_delete.is_dir():
                        shutil.rmtree(plugin_to_delete)
                    
                    print_ok_msg(f"Plugin '{plugin_to_delete.name}' deleted successfully.")
                except subprocess.CalledProcessError as e:
                    print_error_msg(f"Failed to remove plugin with git: {e.stderr.strip()}", exit_script=False)
                
            else:
                print_info_msg("Deletion cancelled.")
        else:
            print_error_msg("Invalid choice. Please enter a number from the list.", exit_script=False)

    except ValueError:
        print_error_msg("Invalid input. Please enter a number.", exit_script=False)
    except Exception as e:
        print_error_msg(f"An unexpected error occurred: {e}", exit_script=False)

# --- Main Menu ---

def main_menu():
    """Displays the main menu and handles user input."""
    while True:
        print("\n--- AEON Plugin Manager ---")
        print("1. List Plugins")
        print("2. Add a new plugin")
        print("3. Delete a plugin")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            list_plugins()
        elif choice == '2':
            repo_url = input("Enter the Git repository URL: ").strip()
            name = input("Enter a name for the plugin (or press Enter to use default): ").strip()
            if not repo_url:
                print_error_msg("Repository URL cannot be empty.", exit_script=False)
                continue
            add_plugin(repo_url, name if name else None)
        elif choice == '3':
            delete_plugin()
        elif choice == '4':
            print_ok_msg("Exiting Plugin Manager.")
            sys.exit(0)
        else:
            print_error_msg("Invalid choice. Please enter a number from 1 to 4.", exit_script=False)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print_boot_msg("AEON Plugin Manager")
    main_menu()
