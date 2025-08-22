# core/aeon.py
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import re  # Added for more flexible string cleanup
import shutil # New: Added for zipping files
from duckduckgo_search import DDGS

from core.config import (
    LLM_MODEL, EMBEDDING_MODEL,
    INPUT_DIR, OUTPUT_DIR, CHROMA_DB_DIR, IMG_MODEL,
    MEMORY_DIR, VLM_MODEL
)
from core.ingestion import ingest_documents, ingest_conversation_history
from core.rag_setup import initialize_rag_system
from core.save_conversation import save_conversation, load_conversation
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.image_gen import generate_image_from_prompt
from core.vlm_engine import process_image_with_vlm

# Helper for conditional printing
def print_boot_message(message: str):
    print(f"\033[1;93m[BOOT]\033[0m {message}")

def print_info_message(message: str):
    print(f"\033[1;34m[INFO]\033[0m {message}")

def print_command_message(message: str):
    print(f"\033[1;32m[CMD]\033[0m {message}")

def print_note_message(message: str):
    print(f"\033[1;33m[NOTE]\033[0m {message}")

# --- AI Response Cleanup Function ---
def clean_response(response: str) -> str:
    """Removes model-specific tokens and extraneous whitespace from the AI's response."""
    # This regex removes tokens like <|im_start|> and any content inside them.
    cleaned = re.sub(r'<\|im_start\|>.*?<\|im_end\|>', '', response, flags=re.DOTALL)
    cleaned = cleaned.replace("Question:", "").replace("Answer:", "").strip()
    # Remove any leading newlines or spaces that remain
    cleaned = cleaned.lstrip('\n ').strip()
    # Clean up any leftover blank lines in the response
    cleaned = '\n'.join([line for line in cleaned.split('\n') if line.strip()])
    return cleaned

def helpLayout():
    print("                                    ")
    print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
    print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
    print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
    print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
    print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
    print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")
    print("\n")
    print_info_message(f"Models loaded:\n    LLM: \033[36m{LLM_MODEL}\033[0m\n    IMG: \033[36m{IMG_MODEL}\033[0m\n    VLM: \033[36m{VLM_MODEL}\033[0m\n    EMB: \033[36m{EMBEDDING_MODEL}\033[0m")
    print("                                    ")
    print("Commands to use:")
    print_command_message("'/help' show this screen.")
    print_command_message("'/paths' display Aeon directory paths")
    print_command_message("'/search <TERMS>' make web search with DuckDuckGo")
    print("                                    ")
    print_command_message("'/load <PATH>/<filename.json>' to load previous conversation.")
    print_command_message("'/ingest <PATH>/ | <PATH>/<filename.json,txt,md>' to add documents to RAG.")
    print_command_message("'/image <PROMPT>' to generate image.")
    print_command_message("'/view <PATH>/<filename.png, jpg> <PROMPT>' to visualize image.")
    print("                                    ")
    print_command_message("'/zip' to backup contents to a timestamped zip file.")
    print_command_message("'/restart' to reload AEON.")
    print_command_message("'/quit', '/exit' or '/bye' to end the conversation.")
    print("                                    ")

