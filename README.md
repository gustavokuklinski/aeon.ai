![alt text](https://raw.githubusercontent.com/gustavokuklinski/aeon.ai/refs/heads/main/docs/assets/img/aeon-logo.png)

<div align="center" style="line-height: 1;">


<a href="https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml" target="_blank" style="margin: 2px;">
    <img src="https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml/badge.svg" style="display: inline-block; vertical-align: middle;"/>
</a>

<a href="https://huggingface.co/spaces/gustavokuklinski/aeon-eval" target="_blank" style="margin: 2px;">
    <img alt="Chat" src="https://img.shields.io/badge/🤖 Chat-Chat Aeon Test-536af5?color=ff0000&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
</a>

<a href="https://huggingface.co/gustavokuklinski/aeon" target="_blank" style="margin: 2px;">
    <img alt="Hugging Face" src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Aeon.ai-ffc107?color=ffc107&logoColor=white" style="display: inline-block; vertical-align: middle;"/>
</a>

</div>

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

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7-10510U | Intel CometLake-U GT2 | 16GB |
| Windows 11 Home Edition | Intel i7-10510U | Intel CometLake-U GT2 | 8GB |


[![Star History Chart](https://api.star-history.com/svg?repos=gustavokuklinski/aeon.ai&type=Date)](https://www.star-history.com/#gustavokuklinski/aeon.ai&Date)