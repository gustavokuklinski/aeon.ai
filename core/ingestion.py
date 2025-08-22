# core/ingestion.py
import os
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, UnstructuredMarkdownLoader, UnstructuredFileLoader, TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import LlamaCppEmbeddings

# Import the custom loader
from core.loaders import JsonPlaintextLoader


def ingest_documents(path_to_ingest: str, vectorstore: Chroma,
                     text_splitter: RecursiveCharacterTextSplitter,
                     embeddings: LlamaCppEmbeddings,
                     batch_size: int = 32):
    """
    Loads documents from a given path (file or directory), splits them,
    generates embeddings in safe batches, and adds them to the Chroma vector store.
    Handles .md, .txt, .json files.
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

            md_loader = DirectoryLoader(str(path), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
            ingested_documents.extend(md_loader.load())

            txt_loader = DirectoryLoader(str(path), glob="**/*.txt", loader_cls=TextLoader)
            ingested_documents.extend(txt_loader.load())

            json_files = list(path.glob("**/*.json"))
            for json_file in json_files:
                print(f"\033[1;34m[INFO]\033[0m Found JSON file: '{json_file}'. Loading with custom JSON plaintext loader.")
                json_loader = JsonPlaintextLoader(str(json_file))
                ingested_documents.extend(json_loader.load())

            if not ingested_documents:
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

        print(f"\033[1;34m[INFO]\033[0m Adding new chunks to vector store (safe mode: 1 by 1)...")
        success, failed = 0, 0

        for i, chunk in enumerate(new_chunks, start=1):
            try:
                vectorstore.add_documents([chunk])
                success += 1
                if i % 20 == 0 or i == len(new_chunks):
                    print(f"\033[1;32m[OK]\033[0m Added {success}/{i} chunks so far.")
            except Exception as e:
                failed += 1
                print(f"\033[91m[ERROR]\033[0m Failed on chunk {i}: {e}")

        print(f"\033[1;34m[INFO]\033[0m Ingestion finished. "
            f"Success: {success}, Failed: {failed}, Total: {len(new_chunks)}")

        # Optional: verify embeddings
        sample = new_chunks[0].page_content[:100].replace("\n", " ")
        vec = embeddings.embed_query(sample)
        print(f"\033[1;34m[INFO]\033[0m Verified embedding vector size: {len(vec)}")

    except Exception as e:
        print(f"\033[91m[ERROR]\033[0m An error occurred during ingestion from '{path_to_ingest}': {e}")

def ingest_conversation_history(conversation_history: list, vectorstore, text_splitter, embeddings):
    """
    Ingests conversation history from a list of dictionaries.
    """
    from langchain_core.documents import Document

    documents_to_ingest = []
    for turn in conversation_history:
        # Combine user and AEON messages into a single document
        content = f"User: {turn.get('user', '')}\nAEON: {turn.get('aeon', '')}"
        documents_to_ingest.append(Document(page_content=content))
    
    # Split the new documents and add to the vector store
    new_chunks = text_splitter.split_documents(documents_to_ingest)
    if new_chunks:
        try:
            vectorstore.add_documents(new_chunks)
            print(f"\033[1;32m[OK]\033[0m Successfully added {len(new_chunks)} conversation chunks to the vector store.")
        except Exception as e:
            print(f"\033[91m[ERROR]\033[0m Failed to add conversation chunks to vector store: {e}")
    else:
        print(f"\033[1;33m[NOTE]\033[0m No new chunks were created from the conversation history.")