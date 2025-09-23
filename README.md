![alt text](https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/docs/assets/img/aeon-logo.png)

[![Aeon build](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml/badge.svg)](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml)

AEON is portable, private, and capable of operating fully offline (with the exception of web search). It democratizes access to powerful, dynamic AI capabilities for a wider audience, regardless of their hardware.

## Using Docker
Aeon in a Docker container allows real-time file updates.
You can customize and backup chats.

**Build the Docker image**
```bash
docker build -t aeon .
```

**Run the docker image**
```bash
docker run -it --rm -p 7860:7860 -v "$(pwd):/app" aeon
```

Docker image params:
* `-it` : Runs the container in interactive mode, allowing you to use the menu.
* `--rm` : Automatically removes the container when you exit.
* `-p 7860:7860` : Maps the container's port 7860 to your host machine's port 7860, allowing you to access the web interface.
* `-v "$(pwd):/app"` : This is the bind mount. It links your project folder on your machine directly to the /app folder in the container. Any changes you save on your local machine will be immediately available to the Python script running inside the container.
* `aeon` : The name of the Docker image you built.

## Manual Installation
If you want to tweak everything!

AEON uses Python with virtual environment and `git lfs` installed. 

Use the script `./install.py` to set up your virtual environment and install all necessary pip dependencies.

```shell
/$ git lfs install

# With plugins
/$ git clone --recurse-submodules https://github.com/gustavokuklinski/aeon.ai.git

# Without plugins
/$ git clone https://github.com/gustavokuklinski/aeon.ai.git
```

```shell
# Create .venv
/$ python -m venv .venv

# Start virtual env
/$ source .venv/bin/activate

# Run check and install dependencies
/$ python3 scripts/install.py 

# Start AEON
/$ python3 aeon.py
```

To run on **Windows** check: [Windows setup](https://github.com/gustavokuklinski/aeon.ai/blob/main/docs/assets/md/WINDOWS.md)


## Global Configuration

Edit `config.yml` to fit your needs. You must specify the **file paths** to your locally use models and `prompts`.

**User configuration**
`/data/chat/<CHAT_ID>/config.yml` sets the current chat configuration.

Example config.yml file:

```yaml
llm_config:
  model: ./data/model/aeon-360M-Q8_0.gguf
  temperature: 0.5
  n_ctx: 4096
  top_k: 40
  top_p: 0.8
  llm_prompt: >
    You are Aeon, a friendly, helpful, and conversational AI assistant.\nCONTEXT: {context}
  llm_rag_prompt: >
    "Your responses should be in plain, natural language ONLY. Determine the nature of the user's QUESTION. If the question is factual, follow this process: 1. Scan the CONTEXT for all relevant facts. 2. Combine these facts to form a single, comprehensive answer. 3. If context is unavailable, state: 'I don't know about it. Can we /search?'. If the question is conversational or non-factual, respond naturally and conversationally, without referring to the CONTEXT. Do not echo the user's QUESTION or the CONTEXT.
emb_config:
  model: ./data/model/all-MiniLM-L6-v2-Q8_0.gguf
  n_ctx: 256
  chunk_size: 20
  chunk_overlap: 0

load_plugins:
  - hello-world
  - aeon-speak
  - aeon-smolvlm-256m-instruct
  - aeon-tiny-sd
```

Know more about AeonLLM: [Finetune Aeon](https://github.com/gustavokuklinski/aeon.llm)
Know more about Aeon: [DOCS](https://github.com/gustavokuklinski/aeon.ai/blob/main/docs/assets/md)

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7-10510U | Intel CometLake-U GT2 | 16GB |
| Windows 11 Home Edition | Intel i7-10510U | Intel CometLake-U GT2 | 8GB |


[![Star History Chart](https://api.star-history.com/svg?repos=gustavokuklinski/aeon.ai&type=Date)](https://www.star-history.com/#gustavokuklinski/aeon.ai&Date)