# src/cli/termPrompts.py
from pathlib import Path

from src.libs.plugins import PluginManager
from src.libs.messages import (
    print_info_message,
    print_note_message,
    print_command_message,
    print_chat_message,
    print_plugin_message
)


def startup_prompt(memory_dir_path: Path):

    print_info_message("Welcome to AEON.")
    print_info_message("Please choose an option:")

    conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if not conversation_dirs:
        print_note_message("No previous conversations found.")
        print_command_message("[1] Start a new conversation or press <ENTER>.")
        print_note_message("To open a backup file, type: /load <PATH_TO_ZIP>")
        choice = input("\n\033[92m[OPTN]:\033[0m ").strip()
        if not choice:
            return "1"
        return choice

    print_info_message("Existing conversations:")
    for i, conv_dir in enumerate(conversation_dirs):
        print_chat_message(f"[{i + 1}] {conv_dir.name}")

    print_command_message(f"[{len(conversation_dirs) + 1}] New conversation.")
    print_note_message("To rename a conversation, type: /rename <NUMBER> <NEW_NAME>")
    print_note_message("To open a backup file, type: /load <PATH_TO_ZIP>")

    choice = input("\033[92m[OPTN]:\033[0m ").strip()
    if not choice:
        return str(len(conversation_dirs) + 1)
    return choice


def printAeonCmd(plugin_manager: PluginManager):
    """
    Prints a list of available commands and loaded plugins.
    """
    print("Commands to use:")
    print_command_message("'/help' Show this screen.")
    print_command_message("'/new' Create a new chat.")
    print_command_message("'/list' List all chats.")
    print_command_message("'/open <NUMBER>' Open chat.")
    print_command_message("'/load <PATH>/<FILE>.zip' Load ZIP backup.")
    print_command_message("'/rename <NUMBER> <NEW_NAME>' Rename chat by ID.")
    print_command_message("'/delete <NUMBER>' Delete selected chat.")
    print_command_message("'/zip' Backup contents to a timestamped zip file.")
    print_command_message("'/ingest <PATH> | <PATH><.json, .txt, .md, .sqlite3>'"
                          "Add documents to RAG.")
    print_command_message("'/search' <TERM>' Make web search with DuckDuckGo")
    print_command_message("'/restart' Restart AEON")
    print_command_message("'/quit', '/exit' or '/bye'"
                          "to end the chat.")
    print_info_message("PLUGINS:")

    for command, plugin in plugin_manager.plugins.items():
        parameters = plugin.get_parameters() or ""
        desc = plugin.desc or ""
        print_plugin_message(f"'{command} {parameters}' {desc}")
