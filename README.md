# cmem-plugin-template

[![workflow][build-shield]][github-actions] [![copier][copier-shield]][copier] [![eccenca Corporate Memory][cmem-shield]][cmem] ![python-shield]

This repository contains a [copier](https://copier.readthedocs.io/) template.

You can use it to bootstrap an [eccenca Corporate Memory](https://documentation.eccenca.com) [python plugin](https://documentation.eccenca.com/latest/develop/python-plugins/).

## Features

- [python / poetry](https://python-poetry.org/) project with [pylint](https://pylint.pycqa.org/), [pytest](https://www.pytest.org/), [flake8](https://flake8.pycqa.org/), [mypy](http://mypy-lang.org/), [bandit](https://bandit.readthedocs.io/), [memray](https://bloomberg.github.io/memray/) and [safety](https://pyup.io/safety/) integration
- local build plan with [task](https://taskfile.dev/)
- [github build plan](https://github.com/eccenca/cmem-plugin-template/tree/main/src/.github/workflows)
- [gitlab build plan](https://github.com/eccenca/cmem-plugin-template/blob/main/src/.gitlab-ci.yml)
- badges, junit XML files and coverage stat generation

## Setup and Usage

### Project Initialization

The following command will create a new project directory:
```shell-session
$ copier gh:eccenca/cmem-plugin-template cmem-plugin-my
```

After that, you can initialize the repository and install git hooks:
```shell-session
$ cd cmem-plugin-my
$ git init
$ git add .
$ git commit -m "init"
$ pre-commit install
```

Then you can run the local test suite an build a first deployment artifact:
```shell-session
$ task check build
```

### Project Update

From time to time, this template will be upgraded, so you can update your repository as well:
```shell-session
$ copier update
```

Please have a look at the [copier documentation](https://copier.readthedocs.io/en/stable/updating/).

### Other Tasks

Available tasks for your project can be listed like this:
```shell-session
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
* poetry:install: Install dependencies managed by Poetry.
* poetry:shell:   Open a poetry shell.
* poetry:update:  Update dependencies managed by Poetry to their newest versions.
* python:format:  Format Python files.
```

You can extend this task lisk by creating a file `TaskfileCustom.yaml` in your repository root:

```shell-session
$ cat TaskfileCustom.yaml
---
version: '3'

tasks:

  ttt:
    desc: just a test
    cmds:
      - task --list
```


### Setup Integration Tests

This template uses pytest for testing.
Testing your plugin is crucial and should be done locally and integrated with eccenca Corporate Memory.

In order to setup access to a Corporate Memory deployment, you need to provide correct environment variables.
Without these variables, only standalone tests can be executed (see `1 skipped`):

```shell-session
$ task check:pytest
...
... ===== 3 passed, 1 skipped in 0.09s =====
```

By giving the correct [cmemc](https://eccenca.com/go/cmemc) [environment variables](https://documentation.eccenca.com/22.1/automate/cmemc-command-line-interface/installation-and-configuration/file-based-configuration/#configuration-variables), your plugin can be tested in an integrated way:

```shell-session
$ export CMEM_BASE_URI="https://cmem.example.org"
$ export OAUTH_CLIENT_ID="cmem-service-account"
$ export OAUTH_CLIENT_SECRET="..."
$ export OAUTH_GRANT_TYPE="client_credentials"
$ task check:pytest
...
... ===== 4 passed in 1.71s =====

```

You can also add these variables to the `.env` file in your repository root (just make sure to never commit this file).

```shell-session
$ cat .env
CMEM_BASE_URI="https://cmem.example.org"
OAUTH_CLIENT_ID="cmem-service-account"
OAUTH_CLIENT_SECRET="..."
OAUTH_GRANT_TYPE="client_credentials"
```

### Setup Build Plan

The gitlab workflow / github action pipelines need the same environment variables as secrets:

- For github, go to Settings > Secret > Actions > [New Repository Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- For gitlab, go to Settings > CI/CD > Variables (Expand) > [Add Variable (protected, masked, all environments)](https://docs.gitlab.com/ee/ci/variables/)

Example github pipelines can be seen [here](https://github.com/eccenca/cmem-plugin-kafka/actions) and [here](https://github.com/eccenca/cmem-plugin-graphql/actions).

In addition to the eccenca Corporate Memory credential secrets, a `PYPI_TOKEN` secret can be set in order to use the `publish` task/workflow.

### Install Local Requirements

The following tools are needed for local task execution:

- Python 3.9
- [copier](https://copier.readthedocs.io/) (>= v6) for project template rendering
- [poetry](https://python-poetry.org/) (>= v1.1) for packaging and dependency managing (+ [dynamic versioning plugin](https://github.com/mtkennerly/poetry-dynamic-versioning))
- [pre-commit](https://pre-commit.com/) (>= v2.20) - managing and maintaining pre-commit hooks
- [task](https://taskfile.dev/) (>= v3) for build task running (make sure to follow the installation instructions to avoid confusion with taskwarrior)
- [cmemc](https://eccenca.com/go/cmemc) (>= v22.1) for interacting with eccenca Corporate Memory

Example installation of the requirements with [pipx](https://pypa.github.io/pipx/) on Ubuntu:

```
$ sudo sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
$ python3 -m pip install --user pipx
$ python3 -m pipx ensurepath
$ pipx install copier
$ pipx install pre-commit
$ pipx install cmem-cmemc
$ pipx install poetry
$ poetry self add "poetry-dynamic-versioning[plugin]"
```

[github-actions]: https://github.com/eccenca/cmem-plugin-template/actions
[build-shield]: https://github.com/eccenca/cmem-plugin-template/actions/workflows/check.yml/badge.svg
[copier]: https://copier.readthedocs.io/
[copier-shield]: https://img.shields.io/badge/made%20with-copier-orange
[cmem]: https://documentation.eccenca.com
[cmem-shield]: https://img.shields.io/badge/made%20for-Corporate%20Memory-blue
[python-shield]: https://img.shields.io/badge/python-v3.9-blue

