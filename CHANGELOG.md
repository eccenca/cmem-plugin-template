# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added

- github_page question (to add icons and homepage links)
- pypi question (to add icons and links)
- made for badge in README
- github token for task checkout step in the github workflow


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

