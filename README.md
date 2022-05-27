# cmem-plugin-template

## Requirements and Installation

This repository contains a [copier](https://copier.readthedocs.io/) template, which can be used to bootstrap an eccenca Corporate Memory python plugin.

The following tools are needed:

- Python 3.9
- [copier](https://copier.readthedocs.io/) (>= v6) for project template rendering
- [poetry](https://python-poetry.org/) (>= v1.1) for packaging and dependency managing
- [task](https://taskfile.dev/) (>= v3) for build task running (make sure to follow the installation instructions to avoid confusion with taskwarrior)
- [cmemc](https://eccenca.com/go/cmemc) (>= v22.1) for interacting with eccenca Corporate Memory

Example installation of requirements on Ubuntu (using [pipx](https://pypa.github.io/pipx/) to install the python tools)

```
sudo sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install copier
pipx install poetry
pipx install cmem-cmemc
```

## Usage

```
copier gh:eccenca/cmem-plugin-template cmem-plugin-my
```

