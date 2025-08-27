# src/main.py
import os
import sys
from pathlib import Path
from langchain_core.documents import Document

from src.config import (
    INPUT_DIR,
    OUTPUT_DIR,
    BACKUP_DIR,
    MEMORY_DIR
)

from src.core.imgSystem import imgSystem
from src.core.vlmSystem import vlmSystem

from src.utils.ingestion import ingestDocuments
from src.utils.webSearch import webSearch
from src.utils.zipBackup import zipBackup
from src.utils.conversation import saveConversation
from src.utils.list import listConversations
from src.utils.open import openConversation
from src.utils.new import newConversation
from src.utils.load import loadIngestConversation

from src.libs.messages import (
    print_info_message,
    print_note_message,
    print_command_message,
    print_error_message,
    print_aeon_message,
    print_boot_message,
    print_chat_message,
    print_success_message
)
from src.libs.termLayout import printAeonLayout, printAeonCmd, printAeonModels

os.environ["LLAMA_LOG_LEVEL"] = "0"


def startup_prompt(memory_dir_path: Path):

    printAeonLayout()
    print_info_message("Welcome to AEON.")
    print_info_message("Please choose an option:")

    conversation_dirs = [d for d in memory_dir_path.iterdir(
    ) if d.is_dir() and not d.name.startswith('.')]

    if not conversation_dirs:
        print_note_message("No previous conversations found.")
        print_command_message("[1] Start a new conversation.")
        choice = input("\n\033[92m[OPTN]:\033[0m ").strip()
        return choice if choice != "1" else "1"

    print_info_message("Existing conversations:")
    for i, conv_dir in enumerate(conversation_dirs):
        print_chat_message(f"[{i + 1}] {conv_dir.name}")

    print_command_message(f"[{len(conversation_dirs) + 1}] New conversation.")
    return input("\033[92m[OPTN]:\033[0m ").strip()


def _initialize_session(memory_dir_path: Path):

    user_choice = startup_prompt(memory_dir_path)
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


def _handle_image(user_input, session_vars):

    image_prompt = user_input[len("/image "):].strip()
    print_info_message("Processing image generation request...")
    image_output_path = session_vars["current_memory_path"] / "output"
    imgSystem(image_prompt, image_output_path)


def _handle_zip(session_vars):

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

    conv_id = user_input[len("/load "):].strip()
    loadIngestConversation(
        conv_id,
        session_vars["memory_dir_path"],
        session_vars["vectorstore"],
        session_vars["text_splitter"],
        session_vars["llama_embeddings"]
    )


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


def _handle_view(user_input, session_vars):

    parts = user_input.split(" ", 2)
    if len(parts) < 3:
        print_command_message("Usage: /view <PATH_TO_IMAGE> <PROMPT>")
        return

    image_path, view_prompt = parts[1], parts[2]
    if not os.path.exists(image_path):
        print_note_message(f"Image not found at: {image_path}")
        return

    print_info_message("Processing image with the Vision Language Model...")
    try:
        vlm_response = vlmSystem(image_path, view_prompt)
        final_ai_response = session_vars["rag_chain"].invoke(vlm_response)
        clean_ai_response = str(final_ai_response)
        print_aeon_message(clean_ai_response)

        # Ingest the VLM response into Chroma DB
        aeon_doc = Document(
            page_content=clean_ai_response,
            metadata={
                "source": "view_response",
                "query": view_prompt,
                "image_path": image_path})
        aeon_chunks = session_vars["text_splitter"].split_documents([aeon_doc])
        if aeon_chunks:
            session_vars["vectorstore"].add_documents(aeon_chunks)
            print_success_message(
                f"Ingested {
                    len(aeon_chunks)} chunks from VLM response.")
        else:
            print_note_message("No chunks generated from VLM response.")

        saveConversation(
            user_input,
            clean_ai_response,
            session_vars["current_memory_path"],
            session_vars["conversation_filename"])
        session_vars["current_chat_history"].append(
            {"user": user_input, "aeon": clean_ai_response})

    except Exception as e:
        print_error_message(
            f"Failed to process image with VLM or RAG chain: {e}")


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


def main():
    project_root = Path(__file__).parent.parent
    input_dir_path = project_root / INPUT_DIR
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR
    temp_zip_dir = project_root / BACKUP_DIR

    session_vars = _initialize_session(memory_dir_path)
    if not session_vars:
        print_error_message("Failed to initialize AEON. Exiting.")
        sys.exit()

    printAeonLayout()
    printAeonModels()
    print("\033[1;31m[Type /help to show commands]\033[0m")
    print("\033[1;31m[STARTING AEON]\033[0m")

    # Command handlers dictionary
    command_handlers = {
        "/help": lambda *_: printAeonCmd(),
        "/list": lambda *_: listConversations(memory_dir_path),
        "/paths": lambda *_: (
            print_info_message("Displaying AEON's important directory paths:"),
            print(
                f"\033[1;36mInput Directory:\033[0m {
                    input_dir_path.resolve()}"),
            print(
                f"\033[1;36mOutput Directory:\033[0m {
                    output_dir_path.resolve()}"),
            print(
                f"\033[1;36mMemory Directory:\033[0m {
                    memory_dir_path.resolve()}"),
            print(
                f"\033[1;36mBackup Directory:\033[0m {
                    temp_zip_dir.resolve()}"),
            print_command_message("'/help' show all commands.")),
        "/ingest": _handle_ingest,
        "/image": _handle_image,
        "/zip": _handle_zip,
        "/load": _handle_load,
        "/search": _handle_search,
        "/view": _handle_view,
        "/restart": lambda *_: (
            print_boot_message("Restarting AEON..."),
            os.execv(
                sys.executable,
                ['python'] + sys.argv)),
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

        command = user_input.lower().split(" ")[0]
        if command in command_handlers:
            if command in [
                "/open",
                "/ingest",
                "/image",
                "/load",
                "/search",
                    "/view"]:
                command_handlers[command](user_input, session_vars)
            elif command in ["/zip", "/new", "/help",
                             "/list", "/paths", "/restart"]:
                command_handlers[command](session_vars)
            else:
                command_handlers[command]()
        else:
            _handle_rag_chat(user_input, session_vars)


if __name__ == "__main__":
    main()
