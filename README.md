# AEON

**AEON** is a simple, stateless Retrieval-Augmented Generation (**RAG**) chatbot designed to answer questions based on a provided set of Markdown (`.md`), Text (`.txt`), and JSON (`.json`) documents. It leverages local Large (or Small) Language Models (**LLMs** and **SLMs**) in the **GGUF format** and local image generation models in the **SafeTensor format**.

The main focus is to be simple and lightweight, capable of running on a **CPU with at least 8GB of RAM** locally.

## Stats
[![Aeon build](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml/badge.svg)](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml)

### Summary

[Installation](#installation)<br />
[Setup Local Models](#setup-local-models)<br />
[Configuration](#configuration)<br />
[Start AEON](#start-aeon)<br />
[Data RAG](#data-rag)<br />
[AEON Commands](#aeon-commands)<br />

-----

## Installation

AEON uses Python and requires a virtual environment. Use the script `./aeon.py` to set up your virtual environment and install all necessary pip dependencies from `requirements.txt`.

Before cloning, make sure you have GIT LFS installed

```shell
$ git lfs install
$ git clone https://github.com/gustavokuklinski/aeon.ai.git

# Run check and install dependencies
$ python3 ./install.py 

# Start AEON
$ python3 ./aeon.py
```
-----

To run on **Windows** check: [Windows setup](https://github.com/gustavokuklinski/aeon.ai/blob/main/docs/WINDOWS.md)

## Setup Local Models

AEON is designed to run entirely locally, meaning all models must be downloaded beforehand. It does **not** automatically download models from the internet.

1.  **Download LLM (GGUF file):** Choose a GGUF model from a local-first repository like TheBloke on Hugging Face. Place the downloaded `.gguf` file in the `./llm/` directory.
2.  **Download Embedding Model (GGUF file):** Download a GGUF-compatible embedding model. Place the `.gguf` file in the `./llm/` directory.
3.  **Download Image Generation Model:** Clone a `text-to-image` model in the `./llm/image/` directory.
3.  **Download Image Visualization Model:** Clone a `image-to-text` model in the `./llm/vlm/` directory.

You can use GGUF downloaded models at:
(HuggingFace.co)[https://huggingface.co/models?search=gguf]

For image generation/visualization, download and/or clone all SafeTensors repository with `git lfs`

-----

## Configuration

Edit `config.yml` to fit your needs. You must specify the **file paths** to your locally downloaded models and `prompts`

-----

## Start AEON

Make sure you have all dependencies installed and then run the launcher script. The script will handle all setup and model loading for you. **No internet connection is required after the initial setup.**

```shell
$ python3 ./aeon.py
```

-----

## Data RAG:

All data is stored in the `/data/` directory:

  * `/data/memory`: This directory stores the Chroma vector database, which is automatically created or loaded by AEON as store the conversarion JSON.
  * `/data/cerebrum/system`: Basic prompting for AI assistence.
  * `/data/cerebrum/temp`: Place your own Markdown, Text, and JSON files here. These are the documents AEON will use as its knowledge base.
  * `/data/output/backup`: Command `/zip` timestamped conversation backups.

-----

## AEON Commands

Commands can be placed directly in the chat interface:

* `/help`: Show list of commands.
* `/paths`: Display directory paths.
* `/new`: Create a new conversation.
* `/list`: List all conversations.
* `/open <NUMBER>`: Open a conversation.
* `/load <NUMBER>`: Ingest a previous conversation.
* `/ingest <PATH> | <PATH><filename.json,txt,md>`: Add documents to RAG.
* `/zip`: Backup contents to a timestamped zip file.
* `/search <TERM>`: Make a web search with DuckDuckGo.
* `/image <PROMPT>`: Generate an image.
* `/view <PATH><filename.png, jpg> <PROMPT>`: Visualize an image.
* `/restart`: Restart the application.
* `/quit`, `/exit`, `/bye`: End the conversation.

-----

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gustavokuklinski/aeon.ai&type=Date)](https://www.star-history.com/#gustavokuklinski/aeon.ai&Date)

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | - | 16GB |