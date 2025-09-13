import json
import sqlite3
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    UnstructuredMarkdownLoader,
    UnstructuredFileLoader,
    TextLoader,
    CSVLoader)
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


def _parse_file_metadata(path: Path) -> dict:
    """Extracts metadata from a file path."""
    metadata = {
        "source": str(path),
        "file_path": str(path.resolve()),
        "file_name": path.name,
        "file_type": path.suffix.lstrip('.'),
        "file_size": path.stat().st_size if path.exists() else 0,
    }
    return metadata


def _load_sqlite_db(path: Path) -> list[Document]:
    """
    Loads documents from a SQLite3 database file.
    Assumes a table named 'conversations' with columns: GUID, USER, AEON, CHAT_ID, TIMESTAMP.
    """
    documents = []
    try:
        with sqlite3.connect(path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations ORDER BY TIMESTAMP ASC")
            rows = cursor.fetchall()
            
            for row in rows:
                content = f"user: {row['USER']}\naeon: {row['AEON']}\nsource: {row['SOURCE']}"
                metadata = {
                    "source": str(path),
                    "guid": row['GUID'],
                    "chat_id": row['CHAT_ID'],
                    "timestamp": row['TIMESTAMP']
                }
                documents.append(Document(page_content=content, metadata=metadata))
            
            print_success_message(f"Successfully loaded {len(documents)} records from the database.")
    except sqlite3.Error as e:
        print_error_message(f"SQLite database error when loading '{path}': {e}")
        return []
    except Exception as e:
        print_error_message(f"An unexpected error occurred while loading the database file: {e}")
        return []
        
    return documents


def _load_single_file(path: Path) -> list[Document]:
    """Load a single document based on its file extension and parse metadata."""
    if path.suffix.lower() == ".md":
        loader = UnstructuredMarkdownLoader(str(path))
    elif path.suffix.lower() == ".txt":
        print_info_message("Detected .txt file. Loading as plain text.")
        loader = TextLoader(str(path))
    elif path.suffix.lower() == ".json":
        print_info_message(
            "Detected .json file. Loading with custom JSON plaintext loader.")
        loader = JsonPlaintextLoader(str(path))
    elif path.suffix.lower() == ".csv":
        print_info_message("Detected .csv file. Loading with CSVLoader.")
        loader = CSVLoader(str(path))
    elif path.suffix.lower() == ".sqlite3":
        print_info_message("Detected .sqlite3 file. Loading as SQLite database.")
        return _load_sqlite_db(path)
    else:
        print_info_message(
            "Attempting to load with UnstructuredFileLoader for unknown type.")
        loader = UnstructuredFileLoader(str(path))
        
    documents = loader.load()
    metadata = _parse_file_metadata(path)
    for doc in documents:
        doc.metadata.update(metadata)
    
    return documents


def _load_directory_documents(path: Path) -> list[Document]:

    all_documents = []

    md_loader = DirectoryLoader(
        str(path), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    md_docs = md_loader.load()
    for doc in md_docs:
        doc.metadata.update(_parse_file_metadata(Path(doc.metadata['source'])))
    all_documents.extend(md_docs)

    txt_loader = DirectoryLoader(
        str(path), glob="**/*.txt", loader_cls=TextLoader)
    txt_docs = txt_loader.load()
    for doc in txt_docs:
        doc.metadata.update(_parse_file_metadata(Path(doc.metadata['source'])))
    all_documents.extend(txt_docs)

    csv_loader = DirectoryLoader(
        str(path), glob="**/*.csv", loader_cls=CSVLoader)
    csv_docs = csv_loader.load()
    for doc in csv_docs:
        doc.metadata.update(_parse_file_metadata(Path(doc.metadata['source'])))
    all_documents.extend(csv_docs)

    json_files = list(path.glob("**/*.json"))
    for json_file in json_files:
        print_info_message(
            f"Found JSON file: '{json_file}'. "
            "Loading with custom JSON plaintext loader.")
        json_loader = JsonPlaintextLoader(str(json_file))
        json_docs = json_loader.load()
        for doc in json_docs:
            doc.metadata.update(_parse_file_metadata(json_file))
        all_documents.extend(json_docs)
        
    db_files = list(path.glob("**/*.sqlite3"))
    for db_file in db_files:
        print_info_message(
            f"Found SQLite database file: '{db_file}'. "
            "Loading conversation history from it.")
        all_documents.extend(_load_sqlite_db(db_file))

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
        if ingested_documents:
            first_doc_meta = ingested_documents[0].metadata
            print_info_message(f"Sample metadata: {first_doc_meta}")

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
    documents_to_ingest = []
    for turn in conversation_history:
        content = f"USER: {turn.get('user', '')}\nAEON: {turn.get('aeon', '')}\nSOURCE: {turn.get('source', '')}"
        metadata = {
            "source": "conversation_history",
            "guid": turn.get("guid"),
            "chat_id": turn.get("chat_id"),
            "timestamp": turn.get("timestamp")
        }
        documents_to_ingest.append(Document(page_content=content, metadata=metadata))

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
