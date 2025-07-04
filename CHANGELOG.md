<!-- markdownlint-disable MD012 MD013 MD024 MD033 -->
# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Changed

- upgrade base dependency to 4.12.1
- all: update dev-dependencies


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

