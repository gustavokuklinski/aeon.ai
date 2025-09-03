import yaml
from pathlib import Path
from src.libs.messages import (print_boot_message,
                               print_success_message, print_error_message,
                               print_info_message)
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

    conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]

    try:
        idx = int(conv_id) - 1
        if 0 <= idx < len(conversation_dirs):
            selected_conv_path = conversation_dirs[idx]
            conversation_hash_name = selected_conv_path.name

            print_boot_message(f"Opening conversation: {conversation_hash_name}")
            
            current_memory_path = memory_dir_path / conversation_hash_name
            config_path = current_memory_path / "config.yml"
            
            # Load the config file for the selected conversation
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    conversation_config = yaml.safe_load(f)
                print_info_message(f"Loaded config from: {config_path}")
            except FileNotFoundError:
                print_error_message(f"Configuration file not found for this conversation: {config_path}")
                return None
            except Exception as e:
                print_error_message(f"Failed to load config file: {e}")
                return None

            chroma_db_dir_path = current_memory_path / "db"
            conversation_filename = (f"{conversation_hash_name}.json")

            (rag_chain, vectorstore, text_splitter,
                llama_embeddings, llm_instance) = ragSystem(
                current_memory_path, chroma_db_dir_path, is_new_session=False)

            current_chat_history = loadConversation(
                current_memory_path, conversation_filename)

            print_success_message(
                "Successfully loaded conversation"
                f" from '{conversation_hash_name}'.")

            return {
                "rag_chain": rag_chain,
                "vectorstore": vectorstore,
                "text_splitter": text_splitter,
                "llama_embeddings": llama_embeddings,
                "llm_instance": llm_instance,
                "current_memory_path": current_memory_path,
                "conversation_filename": conversation_filename,
                "current_chat_history": current_chat_history,
                "loaded_config": conversation_config,
                "user_prompt_string": f"\033[92m[\033[93m{conversation_hash_name}\033[92m@\033[92m>>>>]:\033[0m "
            }
        
        else:
            print_error_message("Invalid input. Please provide a number from the list.")
            return None

    except ValueError:
        print_error_message("Invalid input. Please provide a number from the list.")
        return None
