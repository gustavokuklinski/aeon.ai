# src/utils/delete.py
import shutil
from pathlib import Path

from src.libs.messages import (
    print_info_message,
    print_success_message,
    print_error_message,
    print_note_message
)
from src.config import MEMORY_DIR

def deleteConversation(user_input: str, session_vars: dict):
    try:
        command_parts = user_input.split(" ")
        if len(command_parts) < 2:
            print_error_message("Usage: /delete <NUMBER>")
            return

        conv_id = command_parts[1]
        memory_dir_path = Path(MEMORY_DIR)

        if not memory_dir_path:
            print_error_message("MEMORY_DIR is not set in session variables.")
            return

        conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if session_vars.get("current_memory_path") and session_vars["current_memory_path"] in conversation_dirs:
            conversation_dirs.remove(session_vars["current_memory_path"])

        idx = int(conv_id) - 1
        
        if 0 <= idx < len(conversation_dirs):
            selected_conv_path = conversation_dirs[idx]
            
            if selected_conv_path == session_vars.get("current_memory_path"):
                print_error_message("Cannot delete the current active conversation.")
                return

            print_note_message(
                f"Are you sure you want to permanently delete "
                f"'{selected_conv_path.name}' and all its contents? (y/n)"
            )
            confirmation = input().strip().lower()

            if confirmation == 'y':
                shutil.rmtree(selected_conv_path)
                print_success_message(f"Conversation '{selected_conv_path.name}' successfully deleted.")
            else:
                print_info_message("Deletion cancelled.")
        else:
            print_error_message("Invalid conversation number.")
            print_info_message("Use /list to see available conversations.")
            
    except ValueError:
        print_error_message("Invalid input. Please provide a valid number.")
    except IndexError:
        print_error_message("Invalid conversation number.")
        print_info_message("Use /list to see available conversations.")
    except Exception as e:
        print_error_message(f"An unexpected error occurred: {e}")
