# cmem-plugin-template

[![workflow][build-shield-main]][github-actions] [![workflow][build-shield-develop]][github-actions] [![version][version-shield]][changelog] ![python-shield]
[![poetry][poetry-shield]][poetry-link] [![ruff][ruff-shield]][ruff-link] [![mypy][mypy-shield]][mypy-link] [![copier][copier-shield]][copier] 
[![eccenca Corporate Memory][cmem-shield]][cmem]

This repository contains a [copier](https://copier.readthedocs.io/) template.

You can use it to bootstrap the following types of project:

- **[eccenca Corporate Memory](https://documentation.eccenca.com) [Python Plugin](https://documentation.eccenca.com/latest/develop/python-plugins/)**: Bootstrapping and keeping plugin repositories up-to-date was the initial idea of this template.
- **Generic Python Project**: After tons of commits, we wanted to use this template not only for plugins, but for all kinds of python projects.

<details>
  <summary>Table of contents</summary>
<!-- vim-markdown-toc GFM -->

* [Features](#features)
* [Usage](#usage)
    * [Project Initialization](#project-initialization)
    * [Template Updates](#template-updates)
    * [Other Tasks](#other-tasks)
* [Setup](#setup)
    * [Local Requirements](#local-requirements)
    * [Integration Tests](#integration-tests)
    * [Plugins only: Corporate Memory Environment](#plugins-only-corporate-memory-environment)
    * [CI Build Plan](#ci-build-plan)
    * [Editor / IDE Support](#editor--ide-support)
        * [PyCharm](#pycharm)

<!-- vim-markdown-toc -->
</details>

## Features

- [Python / poetry](https://python-poetry.org/) project with
  - [pytest](https://www.pytest.org/) (incl. [memray](https://bloomberg.github.io/memray/) + [pytest-dotenv](https://github.com/quiqua/pytest-dotenv) + [code coverage](https://github.com/pytest-dev/pytest-cov)) as the testing framework,
  - [ruff](https://docs.astral.sh/ruff/) as all-hands linter and formatter,
  - [mypy](http://mypy-lang.org/) as type checker, and
  - [safety](https://pyup.io/safety/) as dependency vulnerability scanner.
- Build plans for
  - [gitlab](https://github.com/eccenca/cmem-plugin-template/blob/main/src/.gitlab-ci.yml),
  - [github](https://github.com/eccenca/cmem-plugin-template/tree/main/src/.github/workflows), and
  - locally with [task](https://taskfile.dev/) (tested for Linux, MacOS and Windows/MinGW).
  - Including
    - badge generation,
    - JUnit XML file and
    - coverage stat generation.

## Usage

### Project Initialization

The following command will create a new project directory with the latest released template.
This produces a plugin which is compatible the [latest release of eccenca Corporate Memory](https://documentation.eccenca.com/latest/).

Note: Select 'Generic Python Project' as an answer to the initial question to skip creation of plugin specific code.

```shell-session
$ copier copy gh:eccenca/cmem-plugin-template cmem-plugin-my
```

The following command will use the latest develop version of the template:
This produces a plugin which is compatible the latest development snapshot of eccenca Corporate Memory.

```shell-session
$ copier copy -r develop gh:eccenca/cmem-plugin-template cmem-plugin-my
```

After that, you can initialize the repository and install git hooks:

```shell-session
$ cd cmem-plugin-my
$ git init; git add .; git commit -m "init"
$ pre-commit install
```

Then you can run the local test suite and build a first deployment artefact:

```shell-session
$ task check build
```

### Template Updates

We [continuously update](https://github.com/eccenca/cmem-plugin-template/graphs/code-frequency) this repository.
This includes maintenance of dependencies, build plan updates and the adoption of new features from the [plugin base library](https://github.com/eccenca/cmem-plugin-base).

In order to upgrade your project to the latest template release, use the following command:

```shell-session
$ copier update
```

In order to prepare your project for the upcoming next release, use this command:

```shell-session
$ copier update -r develop
```

Please also have a look at the [copier documentation](https://copier.readthedocs.io/en/stable/updating/).

### Other Tasks

All available tasks for your project can be listed like this:

```shell-session
∴ task
task: Available tasks for this project:
* build:                   Build a tarball and a wheel package
* check:                   Run whole test suite incl. unit and integration tests
* clean:                   Removes dist, *.pyc and some caches
* check:linters:           Run all linter and static code analysis tests
* check:mypy:              Complain about typing errors
* check:pytest:            Run unit and integration tests
* check:ruff:              Complain about everything else
* check:safety:            Complain about vulnerabilities in dependencies
* format:fix:              Format Python files and fix obvious issues
* format:fix-unsafe:       Format Python files and fix 'unsafe' issues
* plugin:deploy:           Install plugin package in Corporate Memory
```

You can extend this task list by creating a file `TaskfileCustom.yaml` in your repository root:

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


## Setup

### Local Requirements

The following tools are needed for local task execution:

- Python 3.11
- [copier](https://copier.readthedocs.io/) (>= v9) for project template rendering
- [poetry](https://python-poetry.org/) (>= v1.7) for packaging and dependency managing (+ [dynamic versioning plugin](https://github.com/mtkennerly/poetry-dynamic-versioning))
- [pre-commit](https://pre-commit.com/) (>= v2.20) - managing and maintaining pre-commit hooks
- [task](https://taskfile.dev/) (>= v3.29) for build task running (make sure to follow the installation instructions to avoid confusion with taskwarrior)
- [cmemc](https://eccenca.com/go/cmemc) (>= v23.1) for interacting with eccenca Corporate Memory (only needed for plugin projects)

Example installation of the requirements with [pipx](https://pipx.pypa.io/) on Ubuntu:

``` shell-session
$ sudo sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin
$ python3 -m pip install --user pipx
$ python3 -m pipx ensurepath
$ pipx install copier
$ pipx install pre-commit
$ pipx install cmem-cmemc
$ pipx install poetry
$ poetry self add "poetry-dynamic-versioning[plugin]"
```

### Integration Tests

This template uses the [pytest](https://pytest.org) testing framework.
Testing your plugin is crucial and should be done locally as well as  integrated with eccenca Corporate Memory.

In order to setup access to a Corporate Memory deployment, you need to provide correct environment variables.
Without these variables, only standalone tests can be executed (see `1 skipped`):

``` shell-session
$ task check:pytest
...
... ===== 3 passed, 1 skipped in 0.09s =====
```

### Plugins only: Corporate Memory Environment

By providing the correct [cmemc](https://eccenca.com/go/cmemc) [environment variables](https://documentation.eccenca.com/latest/automate/cmemc-command-line-interface/configuration/environment-based-configuration/) in an `.env` file or directly in your environment, your plugin can be tested in an integrated way:

``` shell-session
# Environment as direct variables:
$ export CMEM_BASE_URI="https://cmem.example.org"
$ export OAUTH_CLIENT_ID="cmem-service-account"
$ export OAUTH_CLIENT_SECRET="..."
$ export OAUTH_GRANT_TYPE="client_credentials"
```

``` shell-session
# Environment as .env files
$ cat .env
CMEM_BASE_URI="https://cmem.example.org"
OAUTH_CLIENT_ID="cmem-service-account"
OAUTH_CLIENT_SECRET="..."
OAUTH_GRANT_TYPE="client_credentials"
```

### CI Build Plan

The gitlab workflow as well as the github action pipelines need the same environment variables as secrets:

- For github, go to Settings > Secret > Actions > [New Repository Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- For gitlab, go to Settings > CI/CD > Variables (Expand) > [Add Variable (protected, masked, all environments)](https://docs.gitlab.com/ee/ci/variables/)

An example github pipeline can be seen [here](https://github.com/eccenca/cmem-plugin-yaml/actions).

In addition to the eccenca Corporate Memory credential secrets, a `PYPI_TOKEN` secret can be set in order to use the `publish` task/workflow.

### Editor / IDE Support

#### PyCharm

In order to have the best PyCharm experience, when starting a project with this template, we suggest the following PyCharm plugins:

- [Ruff](https://plugins.jetbrains.com/plugin/20574-ruff) will provide the linting hints which will be raised by the pipeline anyway.
- [Taskfile](https://plugins.jetbrains.com/plugin/17058-taskfile) will allow for starting tasks.

[version-shield]: https://img.shields.io/github/v/tag/eccenca/cmem-plugin-template?label=version&sort=semver
[changelog]: https://github.com/eccenca/cmem-plugin-template/blob/main/CHANGELOG.md
[github-actions]: https://github.com/eccenca/cmem-plugin-template/actions
[build-shield-main]: https://img.shields.io/github/actions/workflow/status/eccenca/cmem-plugin-template/check.yml?logo=github&branch=main&label=main
[build-shield-develop]: https://img.shields.io/github/actions/workflow/status/eccenca/cmem-plugin-template/check.yml?logo=github&branch=develop&label=develop
[copier]: https://copier.readthedocs.io/
[copier-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json
[cmem]: https://documentation.eccenca.com
[cmem-shield]: https://img.shields.io/endpoint?url=https://dev.documentation.eccenca.com/badge.json
[python-shield]: https://img.shields.io/badge/python-v3.11-blue
[mypy-link]: https://mypy-lang.org/
[mypy-shield]: https://www.mypy-lang.org/static/mypy_badge.svg
[ruff-link]: https://docs.astral.sh/ruff/
[ruff-shield]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&label=Code%20Style
[poetry-link]: https://python-poetry.org/
[poetry-shield]: https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json

