# src/utils/open.py
from pathlib import Path
from src.libs.messages import (print_boot_message,
                               print_success_message, print_error_message)
from src.core.ragSystem import ragSystem
from src.utils.conversation import loadConversation


def openConversation(
    conv_id: str,
    memory_dir_path: Path,
    rag_chain,
    vectorstore,
    text_splitter,
    llama_embeddings,
    llm_instance
):

    conversation_dirs = [d for d in memory_dir_path.iterdir(
    ) if d.is_dir() and not d.name.startswith('.')]

    try:
        idx = int(conv_id) - 1
        if 0 <= idx < len(conversation_dirs):
            selected_conv_path = conversation_dirs[idx]
            conversation_hash_name = selected_conv_path.name

            print_boot_message(
                f"Opening conversation: {conversation_hash_name}")

            current_memory_path = selected_conv_path
            chroma_db_dir_path = current_memory_path / "db"
            conversation_filename = (f"{conversation_hash_name}.json")

            (rag_chain, vectorstore, text_splitter,
             llama_embeddings, llm_instance) = ragSystem(
                current_memory_path, chroma_db_dir_path, is_new_session=False)

            current_chat_history = loadConversation(
                current_memory_path, conversation_filename)

            print_success_message(
                "Successfully loaded conversation"
                f"from '{conversation_hash_name}'.")

            return {
                "rag_chain": rag_chain,
                "vectorstore": vectorstore,
                "text_splitter": text_splitter,
                "llama_embeddings": llama_embeddings,
                "llm_instance": llm_instance,
                "current_memory_path": current_memory_path,
                "conversation_filename": conversation_filename,
                "current_chat_history": current_chat_history,
                "user_prompt_string": f"\033[92m[\033[93m{conversation_hash_name}\033[92m@\033[92m>>>>]:\033[0m "
            }
        else:
            print_error_message("Invalid conversation number.")
    except (ValueError, IndexError):
        print_error_message(
            "Invalid input. Please provide a number from the list.")

    return None
