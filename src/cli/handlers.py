import sys
import os
from pathlib import Path
from src.utils.ingestion import ingestDocuments
from src.utils.webSearch import webSearch
from src.utils.zipBackup import zipBackup
from src.utils.conversation import saveConversation
from src.utils.list import listConversations
from src.utils.open import openConversation
from src.utils.new import newConversation
from src.utils.load import loadBackup
from src.utils.delete import deleteConversation
from src.utils.rename import renameConversation

from src.libs.messages import print_error_message, print_info_message, print_aeon_message,print_source_message, print_think_message
from src.cli.termPrompts import startup_prompt
from langchain.docstore.document import Document

def _initialize_session(memory_dir_path: Path):
    user_choice = startup_prompt(memory_dir_path)
    if user_choice.startswith("/load"):
        zip_path = user_choice[len("/load "):].strip()
        success = loadBackup(zip_path, memory_dir_path)
        if success:
            return _initialize_session(memory_dir_path)
        else:
            print_error_message("Unzipping failed. Please try again.")
            return _initialize_session(memory_dir_path)
        
    try:
        choice_int = int(user_choice)
        conversation_dirs = [d for d in memory_dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]

        if 1 <= choice_int <= len(conversation_dirs):
            return openConversation(
                str(choice_int),
                memory_dir_path,
                None,
                None,
                None,
                None,
                None)
        elif (choice_int == len(conversation_dirs) + 1 or (not conversation_dirs and choice_int == 1)):
            return newConversation(memory_dir_path)
        else:
            print_error_message("Invalid choice. Exiting.")
            sys.exit()
    except (ValueError, IndexError):
        print_error_message("Invalid input. Please enter a number.")
        sys.exit()


def _handle_ingest(user_input, session_vars):
    if not isinstance(user_input, str):
        print_error_message(
            "Invalid input to the ingest handler. Expected a string but received a dictionary."
        )
        return
    
    ingest_path = user_input[len("/ingest "):].strip()
    ingestDocuments(
        ingest_path,
        session_vars["vectorstore"],
        session_vars["text_splitter"],
        session_vars["llama_embeddings"]
    )


def _handle_zip(user_input, session_vars):
    print_info_message("Zipping memory folder contents...")
    try:
        archive_path = zipBackup(
            session_vars["current_memory_path"], session_vars["output_dir_path"])
        if archive_path:
            print_info_message(f"Conversation successfully zipped to {archive_path}.")
        else:
            print_error_message("Failed to zip conversation folder.")
    except Exception as e:
        print_error_message(f"An error occurred during zipping: {e}")


def _handle_load(user_input, session_vars):
    zip_path = user_input[len("/load "):].strip()
    loadBackup(zip_path, session_vars)


def _handle_search(user_input, session_vars):
    search_query = user_input[len("/search "):].strip()
    summarized_search_results = webSearch(
        search_query,
        session_vars["llm_instance"],
        session_vars["text_splitter"],
        session_vars["vectorstore"]
    )
    print_aeon_message(f"{summarized_search_results[0]}\n\n{summarized_search_results[1]}")
    saveConversation(
        user_input,
        summarized_search_results[0],
        summarized_search_results[1],
        session_vars["current_memory_path"],
        session_vars["conversation_filename"]
    )
    session_vars["current_chat_history"].append(
        {"user": user_input, "aeon": summarized_search_results})

def _ingest_conversation_turn(user_input, aeon_output, vectorstore, text_splitter, llama_embeddings):
    try:
        conversation_text = f"{user_input}\n\n{aeon_output}"
        
        conversation_document = Document(
            page_content=conversation_text,
            metadata={"source": "memory"}
        )
        
        docs = text_splitter.split_documents([conversation_document])
        success, failed = 0, 0
        for i, chunk in enumerate(docs, start=1):
            try:
                vectorstore.add_documents([chunk])
                success += 1
               
            except Exception as e:
                failed += 1
                print_error_message(f" Failed on chunk {i}: {e}")

        
    except Exception as e:
        print_error_message(f"Failed to ingest conversation turn: {e}")

def _handle_rag_chat(user_input, session_vars):
    rag_chain = session_vars.get("rag_chain")
    if not rag_chain:
        print_error_message("RAG system not initialized. Type /restart to begin.")
        return

    print_think_message("Thinking...")
    
    try:
        result = rag_chain.invoke(user_input)

        answer = result.get("answer", "No answer found.")
        context_docs = result.get("context", [])

        sources_count = {}
        for doc in context_docs:
            source = doc.metadata.get("source")
            if source:
                cleaned_source = Path(source)
                
                sources_count[cleaned_source] = sources_count.get(cleaned_source, 0) + 1

        formatted_list = [f"{source} ({count}x)" for source, count in sources_count.items()]
        formatted_sources = "\n".join(formatted_list) if formatted_list else "No sources found."

        
        saveConversation(
            user_input,
            answer,
            formatted_sources,
            session_vars["current_memory_path"],
            session_vars["conversation_filename"]
        )
        session_vars["current_chat_history"].append(
            {"user": user_input, "aeon": answer, "source": formatted_sources}
        )

        _ingest_conversation_turn(
            user_input,
            answer,
            session_vars["vectorstore"],
            session_vars["text_splitter"],
            session_vars["llama_embeddings"]
        )


        print_aeon_message(f"{answer}")
        print_source_message(f"\n{formatted_sources}")


    except Exception as e:
        print_error_message(f"An error occurred during RAG processing: {e}")


def _handle_delete(user_input, session_vars):
    deleteConversation(user_input, session_vars)
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def _handle_rename(user_input, session_vars):
    renameConversation(user_input, session_vars)
    python = sys.executable
    os.execv(python, [python] + sys.argv)


def _handle_restart(session_vars):
    print_info_message("Restarting AEON...")
    python = sys.executable
    os.execv(python, [python] + sys.argv)
