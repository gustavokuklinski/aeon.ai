# core/aeon.py
import os
import shutil
from pathlib import Path
import json
import base64
import requests
import io
import uuid
import sys

# Core modules
from core.config import (
    LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL,
    MARKDOWN_DATA_DIR, CHROMA_DB_DIR,
    OUTPUT_DIR,
    SYSTEM_PROMPT
)
from core.ingestion import ingest_documents # Note: ingest_documents itself might print
from core.loaders import JsonPlaintextLoader

# Langchain modules
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader, UnstructuredFileLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.documents import Document

# --- Helper for conditional printing ---
def print_boot_message(message: str):
    print(f"\033[1;93m[BOOT]\033[0m {message}")

def print_info_message(message: str):
    print(f"\033[1;34m[INFO]\033[0m {message}")

# --- RAG Pipeline Setup ---

# 1. Load Initial Documents from MARKDOWN_DATA_DIR (now supports all types)
if not os.path.exists(MARKDOWN_DATA_DIR):
    print(f"\033[91m[ERROR]\033[0m Directory '{MARKDOWN_DATA_DIR}' not found. Please create it and place your Markdown, JSON, or TXT files inside.")
    sys.exit(1)

print_boot_message(f"Loading initial documents from: {MARKDOWN_DATA_DIR} (Markdown, JSON, TXT)")

documents = [] # Initialize an empty list to collect all documents

# Load Markdown files
md_loader = DirectoryLoader(str(Path(MARKDOWN_DATA_DIR)), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
documents.extend(md_loader.load())

# Load Text files
txt_loader = DirectoryLoader(str(Path(MARKDOWN_DATA_DIR)), glob="**/*.txt", loader_cls=TextLoader)
documents.extend(txt_loader.load())

# Load JSON files with custom loader
json_files = list(Path(MARKDOWN_DATA_DIR).glob("**/*.json"))
for json_file in json_files:
    json_loader = JsonPlaintextLoader(str(json_file)) # hide_messages is now effectively False
    print_info_message(f"Found JSON file during initial boot: '{json_file}'. Loading with custom JSON plaintext loader.")
    documents.extend(json_loader.load())

print_boot_message(f"Loaded {len(documents)} initial documents.")

# 2. Split Documents into Chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)
chunks = text_splitter.split_documents(documents)
print_boot_message(f"Split into {len(chunks)} chunks.")

# 3. Generate Embeddings and Store in a Vector Database
ollama_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

if not Path(CHROMA_DB_DIR).exists() or not os.listdir(CHROMA_DB_DIR):
    print_boot_message(f"Vector store not found at {CHROMA_DB_DIR}. Creating new one...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=ollama_embeddings,
        persist_directory=CHROMA_DB_DIR
    )
else:
    print_boot_message(f"Loading existing vector store from {CHROMA_DB_DIR}...")
    vectorstore = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=ollama_embeddings
    )
print_boot_message("Vector store ready.")

retriever = vectorstore.as_retriever()

# --- 4. Set up the LLM and Prompt Templates ---
llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)

qa_system_prompt = SYSTEM_PROMPT

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        ("human", "{input}"),
        
    ]
)

# --- 5. Assemble the Stateless RAG Chain ---
document_combiner = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = (
    {"context": retriever, "input": RunnablePassthrough()}
    | document_combiner
)

print_boot_message("Stateless RAG chain assembled.")

# --- Interactive Chat Loop ---
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