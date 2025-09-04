# plugins/aeon/main.py
from pathlib import Path
import sys
import os
from src.libs.messages import (print_info_message, print_success_message,
                               print_error_message)

from src.utils.ingestion import ingestDocuments
from src.libs.loaders import JsonPlaintextLoader

project_root = Path(__file__).resolve().parent

def run_plugin(*args, **kwargs) -> None:
    vectorstore = kwargs.get("vectorstore")
    text_splitter = kwargs.get("text_splitter")
    embeddings = kwargs.get("embeddings")

    paths_to_ingest = os.path.join(project_root, "model")
    
    if not paths_to_ingest:
        print_error_message(
            "Plugin configuration is missing the 'path_to_ingest' parameter."
        )
        return

    if isinstance(paths_to_ingest, str):
        paths_to_ingest = [paths_to_ingest]

    for path in paths_to_ingest:
        print_info_message(f"Starting ingestion process for path: '{path}'")
        
        ingestDocuments(
            path_to_ingest=path,
            vectorstore=vectorstore,
            text_splitter=text_splitter,
            embeddings=embeddings
        )

    print_success_message("All specified ingesting completed.")
    