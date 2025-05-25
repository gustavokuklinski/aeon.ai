 █████╗ ███████╗ ██████╗ ███╗   ██╗
██╔══██╗██╔════╝██╔═══██╗████╗  ██║
███████║█████╗  ██║   ██║██╔██╗ ██║
██╔══██║██╔══╝  ██║   ██║██║╚██╗██║
██║  ██║███████╗╚██████╔╝██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝

AEON is a simple, stateless Retrieval-Augmented Generation (RAG) chatbot designed to answer questions based on a provided set of Markdown (.md), Text (.txt), and JSON (.json) documents. It leverages local Large Language Models (LLMs), embedding models, and a Vision LLM for image understanding, all powered by Ollama. Chroma is used for its vector database.

The main focus is to be simple and lightweight to run on CPU with at least 8GB Ram and i3 processors, typically using models like *smollm2:135m*,*gemma3:3b (To generate images)*, *nomic-embed-text*, and *moondream*.

## Instalation

Use the ```./install.sh``` to set your ```.venv``` in Python and all the pip dependencies

```shell
$ chmod +x ./install.sh
$ ./install.sh
``` 

```config.json``` to setup Aeon

```json
{
  "llm_config": {
    "model": "tinyllama", <-- Choose your LLM
    "temperature": 0.2
  },
  "vision_model": "moondream", <-- Choose your VLM (Vision LLM)
  "embedding_model": "nomic-embed-text",
  "ollama_url_endpoint": "http://localhost:11434/api/generate"
}
```

Make sure you have all dependencies like: ollama, python and dependencies installed on your machine and run:

```shell
$ chmod +x ./aeon.sh
$ ./aeon.sh
``` 

## Data - RAG
All data is stored in: ```/data/*``` 
  * ```/data/cerebrum``` Place your own Markdown files. 
  * ```/data/output``` AEON response to ```/draw red circle``` (NOTE: Not all models will generate good results)
  * ```/data/synapse``` Chroma vector database