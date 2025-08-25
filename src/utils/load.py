# src/utils/load.py
from pathlib import Path

from src.libs.messages import print_info_message, print_success_message, print_error_message
from src.utils.conversation import loadConversation
from src.utils.ingestion import ingestDocuments

def loadIngestConversation(
    conv_id: str,
    memory_dir_path: Path,
    vectorstore,
    text_splitter,
    llama_embeddings
):
    """
    Loads and ingests a conversation file into the current RAG session's vector store.
    """
    conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    try:
        idx = int(conv_id) - 1
        if 0 <= idx < len(conversation_dirs):
            selected_conv_path = conversation_dirs[idx]
            conversation_hash_name = selected_conv_path.name
            conversation_filename = f"conversation_{conversation_hash_name}.json"
            
            print_info_message(f"Loading conversation from: {conversation_hash_name}")

            loaded_history = loadConversation(selected_conv_path, conversation_filename)

            if loaded_history:
                ingestDocuments(str(selected_conv_path / conversation_filename), vectorstore, text_splitter, llama_embeddings)
                
                print_success_message(f"Successfully ingested conversation history from '{conversation_hash_name}' into the current session's knowledge base.")
            else:
                print_error_message(f"Could not load conversation from '{conversation_hash_name}'. File not found or is empty.")
        else:
            print_error_message("Invalid conversation number.")
    except (ValueError, IndexError):
        print_error_message("Invalid input. Please provide a number from the list.")