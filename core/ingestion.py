# core/ingestion.py
import os
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader, UnstructuredFileLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# Import the custom loader
from core.loaders import JsonPlaintextLoader

def ingest_documents(path_to_ingest: str, vectorstore: Chroma, text_splitter: RecursiveCharacterTextSplitter, embeddings: OllamaEmbeddings):
    """
    Loads documents from a given path (file or directory), splits them,
    generates embeddings, and adds them to the Chroma vector store.
    Handles different file types like .md, .txt, and .json.
    """
    ingested_documents = []
    path = Path(path_to_ingest)

    if not path.exists():
        print(f"\033[91m[ERROR]\033[0m Path not found: '{path_to_ingest}'")
        return

    try:
        if path.is_file():
            print(f"\033[1;34m[INFO]\033[0m Ingesting single file: '{path_to_ingest}'")
            if path.suffix.lower() == ".md":
                loader = UnstructuredMarkdownLoader(str(path))
                ingested_documents.extend(loader.load())
            elif path.suffix.lower() == ".txt":
                print(f"\033[1;34m[INFO]\033[0m Detected .txt file. Loading as plain text.")
                loader = TextLoader(str(path))
                ingested_documents.extend(loader.load())
            elif path.suffix.lower() == ".json":
                print(f"\033[1;34m[INFO]\033[0m Detected .json file. Loading with custom JSON plaintext loader.")
                loader = JsonPlaintextLoader(str(path))
                ingested_documents.extend(loader.load())
            else:
                print(f"\033[1;34m[INFO]\033[0m Attempting to load with UnstructuredFileLoader for unknown type.")
                loader = UnstructuredFileLoader(str(path))
                ingested_documents.extend(loader.load())

        elif path.is_dir():
            print(f"\033[1;34m[INFO]\033[0m Ingesting documents from directory: '{path_to_ingest}'")
            
            # Load Markdown files
            md_loader = DirectoryLoader(str(path), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
            ingested_documents.extend(md_loader.load())

            # Load Text files
            txt_loader = DirectoryLoader(str(path), glob="**/*.txt", loader_cls=TextLoader)
            ingested_documents.extend(txt_loader.load())

            # Load JSON files with custom loader
            json_files = list(path.glob("**/*.json"))
            for json_file in json_files:
                print(f"\033[1;34m[INFO]\033[0m Found JSON file: '{json_file}'. Loading with custom JSON plaintext loader.")
                json_loader = JsonPlaintextLoader(str(json_file))
                ingested_documents.extend(json_loader.load())

            if not (ingested_documents):
                print(f"\033[1;33m[NOTE]\033[0m No .md, .txt, or .json files found in '{path_to_ingest}'.")
        else:
            print(f"\033[91m[ERROR]\033[0m Invalid path type: '{path_to_ingest}'. Please provide a file or a directory.")
            return

        if not ingested_documents:
            print(f"\033[1;33m[NOTE]\033[0m No documents found to ingest at '{path_to_ingest}'.")
            return

        print(f"\033[1;34m[INFO]\033[0m Loaded {len(ingested_documents)} new documents.")
        new_chunks = text_splitter.split_documents(ingested_documents)
        print(f"\033[1;34m[INFO]\033[0m Split into {len(new_chunks)} chunks.")

        print(f"\033[1;34m[INFO]\033[0m Adding new chunks to vector store...")
        vectorstore.add_documents(new_chunks, embedding=embeddings)
        print(f"\033[1;34m[INFO]\033[0m Successfully ingested {len(new_chunks)} chunks from '{path_to_ingest}'. Data is now persistent.")

    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred during ingestion from '{path_to_ingest}': {e}")