# src/utils/conversation.py

import json
import os
from datetime import datetime
from pathlib import Path

from src.utils.messages import *

def saveConversation(user_message: str, aeon_message: str, memory_dir: str, filename: str):
    memory_path = Path(memory_dir)
    memory_path.mkdir(parents=True, exist_ok=True)
    
    file_path = memory_path / filename

    new_turn = {
        "user": user_message,
        "aeon": aeon_message
    }
    conversation_data = []
    
    if file_path.exists() and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)

            if not isinstance(conversation_data, list):
                print_error_message(f"Invalid conversation file format. Creating a new one.")
                conversation_data = []
        except json.JSONDecodeError:
            print_error_message(f"Error decoding JSON from '{filename}'. File may be corrupt. Starting new conversation log.")
            conversation_data = []
    
    conversation_data.append(new_turn)

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=4, ensure_ascii=False)
        
    except Exception as e:
        print_error_message(f"Failed to save conversation to '{filename}': {e}")


def loadConversation(memory_dir: str, filename: str) -> list:
    file_path = Path(memory_dir) / filename
    
    if not file_path.exists() or os.path.getsize(file_path) == 0:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print_error_message(f"Invalid JSON in '{filename}'. History could not be loaded.")
        return []
    except Exception as e:
        print_error_message(f"An error occurred while loading '{filename}': {e}")
        return []
