# PowerShorter

A Python project initialized with `uv` and Jupyter support.

## Setup

This project uses `uv` for dependency management and virtual environment handling.

```bash
# Initialize the virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # For bash/zsh
# or
. .venv/bin/activate.fish  # For fish shell

# Install dependencies
uv pip install -r requirements.txt
```

To use _Power Shorter_, you need to install the device driver library, which communicates over the UART protocol. Download the appropriate `.whl` file from the [product provider's releases page](https://gitee.com/osr-tech/powershorter/releases) and install it as follows:

```bash
$ pip install ~/Downloads/power_shorter-1.0.2-py3-none-any.whl
Collecting pyserial (from power-shorter==1.0.2)
  Using cached pyserial-3.5-py2.py3-none-any.whl.metadata (1.6 kB)
Using cached pyserial-3.5-py2.py3-none-any.whl (90 kB)
Installing collected packages: pyserial, power-shorter
Successfully installed power-shorter-1.0.2 pyserial-3.5
```

## Running Jupyter

```bash
jupyter lab
# or
jupyter notebook
```
