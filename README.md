# cmem-plugin-template

## Requirements

- [cmemc](https://eccenca.com/go/cmemc)
- Python 3.9

## Installation

This repository contains a [copier version 5.1.0](https://copier.readthedocs.io/) template which can be used to bootstrap an eccenca Corporate Memory (CMEM) python plugin.
The following tools are needed (beside copier):

- [poetry](https://python-poetry.org/) with a python 3.9.x environment
- [task](https://taskfile.dev/)

Example with Python3 on Ubuntu:
```
 sudo sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
 python3 -m pip install --user pipx
 python3 -m pipx ensurepath
 pipx install 'copier==5.1.0'
 pipx inject copier "MarkupSafe<2.1.0"
 pipx install poetry
```

## Usage

```
copier gh:eccenca/cmem-plugin-template cmem-plugin-my
```

