# AEON

**AEON** is a simple, stateless Retrieval-Augmented Generation (**RAG**) chatbot designed to answer questions based on a provided set of Markdown (`.md`), Text (`.txt`), and JSON (`.json`) documents. It leverages local Large (or Small) Language Models (**LLMs** and **SLMs**) in the **GGUF format** and local image generation models in the **SafeTensor format**. **Chroma** is used for its vector database.

The main focus is to be simple and lightweight, capable of running on a **CPU with at least 8GB of RAM**. It is typically optimized for compact GGUF models and lightweight image generators.

### Summary

[Installation](#installation)<br />
[Setup Local Models](#setup-local-models)<br />
[Using Other Models](#using-other-models)<br />
[Configuration](#configuration)<br />
[Start AEON](#start-aeon)<br />
[Data RAG](#data-rag)<br />
[AEON Chat Command](#aeon-chat-command)<br />
[Web Chat Interface](#web-chat-interface)<br />
[AEON Image Generator](#aeon-image-generator)<br />
[Running on VPS](#running-on-vps)<br />
[Acknowledgements](#acknowledgements)

-----

## Installation

AEON uses Python and requires a virtual environment. Use the script `./aeon.py` to set up your virtual environment and install all necessary pip dependencies from `requirements.txt`.

Before cloning, make sure you have GIT LFS installed

```shell
$ git lfs install
$ git clone https://github.com/gustavokuklinski/aeon.ai.git
$ python3 ./aeon.py
```

-----

## Setup Local Models

AEON is designed to run entirely locally, meaning all models must be downloaded beforehand. It does **not** automatically download models from the internet.

1.  **Download LLM (GGUF file):** Choose a GGUF model from a local-first repository like TheBloke on Hugging Face. Place the downloaded `.gguf` file in the `./llm/` directory.

2.  **Download Embedding Model (GGUF file):** Download a GGUF-compatible embedding model. Place the `.gguf` file in the `./llm/` directory.

3.  **Download Image Generation Model:** Clone a `text-to-image` model in the `./llm/image/` directory.

-----

## Using other models

Cou can use GGUF downloaded models at:
(HuggingFace.co)[https://huggingface.co/models?search=gguf]

For image generation, download clone all repository with `git lfs`

_Smallest_
(tiny-sd)[https://huggingface.co/segmind/tiny-sd] 
(openjourney)[https://huggingface.co/prompthero/openjourney] 

-----

## Configuration

Edit `config.yml` to fit your needs. You must specify the **file paths** to your locally downloaded models.

```yaml
llm_config:
  model: ./llm/gemma-3-270-it-Q8_0.gguf
  temperature: 0.5
img_config:
  model: ./llm/image/tiny-sd
  width: 512
  height: 512
  hardware: cpu
  negative_prompt: low quality, deformed, blurry, watermark, text
embedding_model: ./llm/nomic-embed-text-v1.5.Q8_0.gguf
system_prompt: "You are a helpful AI assistant. Your name is Aeon.\nContext: {context}"
```

-----

## Start AEON

Make sure you have all dependencies installed and then run the launcher script. The script will handle all setup and model loading for you. **No internet connection is required after the initial setup.**

```shell
$ python3 ./aeon.py
```

-----

## Data RAG

All data is stored in the `/data/` directory:

  * `/data/cerebrum/system`: Basic prompting for AI assistence.
  * `/data/cerebrum/temp`: Place your own Markdown, Text, and JSON files here. These are the documents AEON will use as its knowledge base.
  * `/data/cerebrum/memory`: This directory stores the Chroma vector database, which is automatically created or loaded by AEON as store the conversarion JSON.

To use your own JSON files, follow the example in `/data/cerebrum/temp/example.json`:

```json
[
  {
    "query": "What is your name?",
    "context": "The AI assistant is asked its name, how it may be called",
    "answer": "Hello! My name is Aeon!"
  }
]
```

-----

## AEON Chat Command

Commands can be placed directly in the chat interface:

  * `/image <prompt_to_generate_image>`: Use the local Stable Diffusion model to generate images.
  * `/ingest <path_to_file_or_directory>`: To insert new files or folders into the knowledge base.
  * `/quit`, `/bye`, `/exit`: To close AEON.

-----

## Web Chat Interface

Open your browser at `localhost:4303` to access the web interface.

-----

## AEON Image Generator

The image generator uses a local Stable Diffusion model.

To use in the terminal:

  * `/image <prompt_to_generate_image>`: Use the local Stable Diffusion model to generate images.

All images are stored in `/data/output`. The web endpoint for images is `/images/<filename>.png`.

-----

## Running on VPS

AEON can be run on a VPS to function as a personal or business AI.

To set up AEON on a VPS:

```shell
$ git clone https://github.com/gustavokuklinski/aeon.ai.git
$ python3 ./aeon.py
```

Remember to configure your `config.yml` with the correct local paths to your GGUF and SafeTensor models.

To access your VPS instance locally using Ngrok:

```shell
$ ngrok http 4303
```
-----
## Acknowledgements

**LLMs**

```tex
@article{gemma_2025,
    title={Gemma 3},
    url={https://arxiv.org/abs/2503.19786},
    publisher={Google DeepMind},
    author={Gemma Team},
    year={2025}
}
```

```tex
@misc{nussbaum2024nomic,
      title={Nomic Embed: Training a Reproducible Long Context Text Embedder}, 
      author={Zach Nussbaum and John X. Morris and Brandon Duderstadt and Andriy Mulyar},
      year={2024},
      eprint={2402.01613},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

**Images**

(tiny-sd)[https://huggingface.co/segmind/tiny-sd]

-----

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | - | 16GB |