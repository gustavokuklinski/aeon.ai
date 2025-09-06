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

def add_plugin():
    """Adds a new plugin by cloning a Git repository."""
    print_boot_msg("\nAdding a new plugin...")
    repo_url = input("Enter the Git repository URL: ")

    try:
        # Extract plugin name from URL
        plugin_name = repo_url.split('/')[-1].replace(".git", "")
        plugin_path = PLUGINS_DIR / plugin_name
        
        # Check if plugin already exists
        if plugin_path.exists():
            print_error_msg(f"A directory for plugin '{plugin_name}' already exists.")
            return

        print_info_msg(f"Cloning '{repo_url}' into '{plugin_path}'...")
        subprocess.run(
            ["git", "submodule", "add", repo_url, str(plugin_path)],
            check=True,
            capture_output=True,
            text=True
        )
        print_ok_msg(f"Plugin '{plugin_name}' cloned and added successfully.")
        
    except subprocess.CalledProcessError as e:
        print_error_msg(f"Failed to add plugin. Git command failed: {e.stderr.strip()}", exit_script=False)
    except Exception as e:
        print_error_msg(f"An unexpected error occurred: {e}", exit_script=False)

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
            add_plugin()
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
