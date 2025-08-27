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
        if choice != "1":
            return "1"
        return choice

    print_info_message("Existing conversations:")
    for i, conv_dir in enumerate(conversation_dirs):
        print_chat_message(f"[{i + 1}] {conv_dir.name}")

    print_command_message(f"[{len(conversation_dirs) + 1}] New conversation.")

    choice = input("\033[92m[OPTN]:\033[0m ").strip()
    return choice


def main():
    project_root = Path(__file__).parent.parent
    input_dir_path = project_root / INPUT_DIR
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR
    temp_zip_dir = project_root / BACKUP_DIR

    session_vars = None

    user_choice = startup_prompt(memory_dir_path)

    try:
        choice_int = int(user_choice)
        conversation_dirs = [d for d in memory_dir_path.iterdir(
        ) if d.is_dir() and not d.name.startswith('.')]

        if 1 <= choice_int <= len(conversation_dirs):

            session_vars = openConversation(
                str(choice_int), memory_dir_path, None, None, None, None, None)

        elif (choice_int == len(conversation_dirs) + 1 or
              len(conversation_dirs) == 0 and
              choice_int == 1):
            session_vars = newConversation(memory_dir_path)

        else:
            print_error_message("Invalid choice. Exiting.")
            sys.exit()

    except (ValueError, IndexError):
        print_error_message("Invalid input. Please enter a number.")
        sys.exit()

    if not session_vars:
        print_error_message("Failed to initialize AEON. Exiting.")
        sys.exit()

    # session_vars = newConversation(memory_dir_path)

    rag_chain = session_vars["rag_chain"]
    vectorstore = session_vars["vectorstore"]
    text_splitter = session_vars["text_splitter"]
    llama_embeddings = session_vars["llama_embeddings"]
    llm_instance = session_vars["llm_instance"]
    current_memory_path = session_vars["current_memory_path"]
    conversation_filename = session_vars["conversation_filename"]
    current_chat_history = session_vars["current_chat_history"]
    user_prompt_string = session_vars["user_prompt_string"]

    printAeonLayout()
    printAeonModels()
    print("\033[1;31m[Type /help to show commands]\033[0m")
    print("\033[1;31m[STARTING AEON]\033[0m")

    while True:
        user_input = input(user_prompt_string).strip()

        if user_input.lower() in ["/quit", "/exit", "/bye"]:
            print_aeon_message("Goodbye!")
            break

        if user_input.lower().startswith("/restart"):
            print_boot_message("Restarting AEON...")
            os.execv(sys.executable, ['python'] + sys.argv)

        if not user_input:
            continue

        if user_input.lower().startswith("/help"):
            printAeonCmd()
            continue

        if user_input.lower().startswith("/list"):
            listConversations(memory_dir_path)
            continue

        if user_input.lower().startswith("/open "):
            conv_id = user_input[len("/open "):].strip()
            updated_vars = openConversation(
                conv_id,
                memory_dir_path,
                rag_chain,
                vectorstore,
                text_splitter,
                llama_embeddings,
                llm_instance
            )
            if updated_vars:
                rag_chain = updated_vars["rag_chain"]
                vectorstore = updated_vars["vectorstore"]
                text_splitter = updated_vars["text_splitter"]
                llama_embeddings = updated_vars["llama_embeddings"]
                llm_instance = updated_vars["llm_instance"]
                current_memory_path = updated_vars["current_memory_path"]
                conversation_filename = updated_vars["conversation_filename"]
                current_chat_history = updated_vars["current_chat_history"]
                user_prompt_string = updated_vars["user_prompt_string"]
            continue

        if user_input.lower().startswith("/new"):
            updated_vars = newConversation(memory_dir_path)
            if updated_vars:
                rag_chain = updated_vars["rag_chain"]
                vectorstore = updated_vars["vectorstore"]
                text_splitter = updated_vars["text_splitter"]
                llama_embeddings = updated_vars["llama_embeddings"]
                llm_instance = updated_vars["llm_instance"]
                current_memory_path = updated_vars["current_memory_path"]
                conversation_filename = updated_vars["conversation_filename"]
                current_chat_history = updated_vars["current_chat_history"]
                user_prompt_string = updated_vars["user_prompt_string"]
            continue

        if user_input.lower() == "/paths":
            print_info_message("Displaying AEON's important directory paths:")
            print(
                f"\033[1;36mInput Directory:\033[0m {
                    input_dir_path.resolve()}")
            print(
                f"\033[1;36mOutput Directory:\033[0m {
                    output_dir_path.resolve()}")
            print(
                f"\033[1;36mMemory Directory:\033[0m {
                    memory_dir_path.resolve()}")
            print(
                f"\033[1;36mBackup Directory:\033[0m {
                    temp_zip_dir.resolve()}")
            print_command_message("'/help' show all commands.")
            continue

        if user_input.lower().startswith("/ingest "):
            ingest_path = user_input[len("/ingest "):].strip()
            ingestDocuments(
                ingest_path,
                vectorstore,
                text_splitter,
                llama_embeddings)
            continue

        if user_input.lower().startswith("/image "):
            image_prompt = user_input[len("/image "):].strip()
            print_info_message("Processing image generation request...")
            image_output_path = current_memory_path / "output"
            imgSystem(image_prompt, image_output_path)
            continue

        if user_input.lower() == "/zip":
            print_info_message("Zipping memory folder contents...")
            try:
                archive_path = zipBackup(current_memory_path, OUTPUT_DIR)
                if archive_path:
                    print_info_message(
                        f"Conversation successfully zipped to {archive_path}.")
                else:
                    print_error_message("Failed to zip conversation folder.")
            except Exception as e:
                print_error_message(f"An error occurred during zipping: {e}")
            continue

        if user_input.lower().startswith("/load "):
            conv_id = user_input[len("/load "):].strip()
            loadIngestConversation(
                conv_id,
                memory_dir_path,
                vectorstore,
                text_splitter,
                llama_embeddings
            )
            continue

        if user_input.lower().startswith("/search "):
            search_query = user_input[len("/search "):].strip()
            summarized_search_results = webSearch(
                search_query, llm_instance, text_splitter, vectorstore)
            clean_ai_response = summarized_search_results
            print_aeon_message(f"{clean_ai_response}")

            saveConversation(
                user_input,
                clean_ai_response,
                current_memory_path,
                conversation_filename)
            current_chat_history.append(
                {"user": user_input, "aeon": clean_ai_response})
            continue

        if user_input.lower().startswith("/view "):
            parts = user_input.split(" ", 2)
            if len(parts) < 3:
                print_command_message("Usage: /view <PATH_TO_IMAGE> <PROMPT>")
                continue

            image_path = parts[1]
            view_prompt = parts[2]

            if not os.path.exists(image_path):
                print_note_message(f"Image not found at: {image_path}")
                continue

            print_info_message(
                "Processing image with the Vision Language Model...")

            try:
                vlm_response = vlmSystem(image_path, view_prompt)
                print_info_message(
                    "VLM response received. "
                    "Sending to RAG chain for final processing...")
                final_ai_response = rag_chain.invoke(vlm_response)
                clean_ai_response = str(final_ai_response)

                print_info_message(
                    "Ingesting VLM final response into "
                    "Chroma DB (chunk by chunk)...")
                try:
                    aeon_doc = Document(
                        page_content=clean_ai_response,
                        metadata={
                            "source": "view_response",
                            "query": view_prompt,
                            "image_path": image_path})
                    aeon_chunks = text_splitter.split_documents([aeon_doc])

                    if aeon_chunks:
                        print_info_message(
                            f"Generated {
                                len(aeon_chunks)} chunks for ingestion.")
                        success_count = 0
                        for i, chunk in enumerate(aeon_chunks):
                            try:
                                vectorstore.add_documents([chunk])
                                success_count += 1
                                print_success_message(
                                    "Ingested chunk "
                                    f"{i + 1}/{len(aeon_chunks)} "
                                    "successfully.")
                            except Exception as e_chunk_ingest:
                                print_error_message(
                                    "FAILED to ingest chunk "
                                    f"{i + 1}/{len(aeon_chunks)}:"
                                    f" {e_chunk_ingest}")

                        if success_count > 0:
                            print_success_message(
                                "Completed ingestion. Successfully ingested"
                                f"{success_count}/{len(aeon_chunks)} "
                                "chunks from VLM response into Chroma DB.")
                        else:
                            print_error_message(
                                "No chunks were successfully "
                                "ingested into Chroma DB.")
                    else:
                        print_note_message(
                            "No chunks generated from VLM response. "
                            "Skipping Chroma addition.")
                except Exception as e_ingest:
                    print_error_message(
                        "FAILED TO INGEST Aeon's response into "
                        f"Chroma DB: {e_ingest}")
                    pass

                print_aeon_message(f"{clean_ai_response}")
                saveConversation(
                    user_input,
                    clean_ai_response,
                    current_memory_path,
                    conversation_filename)
                current_chat_history.append(
                    {"user": user_input, "aeon": clean_ai_response})

            except Exception as e:
                print_error_message(
                    f"Failed to process image with VLM or RAG chain: {e}")
            continue

        try:

            response = rag_chain.invoke(user_input)
            ai_response_content = str(response)

            clean_ai_response = ai_response_content

            print_aeon_message(clean_ai_response)

            saveConversation(
                user_input,
                clean_ai_response,
                current_memory_path,
                conversation_filename)

            current_chat_history.append(
                {"user": user_input, "aeon": clean_ai_response})

        except Exception as e:
            print_error_message(
                f"An error occurred during RAG processing: {e}")
            continue


if __name__ == "__main__":
    main()
