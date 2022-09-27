---
orphan: true
---

# Installation

Botafar library should work at least on Windows, Mac and Linux (tested on Debian/Ubuntu/Raspberry Pi OS).

> **NOTE:** every command below starts with a word `python`. You might need to replace it with `python3` (Windows WSL/Mac/Linux) or `py` (Windows) depending on your operating system and how you have Python installed.

## Checking Python version

To work with the library you should have [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) version 3.7 or later installed.

You can check if you have Python installed and it's version with:

```
python --version
```

(Remember to check also `python3 --version` and `py --version` if the command above fails)

If you do not have Python installed or it is too old version, you can install it from [python.org](https://www.python.org/downloads/) or use google for finding other instructions.

## Installing botafar library

Most likely your Python came with pip package installer. Then the installation of botafar library should work with:

```
python -m pip install botafar
```

If the command fails, check instructions on [installing pip](https://pip.pypa.io/en/stable/installation/).

(Most likely simpler `pip install botafar` would have worked as well as seen in the [quickstart guide](quickstart.md), but the commands above specify the Python installation as well, which can help with some rare error cases)

Verify working botafar installation with:

```
python -m botafar --version
```

## Updating botafar library

To update existing botafar installation, run:

```
python -m pip install --upgrade botafar
```