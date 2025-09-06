import json
import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from src.libs.messages import print_error_message


def _initialize_db(db_path: Path):
    """Initializes the SQLite database and creates the conversation table."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    GUID TEXT PRIMARY KEY,
                    USER TEXT,
                    AEON TEXT,
                    CHAT_ID TEXT,
                    SOURCE TEXT,
                    TIMESTAMP TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print_error_message(f"SQLite database error during initialization: {e}")


def saveConversation(
        user_message: str,
        aeon_message: str,
        aeon_source: str,
        memory_dir: Path,
        filename: str):
    
    json_file_path = memory_dir / filename

    new_turn = {
        "user": user_message,
        "aeon": aeon_message,
        "source": aeon_source
    }

    conversation_data = []

    if json_file_path.exists() and os.path.getsize(json_file_path) > 0:
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)

            if not isinstance(conversation_data, list):
                print_error_message("Invalid conversation file format. Creating a new one.")
                conversation_data = []
        except json.JSONDecodeError:
            print_error_message(
                f"Error decoding JSON from '{filename}'. File may be corrupt."
                " Starting new chat log."
            )
            conversation_data = []

    conversation_data.append(new_turn)

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print_error_message(f"Failed to save chat to '{filename}': {e}")

    db_file_path = memory_dir / f"{Path(filename).stem}.db"
    
    _initialize_db(db_file_path)

    try:
        with sqlite3.connect(db_file_path) as conn:
            cursor = conn.cursor()
            
            guid = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            chat_id = Path(filename).stem
            
            cursor.execute('''
                INSERT INTO conversations (GUID, USER, AEON, CHAT_ID, SOURCE, TIMESTAMP)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (guid, user_message, aeon_message, chat_id, aeon_source, timestamp))
            
            conn.commit()
    except sqlite3.Error as e:
        print_error_message(f"Failed to save chat to SQLite database: {e}")


def loadConversation(memory_dir: Path, filename: str) -> list:
    """Loads conversation data from a JSON file."""
    file_path = memory_dir / filename

    if not file_path.exists() or os.path.getsize(file_path) == 0:
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
        
    except json.JSONDecodeError:
        print_error_message(
            f"Invalid JSON in '{filename}'. History could not be loaded."
        )
        return []
    
    except Exception as e:
        print_error_message(f"Error while loading '{filename}': {e}")
        return []
