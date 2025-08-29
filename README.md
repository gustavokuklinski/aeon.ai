# AEON
AEON is portable, private, and capable of operating fully offline (with the exception of web search). It democratizes access to powerful, dynamic AI capabilities for a wider audience, regardless of their hardware.

Know more about Aeon: [DOCS](https://github.com/gustavokuklinski/aeon.ai/blob/main/docs/)

## Stats
[![Aeon build](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml/badge.svg)](https://github.com/gustavokuklinski/aeon.ai/actions/workflows/python-app.yml)


## Installation

AEON uses Python with virtual environment and `git lfs` installed.

Use the script `./install.py` to set up your virtual environment and install all necessary pip dependencies.

```shell
/$ git lfs install
/$ git clone https://github.com/gustavokuklinski/aeon.ai.git

# Run check and install dependencies
/$ python3 ./install.py 

# Start AEON
/$ python3 ./aeon.py
```

Manual install (Linux)
```shell
/$ cd ./aeon.ai/
/aeon.ai $ python -m venv .venv
/aeon.ai $ source ./venv/bin/activate
/aeon.ai $ python install.py
/aeon.ai $ python aeon.py
```

To run on **Windows** check: [Windows setup](https://github.com/gustavokuklinski/aeon.ai/blob/main/docs/WINDOWS.md)


## Configuration

Edit `config.yml` to fit your needs. You must specify the **file paths** to your locally downloaded models and `prompts`


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=gustavokuklinski/aeon.ai&type=Date)](https://www.star-history.com/#gustavokuklinski/aeon.ai&Date)

### Tested on

| OS | CPU | GPU | RAM |
|:---|:---|:---|:---|
| Ubuntu 24.04.2 LTS | Intel i7 - 10510U | - | 16GB |
| Windows 11 Home Edition | Intel i7 - 10510U | - | 8GB |