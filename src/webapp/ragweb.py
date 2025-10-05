# src/web/ragWeb.py
from pathlib import Path

from src.core.ragSystem import ragSystem
from src.libs.messages import print_info_message, print_error_message, print_success_message

rag_system_state = {}

def initialize_rag_system(
    conv_id: str,
    abs_memory_dir: Path
):

    print_info_message(f"Attempting to load conversation ID: {conv_id}")
    conv_dir_path = abs_memory_dir / conv_id
    if not conv_dir_path.is_dir():
        print_error_message(f"Conversation directory for ID '{conv_id}' not found.")
        return None
    
    try:
        rag_chain, vectorstore, text_splitter, llama_embeddings, llm_instance = ragSystem(
            conversation_memory_path=conv_dir_path,
            chroma_db_dir_path=conv_dir_path / "db",
            is_new_session=False
        )
        print_success_message(f"Successfully loaded RAG system for conversation ID: {conv_id}")
        return {
            "rag_chain": rag_chain,
            "vectorstore": vectorstore,
            "text_splitter": text_splitter,
            "llama_embeddings": llama_embeddings,
            "llm_instance": llm_instance,
            "current_memory_path": conv_dir_path,
            "conversation_filename": f"{conv_id}.json",
            "current_conversation_id": conv_id,
            "current_chat_history": []
        }
    except Exception as e:
        print_error_message(f"Error loading conversation '{conv_id}': {e}")
        return None
