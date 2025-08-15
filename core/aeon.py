# core/aeon.py
import os
import sys
from pathlib import Path

# Core modules
from core.config import (
    LLM_MODEL, EMBEDDING_MODEL,
    INPUT_DIR, CHROMA_DB_DIR
)
from core.ingestion import ingest_documents
from core.rag_setup import initialize_rag_system

# Langchain modules (used for type hinting in the function call)
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Helper for conditional printing ---
def print_boot_message(message: str):
    print(f"\033[1;93m[BOOT]\033[0m {message}")

def print_info_message(message: str):
    print(f"\033[1;34m[INFO]\033[0m {message}")

# --- RAG Pipeline Setup (Now a single function call) ---
print_boot_message("Initializing RAG system...")
rag_chain, vectorstore, text_splitter, ollama_embeddings = initialize_rag_system()
print_boot_message("Vector store ready.")
print_boot_message("Stateless RAG chain assembled.")

# --- Interactive Chat Loop (Remains the same) ---
print("                                    ")
print("\033[38;5;196m █████╗ ███████╗ ██████╗ ███╗   ██╗ \033[0m")
print("\033[38;5;197m██╔══██╗██╔════╝██╔═══██╗████╗  ██║ \033[0m")
print("\033[38;5;160m███████║█████╗  ██║   ██║██╔██╗ ██║ \033[0m")
print("\033[38;5;124m██╔══██║██╔══╝  ██║   ██║██║╚██╗██║ \033[0m")
print("\033[38;5;88m██║  ██║███████╗╚██████╔╝██║ ╚████║ \033[0m")
print("\033[38;5;52m╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝ \033[0m")

print("\n\033[1;34m[INFO]\033[0m Models loaded:")
print(f"\033[1;34m[INFO]\033[0m     LLM: \033[36m{LLM_MODEL}\033[0m")
print(f"\033[1;34m[INFO]\033[0m     Embeddings: \033[36m{EMBEDDING_MODEL}\033[0m")
print("                                    ")
print("\033[1;32m[CMD]\033[0m Type '/ingest <path_to_file_or_directory>' to add documents to AEON's knowledge base.")
print("\033[1;32m[CMD]\033[0m Type '/quit', '/exit' or '/bye' to end the conversation.")
print("                                    ")
print("\033[1;33m[NOTE]\033[0m AEON will not remember previous conversations.")
print("                                    ")
print("\033[1;31m[START AEON]\033[0m")

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

    try:
        response = rag_chain.invoke(processed_input)
        ai_response_content = response
        print(f"\033[91m[AEON]:\033[0m {ai_response_content}")
    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred during RAG processing: {e}")
        print("\033[91m[ERROR]\033[0m Please try again or check the logs.")
        continue