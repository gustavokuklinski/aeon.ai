# AEON

**AEON** is a simple, stateless Retrieval-Augmented Generation (**RAG**) chatbot designed to answer questions based on a provided set of Markdown (`.md`), Text (`.txt`), and JSON (`.json`) documents. It leverages local Large (or Small) Language Models (**LLMs** and **SLMs**) in the **GGUF format** and local image generation models in the **SafeTensor format**.

The main focus is to be simple and lightweight, capable of running on a **CPU with at least 8GB of RAM** locally.

## Stats
[![Aeon build](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml/badge.svg)](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml)


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

-----

## Configuration

Edit `config.yml` to fit your needs. You must specify the **file paths** to your locally downloaded models and `prompts`

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
* `/quit`, `/exit`, `/bye`: End the conversation.

-----

## Plugins

* `/hello <PROMPT>`: Simple Hello World plugin
* `/image <PROMPT>`: Generate an image with (segmind/tiny-sd)[https://huggingface.co/segmind/tiny-sd]
* `/view <PATH><filename.png, jpg> <PROMPT>`: Visualize an image. (HuggingFaceTB/SmolVLM-256M-Instruct)[https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct]

All models are stored locally.

-----

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gustavokuklinski/aeon.ai&type=Date)](https://www.star-history.com/#gustavokuklinski/aeon.ai&Date)

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | - | 16GB |