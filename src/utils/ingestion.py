# src/libs/ingestion.py

from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    UnstructuredFileLoader,
    TextLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import LlamaCppEmbeddings

from src.libs.loaders import JsonPlaintextLoader

from src.libs.messages import (
    print_info_message,
    print_error_message,
    print_success_message,
    print_note_message
)


def _load_single_file(path: Path) -> list[Document]:
    """Load a single document based on its file extension."""
    if path.suffix.lower() == ".md":
        loader = UnstructuredMarkdownLoader(str(path))
    elif path.suffix.lower() == ".txt":
        print_info_message("Detected .txt file. Loading as plain text.")
        loader = TextLoader(str(path))
    elif path.suffix.lower() == ".json":
        print_info_message(
            "Detected .json file. Loading with custom JSON plaintext loader.")
        loader = JsonPlaintextLoader(str(path))
    else:
        print_info_message(
            "Attempting to load with UnstructuredFileLoader for unknown type.")
        loader = UnstructuredFileLoader(str(path))
    return loader.load()


def _load_directory_documents(path: Path) -> list[Document]:

    all_documents = []

    md_loader = DirectoryLoader(
        str(path), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    all_documents.extend(md_loader.load())

    txt_loader = DirectoryLoader(
        str(path), glob="**/*.txt", loader_cls=TextLoader)
    all_documents.extend(txt_loader.load())

    json_files = list(path.glob("**/*.json"))
    for json_file in json_files:
        print_info_message(
            f"Found JSON file: '{json_file}'. "
            "Loading with custom JSON plaintext loader.")
        json_loader = JsonPlaintextLoader(str(json_file))
        all_documents.extend(json_loader.load())

    return all_documents


def ingestDocuments(
        path_to_ingest: str,
        vectorstore: Chroma,
        text_splitter: RecursiveCharacterTextSplitter,
        embeddings: LlamaCppEmbeddings):

    path = Path(path_to_ingest)

    if not path.exists():
        print_error_message(f"Path not found: '{path_to_ingest}'")
        return

    try:
        if path.is_file():
            print_info_message(
                f"Ingesting single file: '{path_to_ingest}'")
            ingested_documents = _load_single_file(path)
        elif path.is_dir():
            print_info_message(
                f"Ingesting documents from directory: '{path_to_ingest}'")
            ingested_documents = _load_directory_documents(path)
        else:
            print_error_message(
                f"Invalid path type: '{path_to_ingest}'. "
                "Please provide a file or a directory.")
            return

        if not ingested_documents:
            print_note_message(
                f"No documents found to ingest at '{path_to_ingest}'.")
            return

        print_info_message(f"Loaded {len(ingested_documents)} new documents.")
        new_chunks = text_splitter.split_documents(ingested_documents)
        print_info_message(f"Split into {len(new_chunks)} chunks.")

        print_info_message("Adding new chunks to "
                           "vector store (safe mode: 1 by 1)...")
        success, failed = 0, 0
        for i, chunk in enumerate(new_chunks, start=1):
            try:
                vectorstore.add_documents([chunk])
                success += 1
                if i % 20 == 0 or i == len(new_chunks):
                    print_success_message(
                        f"Added {success}/{i} chunks so far.")
            except Exception as e:
                failed += 1
                print_error_message(f" Failed on chunk {i}: {e}")

        print_info_message(
            f"Ingestion finished. Success: {success}, "
            f"Failed: {failed}, Total: {len(new_chunks)}")

        if new_chunks:
            sample = new_chunks[0].page_content[:100].replace("\n", " ")
            vec = embeddings.embed_query(sample)
            print_info_message(f"Verified embedding vector size: {len(vec)}")

    except Exception as e:
        print_error_message(
            f"An error occurred during ingestion from '{path_to_ingest}': {e}")


def ingestConversationHistory(
        conversation_history: list,
        vectorstore,
        text_splitter,
        embeddings):
    # This function is fine and does not need to be changed
    documents_to_ingest = []
    for turn in conversation_history:
        content = f"USER: {turn.get('user', '')}\nAEON: {turn.get('aeon', '')}"
        documents_to_ingest.append(Document(page_content=content))

    new_chunks = text_splitter.split_documents(documents_to_ingest)
    if new_chunks:
        try:
            vectorstore.add_documents(new_chunks)
            print_success_message(
                f"Successfully added {len(new_chunks)} "
                "conversation chunks to the vector store.")
        except Exception as e:
            print_error_message(
                f"Failed to add conversation chunks to vector store: {e}")
    else:
        print_note_message(
            "No new chunks were created "
            "from the conversation history.")
