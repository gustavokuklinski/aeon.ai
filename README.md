<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon.png" />

**AEON** is a simple, stateless Retrieval-Augmented Generation (**RAG**) chatbot designed to answer questions based on a provided set of Markdown (`.md`), Text (`.txt`), and JSON (`.json`) documents. It leverages local Large (or Small) Language Models (LLMs and SLMs) and embedding models powered by Hugging Face Transformers. **Chroma** is used for its vector database.

The main focus is to be simple and lightweight, capable of running on a **CPU with at least 8GB of RAM**. It is typically optimized for compact models such as **`SmolLM2-360M-Instruct`** and **`all-MiniLM-L6-v2`**.

### Summary

[Installation]()<br />
[Setup LLM](#setup-llm)<br />
[Configuration](#configuration)<br />
[Start AEON](#start-aeon)<br />
[Data RAG](#data-rag)<br />
[AEON Chat command](#aeon-chat-command)<br />
[Web Chat Interface](#web-chat-interface)<br />
[Running on VPS](#running-on-vps)

-----

## Installation

AEON uses Python and requires a virtual environment. Use the script `./aeon.py` to set up your virtual environment and install all necessary pip dependencies from `requirements.txt`.

```shell
$ python3 ./aeon.py
```

-----

## Setup LLM

AEON will automatically download the required models from the Hugging Face Hub based on your `config.yml` file and save into ```~/.cache/huggingface/hub/```. No manual download is required. Ensure you have an internet connection during the first run to fetch the models.

-----

## Configuration

Edit `config.yml` to fit your needs. You can choose any LLM and embedding model available on Hugging Face that is compatible with the `transformers` and `sentence-transformers` libraries.

```yaml
llm_config:
  model: HuggingFaceTB/SmolLM2-360M-Instruct
  temperature: 0.5
img_config:
  model: segmind/tiny-sd
  width: 512
  height: 512
  hardware: cpu
  negative_prompt: low quality, deformed, blurry, watermark, text
embedding_model: sentence-transformers/all-MiniLM-L6-v2
system_prompt: "You are a helpful AI assistant. Your name is Aeon.\nContext: {context}"
```

-----

## Start AEON

Make sure you have all dependencies installed and then run the launcher script. The script will handle all setup and model loading for you.

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-1.png" />

```shell
$ python3 ./aeon.py
```

-----

## Data RAG

All data is stored in the `/data/` directory:

  * `/data/cerebrum`: Place your own Markdown, Text, and JSON files here. These are the documents AEON will use as its knowledge base.
  * `/data/synapse`: This directory stores the Chroma vector database, which is automatically created or loaded by AEON.

To use your own JSON files, follow the example in `/data/cerebrum/example.json`:

```json
[
  {
    "query": "What is your name?", <-- Write your Query
    "context": "The AI assistant is asked its name, how it may be called", <-- What your query is about
    "answer": "Hello! My name is Aeon!" <-- Predicted response for training
  }
]
```

-----

## AEON Chat command

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-terminal.png"/>

Commands can be placed directly in the chat interface:

  * `/image <prompt_to_generate_image>`: Use Stable Diffusion Model to generate images.
  * `/ingest <path_to_file_or_directory>`: To insert new files or folders into the knowledge base.
  * `/quit`, `/bye`, `/exit`: To close AEON.

-----

## Web Chat Interface

<img src="https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/web/assets/img/aeon-web.png" />

Open your browser at `localhost:4303` to access the web interface.

  * `/image <prompt_to_generate_image>`: Use Stable Diffusion Model to generate images.

-----

## Running on VPS

AEON can be run on a VPS to function as a personal or business AI.

To set up AEON on a VPS:

```shell
$ git clone https://github.com/gustavokuklinski/aeon.ai.git
$ python3 ./aeon.py
```

Remember to configure your `config.yml` with the desired Hugging Face models.

To access your VPS instance locally using Ngrok:

```shell
$ ngrok http 4303
```

-----

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | - | 16GB |