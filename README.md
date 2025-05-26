```
 █████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║
███████║█████╗  ██║   ██║██╔██╗ ██║
██╔══██║██╔══╝  ██║   ██║██║╚██╗██║
██║  ██║███████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
```

AEON is a simple, stateless Retrieval-Augmented Generation (RAG) chatbot designed to answer questions based on a provided set of Markdown (.md), Text (.txt), and JSON (.json) documents. It leverages local Large Language Models (LLMs) and embedding models all powered by Ollama. Chroma is used for its vector database.

The main focus is to be simple and lightweight to run on CPU with at least 8GB Ram and i3 processors, typically using models like *smollm2:135m* and *tinyllama* with *nomic-embed-text*.

## Instalation
Install [Ollama](https://ollama.com/) on your machine first

Use the script ```./install.sh``` to set your ```.venv``` in Python and install pip dependencies

```shell
$ chmod +x ./install.sh
$ ./install.sh
``` 

## Configuration
```config.json``` to setup Aeon

```json
{
  "llm_config": {
    "model": "tinyllama", <-- Choose your LLM
    "temperature": 0.2
  },
  "embedding_model": "nomic-embed-text",
  "system_prompt": "Answer the user's question, but only use the information you have the context. If you can't find the answer in the context, say you don't know.\n\nContext: {context}"

}
```

## Start AEON
Make sure you have all dependencies like: ollama, python and dependencies installed on your machine and run:

```shell
$ chmod +x ./aeon.sh
$ ./aeon.sh
``` 

Running Aeon question mode:
```shell
$ ./aeon.sh -q "<your_input>"
``` 

Example: 
```shell
$ ./aeon.sh -q "What is 1+1?"
$ [AEON]: 1 + 1 is equals 2
$ 
```

## Data - RAG
All data is stored in: ```/data/*``` 
  * ```/data/cerebrum``` Place your own Markdown, Text and JSON files. 
  * ```/data/synapse``` Chroma vector database

## AEON Chat command
Command can be placed on chat
  * ```/ingest <path_to_file_or_directory>``` To insert new files or folders
  * ```/quit, /bye, /exit``` To close AEON
