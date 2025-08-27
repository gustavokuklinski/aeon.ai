# src/utils/new.py
import hashlib
from datetime import datetime
from pathlib import Path
from src.libs.messages import print_boot_message, print_success_message
from src.core.ragSystem import ragSystem


def newConversation(memory_dir_path: Path):
    print_boot_message("Starting a new conversation...")

    timestamp_base = datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
    hash_object = hashlib.md5(timestamp_base.encode())
    conversation_hash = hash_object.hexdigest()[:5]

    current_memory_path = memory_dir_path / conversation_hash
    current_memory_path.mkdir(parents=True, exist_ok=True)

    chroma_db_dir_path = current_memory_path / 'db'
    conversation_filename = f"conversation_{conversation_hash}.json"
    current_chat_history = []

    (rag_chain, vectorstore, text_splitter,
     llama_embeddings, llm_instance) = ragSystem(
        current_memory_path, chroma_db_dir_path, is_new_session=True)

    print_success_message("New conversation started.")

    return {
        "conv_id": conversation_hash,
        "rag_chain": rag_chain,
        "vectorstore": vectorstore,
        "text_splitter": text_splitter,
        "llama_embeddings": llama_embeddings,
        "llm_instance": llm_instance,
        "current_memory_path": current_memory_path,
        "conversation_filename": conversation_filename,
        "current_chat_history": current_chat_history,
        "user_prompt_string": f"\033[92m[\033[93m{conversation_hash}\033[92m@\033[92m>>>>]:\033[0m "
    }
