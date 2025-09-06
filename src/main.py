import sys
from pathlib import Path

# Correct the import for the PluginManager class
from src.config import OUTPUT_DIR, MEMORY_DIR, LOADED_PLUGINS
from src.libs.plugins import PluginManager
from src.libs.messages import print_error_message, print_aeon_message, print_info_message
from src.libs.termLayout import printAeonLayout, printAeonModels
from src.cli.termPrompts import printAeonCmd
from src.cli.handlers import (
    _initialize_session,
    _handle_rag_chat,
    _handle_ingest,
    _handle_zip,
    _handle_load,
    _handle_search,
    _handle_delete,
    _handle_rename,
    _handle_restart
)
from src.utils.list import listConversations
from src.utils.open import openConversation
from src.utils.new import newConversation

def main():
    """
    The main entry point for the AEON CLI application.
    """
    project_root = Path(__file__).parent.parent
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR

    session_vars = _initialize_session(memory_dir_path)
    if not session_vars:
        print_error_message("Failed to initialize AEON. Exiting.")
        sys.exit()

    session_vars["output_dir_path"] = output_dir_path
    session_vars["memory_dir_path"] = memory_dir_path
    
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
        "/help": lambda sv: printAeonCmd(sv['plugin_manager']),
        "/list": lambda sv: listConversations(sv["memory_dir_path"]),
        "/ingest": _handle_ingest,
        "/zip": _handle_zip,
        "/load": _handle_load,
        "/search": _handle_search,
        "/delete": _handle_delete,
        "/rename": _handle_rename,
        "/restart": _handle_restart,
        "/open": lambda sv: openConversation(
            sv['user_input'].split(" ", 1)[1].strip(),
            sv["memory_dir_path"],
            sv.get("rag_chain"),
            sv.get("vectorstore"),
            sv.get("text_splitter"),
            sv.get("llama_embeddings"),
            sv.get("llm_instance")
        ),
        "/new": lambda sv: newConversation(sv["memory_dir_path"]),
    }

    while True:
        user_input = input(session_vars["user_prompt_string"]).strip()
        session_vars['user_input'] = user_input  # Store for handlers
        
        if not user_input:
            continue
        if user_input.lower() in ["/quit", "/exit", "/bye"]:
            print_aeon_message("Goodbye!")
            break

        # This section has been corrected to properly parse commands.
        parts = user_input.split(" ", 1)
        command = parts[0].lower()
        query = parts[1] if len(parts) > 1 else ""

        # Check if the command is a plugin
        if command in plugin_manager.plugins:
            plugin = plugin_manager.plugins.get(command)

            plugin.execute(
                query,
                output_dir=output_dir_path,
                vectorstore=session_vars.get("vectorstore"),
                text_splitter=session_vars.get("text_splitter"),
                embeddings=session_vars.get("llama_embeddings")
            )
            continue
        
        # Handle core commands
        if command in command_handlers:
            handler = command_handlers[command]
            
            # Handle restart and new conversation separately
            if command in ["/restart", "/new", "/open"]:
                new_session_vars = handler(session_vars)
                if new_session_vars:
                    session_vars.update(new_session_vars)
            elif command in ["/help", "/list"]:
                handler(session_vars)
            else:
                handler(user_input, session_vars)
        else:
            _handle_rag_chat(user_input, session_vars)

if __name__ == "__main__":
    main()