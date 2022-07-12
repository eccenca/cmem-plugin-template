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
$ sudo sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
$ python3 -m pip install --user pipx
$ python3 -m pipx ensurepath
$ pipx install copier
$ pipx install poetry
$ pipx install cmem-cmemc
```

## Features

- [python / poetry](https://python-poetry.org/) project with [pylint](https://pylint.pycqa.org/), [pytest](https://www.pytest.org/), [flake8](https://flake8.pycqa.org/), [mypy](http://mypy-lang.org/), [bandit](https://bandit.readthedocs.io/) and [safety](https://pyup.io/safety/) integration
- local build plan with [task](https://taskfile.dev/)
- [github build plan](https://github.com/eccenca/cmem-plugin-template/tree/main/src/.github/workflows)
- [gitlab build plan](https://github.com/eccenca/cmem-plugin-template/blob/main/src/.gitlab-ci.yml)
- badges, junit XML files and coverage stat generation

## Usage

The following command will generate a new project for you:
```
$ copier gh:eccenca/cmem-plugin-template cmem-plugin-my
```

After that, you should initialize the repository:
```
$ cd cmem-plugin-my
$ git init
$ git add .
$ git commit -m "init"
```

Then you can run a test build:
```
$ task check build
```

Available tasks for your project can be listed like this:
```
$ task
task: Available tasks for this project:
* build:          Build tarball and a wheel package.
* check:          Run whole test suite.
* check:bandit:   Check source code with bandit.
* check:flake8:   Check source code with flake8.
* check:mypy:     Check source code with mypy.
* check:pylint:   Check source code with pylint.
* check:pytest:   Run pytest suite.
* check:safety:   Check source code with safety.
* clean:          Removes dist, *.pyc and some caches
* deploy: 		  Install plugin package in Corporate Memory
* poetry:init:    Initialze poetry env and add dev dependencies used in this taskfile.
* poetry:install: Install dependencies managed by Poetry.
* poetry:shell:   Open a poetry shell.
* poetry:update:  Update dependencies managed by Poetry to their newest versions.
* python:format:  Format Python files.
```

