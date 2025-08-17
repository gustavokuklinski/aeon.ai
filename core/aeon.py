# core/aeon.py
import os
import sys
from pathlib import Path
from core.config import (
    LLM_MODEL, EMBEDDING_MODEL,
    INPUT_DIR, OUTPUT_DIR, CHROMA_DB_DIR, VLM_MODEL

)
from core.ingestion import ingest_documents
from core.rag_setup import initialize_rag_system
from langchain_chroma import Chroma

from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.image_gen import generate_image_from_prompt

# Helper for conditional printing ---
def print_boot_message(message: str):
    print(f"\033[1;93m[BOOT]\033[0m {message}")

def print_info_message(message: str):
    print(f"\033[1;34m[INFO]\033[0m {message}")

# RAG Pipeline Setup (Now a single function call) ---
print_boot_message("Initializing RAG system...")
rag_chain, vectorstore, text_splitter, ollama_embeddings = initialize_rag_system()
print_boot_message("Vector store ready.")
print_boot_message("Stateless RAG chain assembled.")

# Interactive Chat Loop (Remains the same) ---
print("                                    ")
print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")

print("\n\033[1;34m[INFO]\033[0m Models loaded:")
print(f"\033[1;34m[INFO]\033[0m     LLM: \033[36m{LLM_MODEL}\033[0m")
print(f"\033[1;34m[INFO]\033[0m     IMG: \033[36m{VLM_MODEL}\033[0m")
print(f"\033[1;34m[INFO]\033[0m     Embeddings: \033[36m{EMBEDDING_MODEL}\033[0m")
print("                                    ")
print("\033[1;32m[CMD]\033[0m Type '/image <image_prompt>' to generate image.")
print("\033[1;32m[CMD]\033[0m Type '/ingest <path_to_file_or_directory>' to add documents to AEON's knowledge base.")
print("\033[1;32m[CMD]\033[0m Type '/quit', '/exit' or '/bye' to end the conversation.")
print("                                    ")
print("\033[1;33m[NOTE]\033[0m AEON will not remember previous conversations.")
print("                                    ")
print("\033[1;31m[STARTING AEON]\033[0m")

while True:
    user_input = input("\n\033[92m[>>>>]:\033[0m ").strip()

    if user_input.lower() in ["/quit", "/exit", "/bye"]:
        print("\033[92m[AEON]:\033[0m Goodbye!")
        break

    if not user_input:
        continue

    processed_input = user_input
    
    # Ingest command in interactive mode
    if user_input.lower().startswith("/ingest "):
        ingest_path = user_input[len("/ingest "):].strip()
        ingest_documents(ingest_path, vectorstore, text_splitter, ollama_embeddings)
        continue

    if user_input.lower().startswith("/image "):
        image_prompt = user_input[len("/image "):].strip()
        print("\033[1;34m[INFO]\033[0m Processing image generation request...")
        generate_image_from_prompt(image_prompt, OUTPUT_DIR)
        continue

    try:
        response = rag_chain.invoke(processed_input)

        if isinstance(response, list) and response:
            ai_response_content = response[0].get("generated_text", "")
        else:
            ai_response_content = str(response)

        # --- REVISED CODE TO CLEAN UP THE RESPONSE ---
        clean_response = ai_response_content.replace("<|im_start|>system", "").replace("<|im_end|>", "").replace("<|im_start|>user", "").replace("<|im_start|>assistant", "").strip()
        
        # Remove any leading newlines or spaces that remain
        clean_response = clean_response.lstrip('\n ').strip()
        # Clean up any leftover blank lines in the response
        clean_response = '\n'.join([line for line in clean_response.split('\n') if line.strip()])
        # --- END OF REVISED CLEAN UP CODE ---

        print(f"\033[91m[AEON]:\033[0m {clean_response}")
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred during RAG processing: {e}")
        print("\033[91m[ERROR]\033[0m Please try again or check the logs.")
        continue