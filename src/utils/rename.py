# src/utils/rename.py
from pathlib import Path
from src.libs.messages import (
    print_info_message,
    print_error_message
)
from src.config import MEMORY_DIR

def renameConversation(user_input: str, memory_dir_path: Path):
    """Renames a conversation folder and its main JSON file."""
    try:
        # Split the input to get the conversation number and new name
        parts = user_input.split(" ", 2)
        if len(parts) < 3:
            print_error_message(
                "Usage: /rename <NUMBER> <NEW_NAME>")
            return False  # Return False on failure

        memory_dir_path = Path(MEMORY_DIR)
        conv_number_str = parts[1].strip()
        new_name = parts[2].strip()

        # Check if new name is valid
        if not new_name:
            print_error_message("New name cannot be empty.")
            return False

        # Get list of existing conversations
        conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir()
                                   and not d.name.startswith('.')] # <-- REMOVED .sorted()

        # Validate the conversation number
        try:
            conv_index = int(conv_number_str) - 1
            if not (0 <= conv_index < len(conversation_dirs)):
                print_error_message(
                    "Invalid conversation number.")
                return False
        except ValueError:
            print_error_message(
                "Invalid input. Please enter a number for the conversation.")
            return False

        current_conv_dir = conversation_dirs[conv_index]
        current_name = current_conv_dir.name

        # Construct the new path and check for conflicts
        new_conv_dir = memory_dir_path / new_name
        if new_conv_dir.exists():
            print_error_message(
                f"A conversation named '{new_name}' already exists.")
            return False

        # Rename the directory
        current_conv_dir.rename(new_conv_dir)

        # Find and rename the JSON file inside the newly renamed directory
        old_json_file = next((f for f in new_conv_dir.glob("*.json")), None)
        if old_json_file:
            new_json_path = new_conv_dir / f"{new_name}.json"
            old_json_file.rename(new_json_path)

        print_info_message(
            f"Chat '{current_name}' successfully renamed to '{new_name}'.")
        return True  # Return True on success
    except Exception as e:
        print_error_message(
            f"An error occurred during renaming: {e}")
        return False

def renameConversationForWeb(conv_id: str, new_name: str, memory_dir_path: Path):
    """
    Renames a conversation folder and its main JSON file for a web-based request.
    This function uses the conversation ID directly, which is more robust
    than relying on a numbered list.
    """
    try:
        # Construct the path to the current conversation directory
        current_conv_dir = memory_dir_path / conv_id

        # Check if the directory exists
        if not current_conv_dir.is_dir():
            return False, "Conversation not found."

        # Check if new name is valid
        if not new_name.strip():
            return False, "New name cannot be empty."

        # Construct the new path and check for conflicts
        new_conv_dir = memory_dir_path / new_name
        if new_conv_dir.exists():
            return False, f"A conversation named '{new_name}' already exists."

        # Rename the directory
        current_conv_dir.rename(new_conv_dir)

        # Find and rename the JSON file inside the newly renamed directory
        old_json_file = next((f for f in new_conv_dir.glob("*.json")), None)
        if old_json_file:
            new_json_path = new_conv_dir / f"{new_name}.json"
            old_json_file.rename(new_json_path)

        print_info_message(f"Chat '{conv_id}' successfully renamed to '{new_name}'.")
        return True, new_name
    except Exception as e:
        print_error_message(f"An error occurred during renaming: {e}")
        return False, str(e)