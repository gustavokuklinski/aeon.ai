import os
import sys
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, UnstructuredMarkdownLoader, TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
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
    SYSTEM_RAG_PROMPT,
    LLM_N_CTX,
    LLM_TOP_P,
    LLM_TOP_K
)
from src.libs.messages import (
    print_error_message, print_info_message, print_success_message
)


def _load_initial_documents(input_dir_path: Path) -> list:
    """Loads documents from a specified input directory."""
    if not os.path.exists(input_dir_path):
        print_error_message(
            f"Directory '{input_dir_path}' not found. Please create it.")
        sys.exit(1)

    print_info_message(f"Loading initial documents...")
    documents = []
    documents.extend(DirectoryLoader(str(input_dir_path),
                     glob="**/*.md", loader_cls=UnstructuredMarkdownLoader).load())
    documents.extend(DirectoryLoader(str(input_dir_path),
                     glob="**/*.txt", loader_cls=TextLoader).load())
    for json_file in input_dir_path.glob("**/*.json"):
        documents.extend(JsonPlaintextLoader(str(json_file)).load())
    return documents


def _get_or_create_vectorstore(chroma_db_dir_path: Path, chunks: list, embeddings: LlamaCppEmbeddings) -> Chroma:
    """Loads an existing Chroma vector store or creates a new one with chunks."""
    batch_size = 32
    if chroma_db_dir_path.exists() and os.listdir(chroma_db_dir_path):
        print_info_message(
            f"Loading existing vector store...")
        vectorstore = Chroma(persist_directory=str(
            chroma_db_dir_path), embedding_function=embeddings)
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
        return vectorstore
    else:
        print_info_message(
            f"Vector store not found. Creating a new one at {chroma_db_dir_path}...")
        vectorstore = Chroma(persist_directory=str(
            chroma_db_dir_path), embedding_function=embeddings)
        if chunks:
            print_info_message(
                f"Ingesting {len(chunks)} chunks into new vector store...")
            for i, chunk in enumerate(chunks, start=1):
                try:
                    vectorstore.add_documents([chunk])
                    if i % 20 == 0 or i == len(chunks):
                        print_info_message(
                            f"Ingested chunks {i + 1} to {min(i + batch_size, len(chunks))}.")
                except Exception as e:
                    print_error_message(
                        f"Failed to ingest batch starting at index {i}: {e}")
            print_success_message("Initial document ingestion complete.")
        else:
            print_info_message(
                "No initial documents to ingest. Creating an empty vector store.")
        return vectorstore


def _initialize_models_and_chain(retriever, llm_model_path, system_prompt_template) -> tuple[LlamaCpp, RunnableParallel]:
    print_info_message(f"Loading LLM: {llm_model_path}")
    llm = LlamaCpp(
        model_path=llm_model_path,
        temperature=LLM_TEMPERATURE,
        top_p=LLM_TOP_P,
        top_k=LLM_TOP_K,
        n_ctx=LLM_N_CTX,
        stop=["<|im_end|>", "\nQUESTION:", "\nCONTEXT:","\nUSER:", "RESPONSE:"],
        verbose=False,
    )

    qa_prompt = PromptTemplate.from_template(system_prompt_template)
    
    retrieval_chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
    
    answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    rag_chain = retrieval_chain | RunnablePassthrough.assign(answer=answer_chain)

    print_success_message("RAG chain assembled and ready.")
    return llm, rag_chain


def ragSystem(conversation_memory_path: Path,
              chroma_db_dir_path: Path, is_new_session: bool):
    project_root = Path(__file__).parent.parent.parent
    input_dir_path = project_root / INPUT_DIR

    documents = _load_initial_documents(input_dir_path)
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
        verbose=False)

    try:
        test_vector = llama_embeddings.embed_query(
            "Sanity check for embeddings.")
        print_info_message(
            f"Embedding model loaded successfully. Vector length = {len(test_vector)}")
    except Exception as e:
        print_error_message(f"Failed to run embeddings: {e}")
        sys.exit(1)

    vectorstore = _get_or_create_vectorstore(
        chroma_db_dir_path, chunks, llama_embeddings)
    retriever = vectorstore.as_retriever()
    llm, rag_chain = _initialize_models_and_chain(
        retriever,
        LLM_MODEL,
        "<|im_start|>system\n"
        f"{SYSTEM_PROMPT}\n"
        f"{SYSTEM_RAG_PROMPT}"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        "CONTEXT:{context}\n"
        "QUESTION:{question}\n"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
        "RESPONSE:"
    )

    return rag_chain, vectorstore, text_splitter, llama_embeddings, llm
