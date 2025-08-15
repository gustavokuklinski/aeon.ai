# core/rag_setup.py
import os
import sys
from pathlib import Path

# Langchain modules
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings  # <-- Revert to this
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain

# Core modules
from core.config import (
    LLM_MODEL, LLM_TEMPERATURE, EMBEDDING_MODEL,
    INPUT_DIR, CHROMA_DB_DIR, SYSTEM_PROMPT
)
from core.loaders import JsonPlaintextLoader

def initialize_rag_system():
    """
    Initializes and returns a complete RAG system.
    Returns: A tuple containing (rag_chain, vectorstore, text_splitter, ollama_embeddings).
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
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)

    # 3. Generate Embeddings and Store in a Vector Database
    # Use the LangChain OllamaEmbeddings class
    ollama_embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if not chroma_db_dir_path.exists() or not os.listdir(chroma_db_dir_path):
        print(f"Vector store not found. Creating new one at {chroma_db_dir_path}...")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=ollama_embeddings,
            persist_directory=str(chroma_db_dir_path)
        )
    else:
        print(f"Loading existing vector store from {chroma_db_dir_path}...")
        vectorstore = Chroma(
            persist_directory=str(chroma_db_dir_path),
            embedding_function=ollama_embeddings
        )

    retriever = vectorstore.as_retriever()

    # 4. Set up the LLM and Prompt Templates
    llm = ChatOllama(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    qa_system_prompt = SYSTEM_PROMPT
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            ("human", "{input}"),
        ]
    )

    # 5. Assemble the Stateless RAG Chain
    document_combiner = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = (
        {"context": retriever, "input": RunnablePassthrough()}
        | document_combiner
    )
    print("RAG chain assembled and ready.")

    return rag_chain, vectorstore, text_splitter, ollama_embeddings