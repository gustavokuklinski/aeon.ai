import sys
from pathlib import Path

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

from src.libs.messages import print_error_message, print_info_message, print_aeon_message
from src.cli.termPrompts import startup_prompt


def _initialize_session(memory_dir_path: Path):
    """
    Initializes a new or existing conversation session based on user choice.
    """
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
        conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]

        if 1 <= choice_int <= len(conversation_dirs):
            return openConversation(
                str(choice_int),
                memory_dir_path,
                None,
                None,
                None,
                None,
                None)
        elif (choice_int == len(conversation_dirs) + 1 or (not conversation_dirs and choice_int == 1)):
            return newConversation(memory_dir_path)
        else:
            print_error_message("Invalid choice. Exiting.")
            sys.exit()
    except (ValueError, IndexError):
        print_error_message("Invalid input. Please enter a number.")
        sys.exit()


def _handle_ingest(user_input, session_vars):
    """Handles the /ingest command."""
    if not isinstance(user_input, str):
        print_error_message(
            "Invalid input to the ingest handler. Expected a string but received a dictionary."
        )
        return
    
    ingest_path = user_input[len("/ingest "):].strip()
    ingestDocuments(
        ingest_path,
        session_vars["vectorstore"],
        session_vars["text_splitter"],
        session_vars["llama_embeddings"]
    )


def _handle_zip(user_input, session_vars):
    """Handles the /zip command."""
    print_info_message("Zipping memory folder contents...")
    try:
        archive_path = zipBackup(
            session_vars["current_memory_path"], session_vars["output_dir_path"])
        if archive_path:
            print_info_message(f"Conversation successfully zipped to {archive_path}.")
        else:
            print_error_message("Failed to zip conversation folder.")
    except Exception as e:
        print_error_message(f"An error occurred during zipping: {e}")


def _handle_load(user_input, session_vars):
    """Handles the /load command."""
    zip_path = user_input[len("/load "):].strip()
    loadBackup(zip_path, session_vars)


def _handle_search(user_input, session_vars):
    """Handles the /search command."""
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
    """Handles a standard chat message using the RAG system."""
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
    """Handles the /delete command."""
    deleteConversation(user_input, session_vars)


def _handle_rename(user_input, session_vars):
    """Handles the /rename command."""
    renameConversation(user_input, session_vars)


def _handle_restart(user_input, session_vars):
    """Handles the /restart command."""
    print_info_message("Restarting AEON...")
