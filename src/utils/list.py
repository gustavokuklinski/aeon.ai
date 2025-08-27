# src/utils/list.py
from pathlib import Path
from src.libs.messages import print_info_message, print_note_message


def listConversations(memory_dir_path: Path):

    print_info_message("Available conversations:")
    conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir()
                         and not d.name.startswith('.')]
    if not conversation_dirs:
        print_note_message("No conversations found.")
    else:
        for i, conv_dir in enumerate(conversation_dirs):
            print_info_message(f"[{i+1}] {conv_dir.name}")

    print_info_message("To open conversation type: /open <NUMBER>")
