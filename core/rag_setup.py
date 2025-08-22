# core/rag_setup.py
import os
import sys
from pathlib import Path

# Langchain modules
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import PromptTemplate

# New LlamaCpp and LlamaCpp Embeddings imports
from langchain_community.llms import LlamaCpp
from langchain_community.embeddings import LlamaCppEmbeddings

# Core modules
from core.config import (
    LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL,
    INPUT_DIR, CHROMA_DB_DIR, SYSTEM_PROMPT, LLM_N_CTX
)
from core.loaders import JsonPlaintextLoader

def initialize_rag_system():
    """
    Initializes and returns a complete RAG system using LlamaCpp.
    Returns: A tuple containing (rag_chain, vectorstore, text_splitter, llama_embeddings).
    """
    # Adjust paths to be relative to the project root
    project_root = Path(__file__).parent.parent
    input_dir_path = project_root / INPUT_DIR
    chroma_db_dir_path = project_root / CHROMA_DB_DIR
    
    # 1. Load Initial Documents
    if not os.path.exists(input_dir_path):
        print(f"Error: Directory '{input_dir_path}' not found. Please create it.")
        sys.exit(1)

    print(f"Loading initial documents from: {input_dir_path}")
    documents = []
    md_loader = DirectoryLoader(str(input_dir_path), glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents.extend(md_loader.load())
    txt_loader = DirectoryLoader(str(input_dir_path), glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    json_files = list(input_dir_path.glob("**/*.json"))
    for json_file in json_files:
        json_loader = JsonPlaintextLoader(str(json_file))
        documents.extend(json_loader.load())

    # 2. Split Documents into Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Generate Embeddings and Store in a Vector Database
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    llama_embeddings = LlamaCppEmbeddings(
        model_path=EMBEDDING_MODEL,
        n_ctx=2048,
        verbose=False
    )
    
    batch_size = 32
    
    if not chroma_db_dir_path.exists() or not os.listdir(chroma_db_dir_path):
        # First-time load: Use a single batch
        if not chunks:
            print(f"No initial documents found. Creating an empty vector store at {chroma_db_dir_path}...")
            vectorstore = Chroma(
                persist_directory=str(chroma_db_dir_path),
                embedding_function=llama_embeddings
            )
        else:
            print(f"Vector store not found. Creating a new one with {len(chunks)} chunks at {chroma_db_dir_path}...")
            # Use a loop to add documents in batches
            vectorstore = Chroma(
                persist_directory=str(chroma_db_dir_path),
                embedding_function=llama_embeddings
            )
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                try:
                    vectorstore.add_documents(batch)
                    print(f"[INFO] Ingested chunks {i+1} to {min(i + batch_size, len(chunks))}.")
                except Exception as e:
                    print(f"[ERROR] Failed to ingest batch starting at index {i}: {e}")
            print("Initial document ingestion complete.")
    else:
        # Subsequent loads: Use the one-by-one method for added documents
        print(f"Loading existing vector store from {chroma_db_dir_path}...")
        vectorstore = Chroma(
            persist_directory=str(chroma_db_dir_path),
            embedding_function=llama_embeddings
        )
        if chunks:
            print(f"Adding {len(chunks)} new chunks to the existing vector store.")
            # Use a loop to add documents one-by-one to prevent decode errors
            for i, chunk in enumerate(chunks, start=1):
                try:
                    vectorstore.add_documents([chunk])
                    if i % 20 == 0 or i == len(chunks):
                        print(f"[INFO] Added {i}/{len(chunks)} chunks.")
                except Exception as e:
                    print(f"[ERROR] Failed on chunk {i}: {e}")

    retriever = vectorstore.as_retriever()

    # 4. Set up the LLM and Prompt Templates
    print(f"Loading LLM: {LLM_MODEL}")
    # Use LlamaCpp for GGUF LLMs
    llm = LlamaCpp(
        model_path=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        n_ctx=LLM_N_CTX,
        chat_format="gemma",
        stop=["<end_of_turn>"],
        verbose=False
    )

    qa_prompt = PromptTemplate.from_template(
        "<start_of_turn>user\n"
        f"{SYSTEM_PROMPT}\n"  # System prompt is included in the user turn
        "Context: {context}\n\n"
        "Question: {input}<end_of_turn>\n"
        "<start_of_turn>model\n"
    )

    # 5. Assemble the Stateless RAG Chain
    document_combiner = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = (
        {"context": retriever, "input": RunnablePassthrough()}
        | document_combiner
    )
    print("RAG chain assembled and ready.")

    try:
        test_vector = llama_embeddings.embed_query("Sanity check for embeddings.")
        print(f"[INFO] Embedding model loaded successfully. Vector length = {len(test_vector)}")
    except Exception as e:
        print(f"[ERROR] Failed to run embeddings: {e}")
        sys.exit(1)

    return rag_chain, vectorstore, text_splitter, llama_embeddings