# src/utils/webSearch.py

import sys
from ddgs import DDGS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from src.config import (
    SYSTEM_PROMPT,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_TOP_P,
    LLM_TOP_K,
    LLM_N_CTX,
)
from src.libs.messages import *

def webSearch(search_query: str, llm_instance: LlamaCpp, text_splitter: RecursiveCharacterTextSplitter, vectorstore: Chroma) -> str:

    print_info_message(f"Searching DuckDuckGo for: '{search_query}'...")
    try:
        search_results = DDGS().text(query=search_query, safesearch='off', max_results=5) 
        search_context = ""
        if search_results:
            for i, result in enumerate(search_results):
                if i >= 3:
                    break
                search_context += f"{result.get('body', 'N/A')}\n\n"

            # print(f"\033[1;34m[WEBSEARCH]\033[0m", search_context)
            print_info_message("DuckDuckGo search results obtained. Incorporating into RAG chain...")

            print_info_message("Ingesting search results into Chroma DB (chunk by chunk)...")
            try:
                search_doc = Document(
                    page_content=search_context,
                    metadata={"source": "web_search", "query": search_query}
                )
                search_chunks = text_splitter.split_documents([search_doc])

                if search_chunks:
                    print_info_message(f"Generated {len(search_chunks)} chunks for web search ingestion.")

                    success_count = 0
                    for i, chunk in enumerate(search_chunks):
                        try:
                            vectorstore.add_documents([chunk])
                            success_count += 1
                            print_info_message(f"  Ingested chunk {i+1}/{len(search_chunks)} successfully.")
                        except Exception as e_chunk_ingest:
                            print_error_message(f"  FAILED to ingest chunk {i+1}/{len(search_chunks)}: {e_chunk_ingest}")
                            
                    if success_count > 0:
                        print_success_message(f"Completed ingestion. Successfully ingested {success_count}/{len(search_chunks)} chunks from web search into Chroma DB.")
                    else:
                        print_error_message("No chunks were successfully ingested into Chroma DB.")
                        return "I found search results, but encountered an error ingesting them into my knowledge base. Please check the logs for details."
                else:
                    print_note_message("No chunks generated from web search context for ingestion. Skipping Chroma addition.")
            except Exception as e_ingest:
                print_error_message(f"FAILED TO INGEST search results into Chroma DB: {e_ingest}. This typically means an embedding error or context window issue with the embedding model.")
                return f"An error occurred while adding search results to my knowledge base: {e_ingest}. This might be due to the text being too long for my embedding model or a memory issue."

            summarize_prompt_template_string = (
                "<|im_start|>system\n"
                f"{SYSTEM_PROMPT}\n"
                "Your responses should be in plain, natural language ONLY, without special formatting or prefixes. "
                "Summarize the provided CONTEXT concisely and clearly. Focus on extracting the most relevant information related to the QUESTION. "
                "Do NOT engage in chitchat or introduce outside knowledge. Provide ONLY the summary. "
                "The summary should be directly about the search query and the context provided.\n"
                "<|im_end|>\n"
                "<|im_start|>user\n"
                "CONTEXT:\n{context}\n\n"
                "QUESTION:\nSummarize the contents about {query}\n" 
                "<|im_end|>\n"
                "<|im_start|>assistant\n"
                "RESPONSE:"
            )
            summarize_prompt = PromptTemplate.from_template(summarize_prompt_template_string)

            formatted_summary_input = summarize_prompt.format(
                context=search_context,
                query=search_query
            )
            
            summary_response = llm_instance.invoke(formatted_summary_input)
            
            print_success_message("Search results summarized.")
            return summary_response

        else:
            return print_info_message("No relevant search results found.")

    except Exception as e:
        print_error_message(f"Failed to perform DuckDuckGo web search or process results: {e}")
        return print_error_message("An error occurred during the web search.")

