<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon.png">

AEON is a simple, stateless Retrieval-Augmented Generation (RAG) chatbot designed to answer questions based on a provided set of Markdown (.md), Text (.txt), and JSON (.json) documents. It leverages local Large (or Small) Language Models (LLMs and SLMs) and embedding models all powered by Ollama. Chroma is used for its vector database.

The main focus is to be simple and lightweight to run on CPU with at least 8GB Ram and i3 processors, typically using models like *smollm2:135m*, *gemma3:270m* and *tinyllama* with *nomic-embed-text*.

### Summary
[Installation](#installation)<br />
[Setup LLM](#setup-llm)<br />
[Configuration](#configuration)<br />
[Start AEON](#start-aeon)<br />
[Data RAG](#data-rag)<br />
[AEON Chat command](#aeon-chat-command)<br />
[Web Chat Interface](#web-chat-interface)<br />
[Running on VPS](#running-on-vps)

## Installation
Install [Ollama](https://ollama.com/) on your machine first.

Use the script ```./aeon.sh``` to set your ```.venv``` in Python and install pip dependencies

```shell
$ chmod +x ./aeon.sh
$ ./aeon.sh
``` 

## Setup LLM
Pull the LLM you want from Ollama, recomended: ```gemma3:270m``` due lightweight and the embedding model: ```nomic-embed-text```

```bash
$ ollama pull nomic-embed-text
$ ollama pull gemma3:270m
```

## Configuration
Edit ```config.json``` to fit your needs

```json
{
  "llm_config": {
    "model": "gemma3:270m", <-- Choose your LLM
    "temperature": 0.2
  },
  "embedding_model": "nomic-embed-text",
  "system_prompt": "You are a helpful AI assistant.\n\nContext: {context}"

}
```

## Start AEON
Make sure you have all dependencies like: Ollama, python and dependencies installed on your machine and run:

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-1.png">

```shell
$ chmod +x ./aeon.sh
$ ./aeon.sh
``` 

## Data RAG
All data is stored in: ```/data/*``` 
  * ```/data/cerebrum``` Place your own Markdown, Text and JSON files. 
  * ```/data/synapse``` Chroma vector database

To use your own JSON files, follow the example in: ```/data/cerebrum/example.json``` :
```json
[
  {
    "query": "What is your name?", <-- Write your Query
    "context": "The AI assistant is asked its name, how it may be called", <-- What your query is about
    "answer": "Hello! My name is Aeon!" <-- Predicted response for training
  }
]
```

## AEON Chat command

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-terminal.png">

Command can be placed on chat
  * ```/ingest <path_to_file_or_directory>``` To insert new files or folders
  * ```/quit, /bye, /exit``` To close AEON

## Web Chat Interface

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-web.png">

Open your browser at: ```localhost:4303```

To upload your own files use: ```/ingest <path_to_file_or_directory>```
Valid formats: TXT, MD and JSON

## Running on VPS
Aeon can also be uploaded to a VPS processing data as a personal business AI.

Running on VPS:

```shell
$ git clone https://github.com/gustavokuklinski/aeon.ai.git
$ chmod +x ./aeon.sh
$ ./aeon.sh
```

Remember to setup your ```config.json``` and install (Ollama)[https://ollama.com]

To use locally with Ngrok ```$ ngrok http 4303```

### Tested on
| OS                 | CPU               | GPU | RAM  |
|--------------------|-------------------|-----|------|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | -   | 16GB |