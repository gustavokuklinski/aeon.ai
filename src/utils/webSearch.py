import json
import sqlite3
from pathlib import Path
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from ddgs import DDGS

from src.config import SYSTEM_PROMPT
from src.libs.messages import (
    print_success_message,
    print_info_message,
    print_error_message,
    print_note_message
)


def _perform_search_and_get_context(search_query: str) -> list:
    """
    Performs a DuckDuckGo search and extracts relevant text and links.
    Returns a list of dictionaries, each containing 'title', 'body', and 'href'.
    """
    print_info_message(f"Searching DuckDuckGo for: '{search_query}'...")
    search_results = DDGS().text(query=search_query, backend='duckduckgo',
                                 safesearch='on', max_results=5)
    
    formatted_results = []
    if search_results:
        for i, result in enumerate(search_results):
            # Limit to the top 3 results for a concise context
            if i >= 3:
                break
            formatted_results.append({
                "title": result.get('title', 'N/A'),
                "body": result.get('body', 'N/A'),
                "href": result.get('href', 'N/A')
            })
        print_info_message("DuckDuckGo search results obtained.")
    return formatted_results


def _ingest_search_results(
        search_docs: list[Document],
        text_splitter: RecursiveCharacterTextSplitter,
        vectorstore: Chroma) -> bool:

    try:
        all_chunks = []
        for doc in search_docs:
            chunks = text_splitter.split_documents([doc])
            all_chunks.extend(chunks)

        if not all_chunks:
            print_note_message(
                "No chunks generated from web search context "
                "for ingestion. Skipping Chroma addition.")
            return True

        print_info_message(
            f"Generated {len(all_chunks)} chunks for web search ingestion.")
        success_count = 0
        for i, chunk in enumerate(all_chunks):
            try:
                vectorstore.add_documents([chunk])
                success_count += 1
                print_info_message(
                    f"Ingested chunk {i + 1}/{len(all_chunks)} "
                    "successfully.")
            except Exception as e_chunk_ingest:
                print_error_message(
                    "FAILED to ingest chunk "
                    f"{i + 1}/{len(all_chunks)}: {e_chunk_ingest}")

        if success_count > 0:
            print_success_message(
                "Completed ingestion. Successfully ingested "
                f"{success_count}/{len(all_chunks)} chunks.")
            return True
        else:
            print_error_message(
                "No chunks were successfully ingested into Chroma DB.")
            return False
    except Exception as e_ingest:
        print_error_message(
            f"FAILED TO INGEST search results into Chroma DB: {e_ingest}. "
            "This typically means an embedding error or context "
            "window issue with the embedding model.")
        return False


def _generate_summary(
        search_context: str,
        search_query: str,
        llm_instance: LlamaCpp) -> str:
    """Generates a summary of the search context using the language model."""
    summarize_prompt_template_string = (
        "<|im_start|>system\n"
        f"{SYSTEM_PROMPT}\n"
        "Your responses should be in plain, natural language ONLY, "
        "without special formatting or prefixes. "
        "Summarize the provided CONTEXT concisely and clearly. "
        "Do NOT engage in chitchat or introduce outside knowledge. "
        "Provide ONLY the summary. The summary should be directly about the "
        "search query and the context provided.\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "{context}\n"
        "Summarize the contents about {query}\n"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    summarize_prompt = PromptTemplate.from_template(
        summarize_prompt_template_string)
    formatted_summary_input = summarize_prompt.format(
        context=search_context,
        query=search_query
    )
    summary_response = llm_instance.invoke(formatted_summary_input)
    print_success_message("Search results summarized.")

    return summary_response


def webSearch(
        search_query: str,
        llm_instance: LlamaCpp,
        text_splitter: RecursiveCharacterTextSplitter,
        vectorstore: Chroma) -> None:

    try:
        search_results = _perform_search_and_get_context(search_query)

        if not search_results:
            print_info_message("No relevant search results found.")
            return "No relevant search results were found for your query.", []

        print_info_message("Incorporating into RAG chain...")
        
        search_docs = []
        search_context = ""
        for result in search_results:
            search_context += f"{result['body']}\n\n"
            search_docs.append(
                Document(
                    page_content=result['body'],
                    metadata={
                        "source": result['href'], 
                        "query": search_query
                    }
                )
            )

        if not _ingest_search_results(search_docs, text_splitter, vectorstore):
            return (
                "I found search results, but encountered an error "
                "ingesting them into my knowledge base. Please check "
                "the logs for details."
            ), search_results
        
        summary = _generate_summary(search_context, search_query, llm_instance)

        formatted_links = ""
        for link in search_results:
            formatted_links += f"{link['href']}\n"
            
        final_output = f"{summary}"
        final_sources = f"{formatted_links}"
        print(search_context)
        return final_output, final_sources

    except Exception as e:
        print_error_message(
            f"Failed to perform DuckDuckGo web search or process results: {e}")
        return "An error occurred during the web search.", []