# --- Main Execution Block ---
def main():
    project_root = Path(__file__).parent.parent
    input_dir_path = project_root / INPUT_DIR
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR
    temp_zip_dir = output_dir_path / "backup" # Path for zipped memories

    # RAG Pipeline Setup
    print_boot_message("Initializing RAG system...")
    rag_chain, vectorstore, text_splitter, llama_embeddings = initialize_rag_system()
    print_boot_message("Vector store ready.")
    print_boot_message("Stateless RAG chain assembled.")

    # Prepare conversation file
    conversation_filename = f"conversation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    current_conversation_history = []
    # Define the temporary output directory for zipping

    project_root = Path(__file__).parent.parent
    temp_zip_dir = project_root / OUTPUT_DIR / "backup"

    # Print welcome and command information
    
    helpLayout()

    print("\033[1;31m[STARTING AEON]\033[0m")

    # Interactive Chat Loop
    while True:
        user_input = input("\n\033[92m[>>>>]:\033[0m ").strip()

        if user_input.lower() in ["/quit", "/exit", "/bye"]:
            print("\033[92m[AEON]:\033[0m Goodbye!")
            break

        if user_input.lower().startswith("/restart"):
            print_boot_message("Restarting AEON...")
            # This replaces the current process with a new one, effectively restarting the script
            os.execv(sys.executable, ['python'] + sys.argv)

        if not user_input:
            continue

        if user_input.lower().startswith("/help"):
            helpLayout()
            continue

        if user_input.lower().startswith("/ingest "):
            ingest_path = user_input[len("/ingest "):].strip()
            ingest_documents(ingest_path, vectorstore, text_splitter, llama_embeddings)
            continue

        if user_input.lower() == "/zip":
            print_info_message("Zipping memory folder contents...")
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            zip_filename_base = f"memory_{timestamp}"
            
            # Ensure the temporary zip directory exists
            temp_zip_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # shutil.make_archive(base_name, format, root_dir)
                # base_name: The name of the archive file to create, including path (without extension)
                # format: 'zip' for zip archive
                # root_dir: The directory to start archiving from (MEMORY_DIR)
                # The archive will be created as temp_zip_dir/memory_<TIMESTAMP>.zip
                archive_path = shutil.make_archive(
                    base_name=str(temp_zip_dir / zip_filename_base),
                    format='zip',
                    root_dir=str(project_root / MEMORY_DIR)
                )
                print_info_message(f"Memory folder successfully zipped to: {archive_path}")
            except Exception as e:
                print(f"\033[91m[ERROR]\033[0m Failed to zip memory folder: {e}")
            continue

        if user_input.lower().startswith("/image "):
            image_prompt = user_input[len("/image "):].strip()
            print_info_message("Processing image generation request...")
            generate_image_from_prompt(image_prompt, OUTPUT_DIR)

            continue

        if user_input.lower().startswith("/load "):
            load_filename = user_input[len("/load "):].strip()
            loaded_history = load_conversation(MEMORY_DIR, load_filename)

            if loaded_history:
                current_conversation_history = loaded_history

                # --- THIS IS THE KEY CHANGE ---
                conversation_filename = load_filename
                
                # Update the user prompt string to reflect the loaded chat
                file_prefix = os.path.splitext(load_filename)[0]
                user_prompt_string = f"\n\033[92m[{file_prefix}@>>>>]:\033[0m "
                # ------------------------------

                print_info_message(f"Successfully loaded conversation from '{load_filename}'.")

                # Auto-ingest the loaded conversation file
                file_path_to_ingest = os.path.join(MEMORY_DIR, load_filename)
                print_info_message(f"Ingesting loaded conversation history from '{file_path_to_ingest}' into AEON's knowledge base...")
                ingest_documents(file_path_to_ingest, vectorstore, text_splitter, llama_embeddings)
                print_info_message("Conversation history ingestion complete. It is now part of the RAG system.")

                
                print("\n\033[1;34m[INFO]\033[0m Conversation loaded.")

            else:
                print_info_message(f"Could not load conversation from '{load_filename}'. No history loaded.")
                current_conversation_history = []
            continue

        if user_input.lower() == "/paths":
            print_info_message("Displaying AEON's important directory paths:")
            print(f"\033[1;36mInput Directory:\033[0m {input_dir_path.resolve()}")
            print(f"\033[1;36mOutput Directory:\033[0m {output_dir_path.resolve()}")
            print(f"\033[1;36mMemory Directory:\033[0m {memory_dir_path.resolve()}")
            print(f"\033[1;36mBackup Directory:\033[0m {temp_zip_dir.resolve()}")
            print_command_message("'/help' show all commands.")
            continue

        if user_input.lower().startswith("/search "):
            search_query = user_input[len("/search "):].strip()
            print_info_message(f"Searching DuckDuckGo for: '{search_query}'...")
            try:
                # Perform the web search using DuckDuckGo
                # DDGS().text() returns a list of dictionaries with keys like 'title', 'href', 'body'
                search_results = DDGS().text(keywords=search_query, max_results=5) # Fetch a few more to pick the best 3

                # Format results for the LLM
                search_context = ""
                if search_results:
                    for i, result in enumerate(search_results):
                        if i >= 3: # Limit to top 3 results to keep context concise
                            break
                        search_context += f"Source: {result.get('title', 'N/A')}\nURL: {result.get('href', 'N/A')}\nSnippet: {result.get('body', 'N/A')}\n\n"
                    print_info_message("DuckDuckGo search results obtained. Incorporating into RAG chain...")

                    # Augment the RAG prompt with search results
                    augmented_prompt = (
                        f"<start_of_turn>user\n"
                        f"You are AEON, a helpful AI assistant.\n"
                        f"Web Search Results (from DuckDuckGo):\n"
                        f"{search_context}\n\n"
                        f"Question: {search_query}<end_of_turn>\n"
                        f"<start_of_turn>model\n"
                    )
                
                
                response = rag_chain.invoke(augmented_prompt)
                ai_response_content = str(response)
                clean_ai_response = clean_response(ai_response_content)
                
                print(f"\033[91m[AEON]:\033[0m {clean_ai_response}")
                save_conversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
                current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})

            except Exception as e:
                print(f"\033[91m[ERROR]\033[0m Failed to perform DuckDuckGo web search or process results: {e}")
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
            
            # Assuming you have a variable for the mmproj model path
            # You should add this to your core/config.py
            mmproj_path = VLM_MODEL

            print_info_message("Processing image with the Vision Language Model...")
        
            try:
                # 1. Get the VLM's description of the image.
                vlm_response = process_image_with_vlm(IMG_MODEL, mmproj_path, image_path, view_prompt)

                print_info_message("VLM response received. Sending to RAG chain for final processing...")
                
                # 2. Use the VLM's output as the new input for the RAG chain.
                #    The RAG chain will retrieve context and generate a coherent response.
                final_ai_response = rag_chain.invoke(vlm_response)
                
                # 3. Clean up the final response.
                clean_ai_response = clean_response(str(final_ai_response))
                
                print(f"\033[91m[AEON]:\033[0m {clean_ai_response}")

                # 4. Save the entire exchange to the conversation file.
                save_conversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
                current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})
                
            except Exception as e:
                print(f"\033[91m[ERROR]\033[0m Failed to process image with VLM or RAG chain: {e}")
            continue
        try:
            # We no longer manually build the conversation history string.
            # The RAG system will now retrieve relevant context from the vector store.
            template = (
                "<start_of_turn>user\n"
                "Question: {user_input}<end_of_turn>\n"
                "<start_of_turn>model\n"
            )
            # Combine the template with the current user input
            full_prompt = template.format(user_input=user_input).strip()

            # The RAG chain will automatically handle retrieving relevant documents
            # (including conversation history from the vector store) and providing them as context to the LLM.
            response = rag_chain.invoke(full_prompt)

            ai_response_content = str(response)
            clean_ai_response = clean_response(ai_response_content)

            print(f"\033[91m[AEON]:\033[0m {clean_ai_response}")

            # Save and update conversation history
            save_conversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
            current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})
            # This line is crucial for displaying the history upon a '/load' command.
            # It's important to keep it for the display logic.

        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m An error occurred during RAG processing: {e}")
            print("\033[91m[ERROR]\033[0m Please try again or check the logs.")
            continue

if __name__ == "__main__":
    main()