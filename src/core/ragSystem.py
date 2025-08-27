# src/core/ragSystem.py

import os
import sys
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, UnstructuredMarkdownLoader, TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_community.embeddings import LlamaCppEmbeddings

from src.libs.loaders import JsonPlaintextLoader

from src.config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    EMB_MODEL,
    EMB_N_CTX,
    EMB_CHUNK_SIZE,
    EMB_CHUNK_OVERLAP,
    INPUT_DIR,
    SYSTEM_PROMPT,
    LLM_N_CTX,
    LLM_TOP_P,
    LLM_TOP_K
)
from src.libs.messages import (
    print_error_message, print_info_message, print_success_message
)


def ragSystem(conversation_memory_path: Path,
              chroma_db_dir_path: Path, is_new_session: bool):

    project_root = Path(__file__).parent.parent.parent
    input_dir_path = project_root / INPUT_DIR

    if not os.path.exists(input_dir_path):
        print_error_message(
            f"Directory '{input_dir_path}' not found. Please create it.")
        sys.exit(1)

    print_info_message(f"Loading initial documents from: {input_dir_path}")
    documents = []
    md_loader = DirectoryLoader(
        str(input_dir_path), glob="**/*.md",
        loader_cls=UnstructuredMarkdownLoader)
    documents.extend(md_loader.load())
    txt_loader = DirectoryLoader(
        str(input_dir_path), glob="**/*.txt",
        loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    json_files = list(input_dir_path.glob("**/*.json"))
    for json_file in json_files:
        json_loader = JsonPlaintextLoader(str(json_file))
        documents.extend(json_loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=EMB_CHUNK_SIZE,
        chunk_overlap=EMB_CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)

    print_info_message(f"Loading embedding model: {EMB_MODEL}")
    llama_embeddings = LlamaCppEmbeddings(
        model_path=EMB_MODEL,
        n_ctx=EMB_N_CTX,
        verbose=False
    )

    batch_size = 32

    if not chroma_db_dir_path.exists() or not os.listdir(chroma_db_dir_path):
        if not chunks:
            print_info_message(
                f"No initial documents found. Creating an"
                "empty vector store at "
                f"{chroma_db_dir_path}...")
            vectorstore = Chroma(
                persist_directory=str(chroma_db_dir_path),
                embedding_function=llama_embeddings
            )

        else:
            print_info_message(
                f"Vector store not found. Creating a new one with "
                f"{len(chunks)} chunks at {chroma_db_dir_path}...")
            vectorstore = Chroma(
                persist_directory=str(chroma_db_dir_path),
                embedding_function=llama_embeddings
            )
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                try:
                    vectorstore.add_documents(batch)
                    print_info_message(
                        f"Ingested chunks {i + 1} to "
                        f"{min(i + batch_size, len(chunks))}.")
                except Exception as e:
                    print_error_message(
                        f"Failed to ingest batch starting at index {i}: {e}")
            print_success_message("Initial document ingestion complete.")
    else:
        print_info_message(
            f"Loading existing vector"
            f"store from {chroma_db_dir_path}...")
        vectorstore = Chroma(
            persist_directory=str(chroma_db_dir_path),
            embedding_function=llama_embeddings
        )
        if chunks:
            print_info_message(
                f"Adding {len(chunks)} new chunks to vector store.")
            for i, chunk in enumerate(chunks, start=1):
                try:
                    vectorstore.add_documents([chunk])
                    if i % 20 == 0 or i == len(chunks):
                        print_info_message(f"Added {i}/{len(chunks)} chunks.")
                except Exception as e:
                    print_error_message(f"Failed on chunk {i}: {e}")

    retriever = vectorstore.as_retriever()

    print_info_message(f"Loading LLM: {LLM_MODEL}")

    llm = LlamaCpp(
        model_path=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        top_p=LLM_TOP_P,
        top_k=LLM_TOP_K,
        n_ctx=LLM_N_CTX,
        stop=["<|im_end|>", "\nQUESTION:", "\nCONTEXT:", "RESPONSE:"],
        verbose=False,
    )

    qa_prompt = PromptTemplate.from_template(
        "<|im_start|>system\n"
        f"{SYSTEM_PROMPT}\n"
        "Your responses should be in plain, natural language ONLY."
        "Determine the nature of the user's QUESTION. "
        "If the question is factual, follow this process: "
        "1. Scan the CONTEXT for all relevant facts."
        "2. Combine these facts to form a single, comprehensive answer."
        "3. If context is unavailable, "
        "state: 'I don't know about it. Can we /search?'."
        "If the question is conversational "
        "or non-factual, respond naturally and "
        "conversationally, without referring to the CONTEXT."
        "Do not echo the user's QUESTION or the CONTEXT."
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "CONTEXT:{context}\n"
        "QUESTION:{question}\n"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
        "RESPONSE:"
    )

    document_combiner = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | document_combiner
    )

    print_success_message("RAG chain assembled and ready.")

    try:
        test_vector = llama_embeddings.embed_query(
            "Sanity check for embeddings.")
        print_info_message(
            f"Embedding model loaded successfully."
            f"Vector length = {len(test_vector)}"
        )
    except Exception as e:
        print_error_message(f"Failed to run embeddings: {e}")
        sys.exit(1)

    return rag_chain, vectorstore, text_splitter, llama_embeddings, llm
