# src/main.py
import os
import sys
from pathlib import Path

from src.config import (
    OUTPUT_DIR,
    MEMORY_DIR,
    LOADED_PLUGINS
) 

from src.utils.ingestion import ingestDocuments
from src.utils.webSearch import webSearch
from src.utils.zipBackup import zipBackup
from src.utils.conversation import saveConversation
from src.utils.list import listConversations
from src.utils.open import openConversation
from src.utils.new import newConversation
from src.utils.load import loadBackup
from src.utils.delete import deleteConversation
from src.utils.rename import renameConversation

from src.libs.plugins import PluginManager
from src.libs.messages import (
    print_info_message,
    print_note_message,
    print_command_message,
    print_error_message,
    print_aeon_message,
    print_chat_message,
    print_plugin_message
)
from src.libs.termLayout import printAeonLayout, printAeonModels

def startup_prompt(memory_dir_path: Path):

    printAeonLayout()
    print_info_message("Welcome to AEON.")
    print_info_message("Please choose an option:")

    conversation_dirs = [d for d in memory_dir_path.iterdir(
    ) if d.is_dir() and not d.name.startswith('.')]

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
    print_note_message(
        "To rename a conversation, type: /rename <NUMBER> <NEW_NAME>")
    # Add a note about loading a backup file
    print_note_message("To open a backup file, type: /load <PATH_TO_ZIP>")

    choice = input("\033[92m[OPTN]:\033[0m ").strip()
    # If user presses ENTER, default to starting a new conversation
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
    print_command_message("'/ingest <PATH> | <PATH><filename.json,txt,md>'"
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

def _initialize_session(memory_dir_path: Path):

    user_choice = startup_prompt(memory_dir_path)
    if user_choice.startswith("/load"):
        zip_path = user_choice[len("/load "):].strip()
        success = loadBackup(zip_path, memory_dir_path)
        if success:
            return _initialize_session(memory_dir_path)
        else:
            print_error_message("Unzipping failed. Please try again.")
            return _initialize_session(memory_dir_path)
        
    try:
        choice_int = int(user_choice)
        conversation_dirs = [d for d in memory_dir_path.iterdir(
        ) if d.is_dir() and not d.name.startswith('.')]

        if 1 <= choice_int <= len(conversation_dirs):
            return openConversation(
                str(choice_int),
                memory_dir_path,
                None,
                None,
                None,
                None,
                None)
        elif (choice_int == len(conversation_dirs) + 1
              or (not conversation_dirs and choice_int == 1)):
            return newConversation(memory_dir_path)
        else:
            print_error_message("Invalid choice. Exiting.")
            sys.exit()
    except (ValueError, IndexError):
        print_error_message("Invalid input. Please enter a number.")
        sys.exit()


def _handle_ingest(user_input, session_vars):

    ingest_path = user_input[len("/ingest "):].strip()
    ingestDocuments(
        ingest_path,
        session_vars["vectorstore"],
        session_vars["text_splitter"],
        session_vars["llama_embeddings"]
    )


def _handle_zip(user_input, session_vars):

    print_info_message("Zipping memory folder contents...")
    try:
        archive_path = zipBackup(
            session_vars["current_memory_path"], OUTPUT_DIR)
        if archive_path:
            print_info_message(
                f"Conversation successfully zipped to {archive_path}.")
        else:
            print_error_message("Failed to zip conversation folder.")
    except Exception as e:
        print_error_message(f"An error occurred during zipping: {e}")


def _handle_load(user_input, session_vars):
    zip_path = user_input[len("/load "):].strip()
    loadBackup(zip_path, session_vars)


def _handle_search(user_input, session_vars):

    search_query = user_input[len("/search "):].strip()
    summarized_search_results = webSearch(
        search_query,
        session_vars["llm_instance"],
        session_vars["text_splitter"],
        session_vars["vectorstore"]
    )
    print_aeon_message(summarized_search_results)
    saveConversation(
        user_input,
        summarized_search_results,
        session_vars["current_memory_path"],
        session_vars["conversation_filename"]
    )
    session_vars["current_chat_history"].append(
        {"user": user_input, "aeon": summarized_search_results})


def _handle_rag_chat(user_input, session_vars):

    try:
        response = session_vars["rag_chain"].invoke(user_input)
        ai_response_content = str(response)
        print_aeon_message(ai_response_content)

        saveConversation(
            user_input,
            ai_response_content,
            session_vars["current_memory_path"],
            session_vars["conversation_filename"])
        session_vars["current_chat_history"].append(
            {"user": user_input, "aeon": ai_response_content})
    except Exception as e:
        print_error_message(f"An error occurred during RAG processing: {e}")


def _handle_delete(user_input, session_vars):
    deleteConversation(user_input, session_vars)
    main()

def _handle_rename(user_input, session_vars):
    renameConversation(user_input, session_vars)
    main()


def _handle_restart(user_input, session_vars):
    print_info_message("Restarting AEON...")
    main()


def main():
    project_root = Path(__file__).parent.parent
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR

    session_vars = _initialize_session(memory_dir_path)
    if not session_vars:
        print_error_message("Failed to initialize AEON. Exiting.")
        sys.exit()

    printAeonLayout()
    printAeonModels()
    if "loaded_config" in session_vars:
        print_info_message(f"Using config from: {session_vars['current_memory_path']}")

    print("\033[1;31m[Type /help to show commands]\033[0m")
    plugins_to_load = session_vars.get("loaded_config", {}).get("load_plugins", LOADED_PLUGINS)
    plugin_manager = PluginManager(plugins_to_load)
    session_vars['plugin_manager'] = plugin_manager 
    print("\033[1;31m[STARTING AEON]\033[0m")

    # Command handlers dictionary
    command_handlers = {
        "/help": lambda *_: printAeonCmd(plugin_manager),
        "/list": lambda *_: listConversations(memory_dir_path),
        "/ingest": _handle_ingest,
        "/zip": _handle_zip,
        "/load": _handle_load,
        "/search": _handle_search,
        "/delete": _handle_delete,
        "/rename": _handle_rename,
        "/restart": _handle_restart,
        "/open": lambda user_input,
        sv: (
            sv.update(
                openConversation(
                    user_input.split(
                        " ",
                        1)[1].strip(),
                    memory_dir_path,
                    sv["rag_chain"],
                    sv["vectorstore"],
                    sv["text_splitter"],
                    sv["llama_embeddings"],
                    sv["llm_instance"])) if len(
                user_input.split(
                    " ",
                    1)) > 1 else None),
        "/new": lambda *_: (
            session_vars.update(
                newConversation(memory_dir_path)))}

    while True:
        user_input = input(session_vars["user_prompt_string"]).strip()
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/bye"]:
            print_aeon_message("Goodbye!")
            break

        # Separate the command from its arguments
        parts = user_input.split(" ", 1)
        command = parts[0].lower()
        query = parts[1] if len(parts) > 1 else ""

        plugin = plugin_manager.load_plugins()
        if plugin:
            # Get the expected parameters from the plugin's config
            param_string = plugin
            if param_string:
                expected_params = param_string.split()
                num_expected = len(expected_params)
                query_parts = query.split(" ", num_expected - 1)

                if len(query_parts) < num_expected:
                    print_error_message(f"Usage: {command} {param_string}")
                    continue

                plugin_manager.execute_command(
                    command, *query_parts, output_dir=output_dir_path)
            else:
                plugin_manager.execute_command(
                    command, query, output_dir=output_dir_path)
            continue

        if command in command_handlers:
            command_handlers[command](user_input, session_vars)
        else:
            _handle_rag_chat(user_input, session_vars)


if __name__ == "__main__":
    main()
