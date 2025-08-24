# src/aeon.py
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import re
import shutil
from ddgs import DDGS
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import (
    LLM_MODEL, 
    EMBEDDING_MODEL,
    INPUT_DIR, 
    OUTPUT_DIR, 
    CHROMA_DB_DIR, 
    IMG_MODEL,
    MEMORY_DIR, 
    VLM_MODEL
)

from src.core.ragSystem import ragSystem, ragPersist
from src.core.imageGenerator import imageGenerator
from src.core.vlmSystem import vlmSystem
from src.core.webSearch import webSearch

from src.utils.ingestion import ingestDocuments, ingestConversationHistory
from src.utils.conversation import saveConversation, loadConversation
from src.utils.zipBackup import zipBackup

from src.utils.messages import *



def printHelpLayout():
    print("                                    ")
    print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
    print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
    print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
    print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
    print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
    print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")
    print_info_message(f"Models loaded:\nLLM: \033[36m{LLM_MODEL}\033[0m\nIMG: \033[36m{IMG_MODEL}\033[0m\nVLM: \033[36m{VLM_MODEL}\033[0m\nEMB: \033[36m{EMBEDDING_MODEL}\033[0m")
    print("Commands to use:")
    print_command_message("'/help' show this screen.")
    print_command_message("'/paths' display Aeon directory paths")
    print_command_message("'/search <TERMS>' make web search with DuckDuckGo")
    print_command_message("'/load <PATH><filename.json>' to load previous conversation.")
    print_command_message("'/ingest <PATH> | <PATH><filename.json,txt,md>' to add documents to RAG.")
    print_command_message("'/image <PROMPT>' to generate image.")
    print_command_message("'/view <PATH><filename.png, jpg> <PROMPT>' to visualize image.")
    print_command_message("'/zip' backup contents to a timestamped zip file.")
    print_command_message("'/restart' to restart")
    print_command_message("'/quit', '/exit' or '/bye' to end the conversation.")

def main():
    project_root = Path(__file__).parent.parent
    input_dir_path = project_root / INPUT_DIR
    output_dir_path = project_root / OUTPUT_DIR
    memory_dir_path = project_root / MEMORY_DIR
    temp_zip_dir = output_dir_path / "backup"

    print_boot_message("Initializing RAG system...")
    rag_chain, vectorstore, text_splitter, llama_embeddings, llm_instance = ragSystem()
    print_boot_message("Vector store ready.")
    print_boot_message("Stateless RAG chain assembled.")

    conversation_filename = f"conversation_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    current_conversation_history = []

    printHelpLayout()

    print("\033[1;31m[STARTING AEON]\033[0m")

    while True:
        user_input = input("\n\033[92m[>>>>]:\033[0m ").strip()

        if user_input.lower() in ["/quit", "/exit", "/bye"]:
            print_aeon_message("Goodbye!")
            break

        if user_input.lower().startswith("/restart"):
            print_boot_message("Restarting AEON...")
            os.execv(sys.executable, ['python'] + sys.argv)

        if not user_input:
            continue

        if user_input.lower().startswith("/help"):
            printHelpLayout()
            continue
        
        if user_input.lower() == "/paths":
            print_info_message("Displaying AEON's important directory paths:")
            print(f"\033[1;36mInput Directory:\033[0m {input_dir_path.resolve()}")
            print(f"\033[1;36mOutput Directory:\033[0m {output_dir_path.resolve()}")
            print(f"\033[1;36mMemory Directory:\033[0m {memory_dir_path.resolve()}")
            print(f"\033[1;36mBackup Directory:\033[0m {temp_zip_dir.resolve()}")
            print_command_message("'/help' show all commands.")
            continue

        if user_input.lower().startswith("/ingest "):
            ingest_path = user_input[len("/ingest "):].strip()
            ingestDocuments(ingest_path, vectorstore, text_splitter, llama_embeddings)
            continue

        if user_input.lower().startswith("/image "):
            image_prompt = user_input[len("/image "):].strip()
            print_info_message("Processing image generation request...")
            imageGenerator(image_prompt, OUTPUT_DIR)
            continue


        if user_input.lower() == "/zip":
            print_info_message("Zipping memory folder contents...")
            
            try:
                archive_path = zipBackup(MEMORY_DIR, OUTPUT_DIR)
                if archive_path:
                    print_info_message(f"Memory folder successfully zipped.")
                else:
                    print_error_message(f"Failed to zip memory folder.")

            except Exception as e:
                print_error_message(f"An error occurred during zipping: {e}")
            continue

        if user_input.lower().startswith("/load "):
            load_filename = user_input[len("/load "):].strip()
            loaded_history = loadConversation(MEMORY_DIR, load_filename)

            if loaded_history:
                current_conversation_history = loaded_history
                conversation_filename = load_filename

                file_prefix = os.path.splitext(load_filename)[0]
                user_prompt_string = f"\n\033[92m[{file_prefix}@>>>>]:\033[0m "

                print_info_message(f"Successfully loaded conversation from '{load_filename}'.")

                file_path_to_ingest = os.path.join(MEMORY_DIR, load_filename)
                print_info_message(f"Ingesting loaded conversation history from '{file_path_to_ingest}' into AEON's knowledge base...")
                ingestDocuments(file_path_to_ingest, vectorstore, text_splitter, llama_embeddings)

                print_info_message("Conversation history ingestion complete. It is now part of the RAG system.")
                print_info_message("Conversation loaded.")

            else:
                print_error_message(f"Could not load conversation from '{load_filename}'. No history loaded.")
                current_conversation_history = []
            continue       

        if user_input.lower().startswith("/search "):
            search_query = user_input[len("/search "):].strip()
            summarized_search_results = webSearch(search_query, llm_instance, text_splitter, vectorstore) 
            clean_ai_response = summarized_search_results           
            print_aeon_message(f"{clean_ai_response}")
            
            saveConversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
            current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})
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
            
            print_info_message("Processing image with the Vision Language Model...")
        
            try:
                vlm_response = vlmSystem(image_path, view_prompt)

                print_info_message("VLM response received. Sending to RAG chain for final processing...")
                
                final_ai_response = rag_chain.invoke(vlm_response)
                clean_ai_response = str(final_ai_response)
                
                print_aeon_message(f"{clean_ai_response}")

                saveConversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
                current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})
                
            except Exception as e:
                print_error_message(f"Failed to process image with VLM or RAG chain: {e}")
            continue

        try:
            
            response = rag_chain.invoke(user_input)
            ai_response_content = str(response)
            
            clean_ai_response = ai_response_content 

            print_aeon_message(clean_ai_response)

            ragPersist(vectorstore, llama_embeddings, user_input, clean_ai_response)

            saveConversation(user_input, clean_ai_response, MEMORY_DIR, conversation_filename)
            
            current_conversation_history.append({"user": user_input, "aeon": clean_ai_response})

        except Exception as e:
            print_error_message(f"An error occurred during RAG processing: {e}")
            continue

if __name__ == "__main__":
    main()