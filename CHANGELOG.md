<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [9.0.0] 2026-08-22

### Added

- generated projects ship a `.claude/` directory with agent support for [Claude Code](https://claude.com/claude-code)
  - `.claude/rules/` is read in every session: which files belong to the template, that lint findings are fixed instead of silenced, and that user-visible changes need a changelog entry
  - `.claude/settings.json` allows the everyday commands (`task check`, `task format:fix`, `task build`, `pytest`, `ruff`, `mypy`) without a prompt, while `task install` and `task uninstall` still have to be confirmed
  - it also formats edited files by running `task format:fix` after each agent edit - remove the `hooks` block from `.claude/settings.json` if you do not want that
  - a `copier-update` skill describes how to take a new template version, and a `release` skill how to cut a release - the latter only in github hosted projects, see below
  - plugin projects additionally receive the `plugin-documentation`, `plugin-testing` and `plugin-implementation` skills, plus a rules file about `cmem-plugin-base`, the `needs_cmem` marker and the tasks that change a running deployment
  - the `plugin-implementation` skill records the conventions the plugin fleet converged on: reaching a deployment with `cmem-client` (and that `cmem.cmempy.*` is deprecated), logging through `self.log`, `Icon(package=__package__)`, explicit port declarations, honouring workflow cancellation, reporting progress from inside the entity loop, typing secrets as `Password`, and writing custom parameter types - including that `autocompletion_depends_on_parameters` hands its values to `autocomplete()` positionally
- no `CLAUDE.md` is written into generated projects
  - that file belongs to your project, is never touched by `copier update`, and is read alongside the shipped rules

### Changed

- a project is now generated with the pipeline it actually uses, not with both
  - `github_page` decides the host: with a URL you get `.github/workflows/` and no `.gitlab-ci.yml`, left blank you get `.gitlab-ci.yml` and no `.github` directory
  - `pypi` decides the publish path: the github `publish.yml`, or the manual `pypi` job of the gitlab pipeline, are only generated when it is answered yes
  - **check both answers before updating**, because `copier update` removes the files they no longer select
  - both questions used to be documented as badge and link decoration, so a stale answer is likely: their help texts now say what they generate
  - if you are built on gitlab but keep a github page, clear `github_page` - a mirror is not a build host, and the badges are not worth the pipeline
  - the `release` skill follows the same answers: it is delivered for github hosted projects only, and describes the tag triggered publish only when `pypi` is set
- the Corporate Memory badge is now served from the production documentation instead of `dev.documentation.eccenca.com`
  - the badge itself is unchanged - the development host served the same JSON, but is not a deployment anybody promises to keep up


## [8.8.0] 2026-08-21

### Changed

- github: refresh the Trivy DB cache in the generated check workflow
  - the key was constant, so the database was saved once and never replaced
  - it now rotates per run with a prefix fallback, as the template's own CI does
- copier >= v9 is now enforced by the template, not only documented
  - an older copier fails with a clear message instead of an obscure error
  - v9 is a support policy: it is the only major this template is tested against

### Removed

- the empty `[tool.pytest.ini_options] addopts` setting, which configured nothing

### Fixed

- .gitignore no longer ignores every `*.xml` and `*.html` file in the project
  - they were meant for the reports in `dist/`, which is already ignored anyway
  - a plugin shipping an XML resource or an HTML page had it silently untracked
  - after `copier update`, such files may newly appear as untracked
- .gitignore no longer ignores `version.py`, unused since poetry-dynamic-versioning


## [8.7.0] 2026-08-20

### Changed

- github: update actions/cache to v6 in the generated check workflow
  - v5 moved to the node24 runtime and needs an Actions Runner >= 2.327.1
  - only relevant for projects building on self-hosted runners


## [8.6.0] 2026-08-20

### Changed

- use cmem-plugin-base v4.20.0 (Corporate Memory 26.2)
- plugin: example test code now uses cmem-client instead of cmem-cmempy
- github: update actions in generated workflows
  - checkout v7, setup-task v3, setup-python v7, action-junit-report v6
- ruff: asserts (S101) are now allowed in `tests/` only
  - previously allowed everywhere; `assert` in plugin code is now reported
- ruff: unused args (ARG) are now allowed in `tests/`
- ruff: ignore CPY001 (missing copyright notice)
- update dependencies esp. trivy (0.73.0.1) and ruff (0.16.2)

### Fixed

- generated Taskfile: custom tasks file is `TaskfileCustom.yaml`
  - the file header wrongly named it `TaskfileCustom.yml`, which is silently ignored
- generated Taskfile: typo in the file header
- plugin: typo in the `uninstall` task description
- README: poetry requirement is `>= v2.1` (`[tool.poetry.requires-plugins]` needs poetry 2.x)
- README: task list was outdated
- README: drop manual `poetry self add` step (required plugins are installed automatically)
- gitlab: remove misleading comment on the `pypi` job (it is manual, not tag-restricted)
- trivyignore: drop stale CVE-2022-39280 suppression from the safety era, explain the file instead


## [8.5.0] 2026-06-24

### Changed

- gitlab: use python image v3.13.13
- trivy: use 0.71.2.1
- poetry: use explicit plugin requirements instead of Taskfile checks


## [8.4.1] 2026-04-14

### Fixed

- ruff UP043 issue in example plugin code


## [8.4.0] 2026-04-14

### Added

- export requirements.txt on build

### Changed

- gitlab: use python image v3.13.12
- use cmem-plugin-base v4.16.1 (Corporate Memory 26.1)

### Fixed

- ruff target-version now `py313`
- gitignore: .claude/settings.local.json


## [8.3.2] 2026-03-02

### Changed

- update trivy-py-ecc to v0.69


## [8.3.1] 2026-02-04

### Fixed

- update dependencies, no vulnerabilities


## [8.3.0] 2026-01-21

### Changed

- all: update dev-dependencies


## [8.2.1] 2025-12-10

### Fixed

- git repository init check (is now able to work inside submodule)


## [8.2.0] 2025-11-27

### Fixed

- trivy scan now includes dependencies
- github, gitlab: disable vex notification
- github, gitlab: disable progress

### Added

- github, gitlab: trivydb cached between runs


## [8.1.0] 2025-11-27

### Changed

- replace trivy-py with trivy-py-ecc ^0.67.2


## [8.0.0] 2025-11-24

### Changed

- all: switch to python 3.13.8
- all: update dev-dependencies
- use trivy as vulnerability scanner in exchange for safety
- pre-commit: use python 3.13


## [7.3.0] 2025-07-04

### Changed

- upgrade base dependency to 4.12.1
- all: update dev-dependencies

### Fixed

- lower cmemc dependency restriction in order to avoid dependency deadlock
- gitlab pipeline - pytest job: export all paths in `dist` as artefacts


## [7.2.0] 2025-05-28

### Added

- deptry check step

### Changed

- all: update dev-dependencies
- cmem-plugin-base -> 4.10.2 (Corporate Memory 25.1.x)
- update cmemc dev-dependency to v25
- plugin: example test code now uses integrated Context classes
- all: make poetry:install task non-internal (to allow calls from custom tasks)


## [7.1.0] 2025-02-10

### Changed

- all: update dev-dependencies
- plugin: tailored for Corporate Memory v24.3.x


## [7.0.0] 2024-09-09

### Changed

- Generalization of the template
  - You can create now projects of the following types:
    - eccenca Corporate Memory plugins (same as before)
    - Generic Python Projects (this is new)
  - The first template question will ask you for the project type.
  - Most features depend on this project type and will adapt to the decision.

### Added

- more shields

### Fixed

- limitations of the 6.x template version regarding project name


## [6.4.0] 2024-08-18

### Changed

- dependency updates (ruff 0.5, pytest 8, pytest-cov 5)
- cmem-plugin-base -> 4.7.0 (Corporate Memory 24.2.x)
- github: update to actions/setup-python@v5
- github: update to arduino/setup-task@v2


## [6.3.1] 2024-06-03

### Security

- ignore dev dependency security issue 70612 for jinja2


## [6.3.0] 2024-05-22

### Changed

- update ruff

### Fixed

- exampe test


## [6.2.0] 2024-05-06

### Added

- pytest-html report generation

### Changed

- coverage report does some advanced exclusion:
  - https://coverage.readthedocs.io/en/7.5.0/excluding.html#advanced-exclusion
- update dependencies, esp. ruff

### Security

- ignore pips 67599 safety issue


## [6.1.0] 2024-02-02

### Fixed

- check:ruff now creates always a junit XML file
- ignore FIX002 - allow to add TODO notes in the code

### Changed

- ignore FBT (boolean trap)


## [6.0.1] 2023-11-16

### Fixed

- pre-commit hook switched to ruff as well


## [6.0.0] 2023-11-16

### Changed

- integrate ruff (removing bandit, flake8, black and pylint)
- use plugin base 4.3.0 (cmem-cmempy >= 23.3)
- use poetry-dynamic-versioning option bump=true
  - 0.0.1.devX.. instead of 0.0.0.postX

### Fixed

- race condition in deploy task (#19)
- missing check for poetry versioning plugin on build task


## [5.3.4] 2023-11-06

### Fixed

- avoid safety issue 62044 for pip less than 23.3


## [5.3.3] 2023-10-13

### Fixed

- pylint/pillow dependencies to avoid errors


## [5.3.2] 2023-10-13 (yanked)

### Fixed

- pylint/pillow dependencies to avoid errors


## [5.3.1] 2023-09-14

### Fixed

- gitlab CI: artifact path for pytet


## [5.3.0] 2023-09-08

### Changed

- forward mikepenz/action-junit-report to v4


## [5.2.0] 2023-09-08

### Fixed

- github pipeline: use `concurrency` to avoid integration test issues

### Changes

- update checkout action to v4
- extend documentation
- clean up local build plan / task documentation


## [5.1.0] 2023-09-05 

### Changed

- use cmem-plugin-base 4.1.0 which is used by Corporate Memory 23.2

### Added

- .python-version to the project root in order to control pyenv
  - see https://realpython.com/intro-to-pyenv/ for a tutorial

### Fixed

- Windows / MinGW compatibility
- used github actions
- build plan
- Unneeded safety ignores


## [5.0.2] 2023-07-10

### Fixed

- github pipeline: remove cache config (poetry not found)


## [5.0.1] 2023-07-07

### Fixed

- README: pypi links


## [5.0.0] 2023-07-06

### Changed

- switch to (and enforce) python 3.11
- switch to cmem-plugin-base 4.x (which is the base for Corporate Memory 23.2)


## [4.2.0] 2023-05-11

### Added

- check for correct poetry-dynamic-versioning plugin
- check for valid pyproject.toml (poetry check)


## [4.1.0] 2023-04-28

### Changed

- forward to cmem-plugin-base 3.1.0 (23.1 release)
- forward dev dependencies


## [4.0.0] 2023-03-13

### Changed

- upgrade dependencies incl. cmem-plugin-base to 3.0.0
  - This includes backwards incompatible changes.
  - Migration Notes: https://github.com/eccenca/cmem-plugin-base/blob/main/CHANGELOG.md


## [3.6.2] 2023-03-10

### Changed

- update github actions checkout, cache and and setup-python (deprecated)


## [3.6.2] 2023-03-10

### Changed

- update github actions checkout, cache and and setup-python (deprecated)


## [3.6.1] 2023-02-17

### Changed

- change development dependencies to group notation.


## [3.6.0] 2023-02-13

### Changed

- updates of black, mypy and coverage

### Fixed

- gitlab ci yml migrated to gitlab >15 compatibility


## [3.5.1] 2023-01-18

### Added

- github_page question (to add icons and homepage links)
- pypi question (to add icons and links)
- made for badge in README

### Fixed

- add github token for task checkout step in the github workflow to avoid quota errors


## [3.4.1] 2022-11-24

### Added

- dependabot github action on daily basis
- mypy and flake8 execution for tests code

### Changed

- github actions to latest versions


## [3.4.0] 2022-10-21

### Added

- pytest memray memory profiler plugin
- enable `.env` file usage
- Taskfile with `clean` and `check` tasks to test the template
- github build plan to test the template

### Changed

- upgrade pytest-cov to 4.x
- upgrade mypy to 0.982

### Removed

- unneeded `poetry:init` task


## [3.3.2] 2022-09-14

### Fixed

- github: remove unneeded secrets
- github: use secrets envs only in pylint step


## [3.3.1] 2022-09-14

### Fixed

- github: publish workflow now only executed on tags


## [3.3.0] 2022-09-14

### Changed

- package versions are now generated with the poetry dynamic versioning plugin

### Added

- github: publication of tagged versions to pypi.org (if `PYPI_TOKEN` is set)
- gitlab: publication of tagged versions to pypi.org (if `PYPI_TOKEN` is set)


## [3.2.0] 2022-09-14

### Changed

- gitlab: split check phase into separate jobs
- github: split check phase into separate jobs

### Added

- gitlab: manual `publish:pypi` job which uses `PYPI_TOKEN`


## [3.1.2] 2022-09-07

### Changed

- gitlab build plan: forward base image to v3.9.12-1


## [3.1.1] 2022-09-01

### Fixed

- public README


## [3.1.0] 2022-09-01

### Added

- .gitattributes to reclassify *.py.jinja files as python
- action trigger on main branch
- set CMEM_BASE_URI and OAUTH_CLIENT_SECRET from github secrets
- needs_cmem annotation to run test only of cmem environment is available
- Dummy contexts in utils that can be used in tests
- lifetime transform plugin
- option to extend tasks with `TaskfileCustom.yml`

### Changed

- use plugin base ^2.1.0


## [3.0.1] 2022-07-12

### Fixed

- execution test now gives empty context


## [3.0.0] 2022-07-12

### Changed

- use plugin base ^2
- change interface of execute

### Removed

- all copier after task (they often break the execution)


## [2.1.2] 2022-06-13

### Added

- github action to run `task check`

### Fixed

- remove useless option values not needed by latest pylint


## [2.1.0] 2022-06-10

### Changed

- ignore safety for librdf dependency


## [2.0.0] 2022-05-27

### Changed

- migration to copier 6


## [1.0.0] 2022-05-09

### Added

- initial version for copier 5

