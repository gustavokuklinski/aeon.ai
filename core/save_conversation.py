# core/save_conversation.py
import json
import os
from datetime import datetime
from pathlib import Path

def save_conversation(user_message: str, aeon_message: str, memory_dir: str, filename: str):
    """
    Saves a single turn of the conversation by appending to a JSON file.
    """
    memory_path = Path(memory_dir)
    memory_path.mkdir(parents=True, exist_ok=True)
    
    file_path = memory_path / filename

    new_turn = {
        "user": user_message,
        "aeon": aeon_message
    }
    conversation_data = []
    
    # Check if the file already exists and has content
    if file_path.exists() and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
            # Ensure the loaded data is a list
            if not isinstance(conversation_data, list):
                print(f"\033[91m[ERROR]\033[0m Invalid conversation file format. Creating a new one.")
                conversation_data = []
        except json.JSONDecodeError:
            print(f"\033[91m[ERROR]\033[0m Error decoding JSON from '{filename}'. File may be corrupt. Starting new conversation log.")
            conversation_data = []
    
    # Append the new turn
    conversation_data.append(new_turn)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=4, ensure_ascii=False)
        
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m Failed to save conversation to '{filename}': {e}")


def load_conversation(memory_dir: str, filename: str) -> list:
    """
    Loads conversation history from a JSON file.
    Returns an empty list if the file is not found or is empty.
    """
    file_path = Path(memory_dir) / filename
    
    if not file_path.exists() or os.path.getsize(file_path) == 0:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"\033[91m[ERROR]\033[0m Invalid JSON in '{filename}'. History could not be loaded.")
        return []
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred while loading '{filename}': {e}")
        return []
