# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/)

## [Unreleased]

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

## [3.0.1]

### Fixed

- execution test now gives empty context

## [3.0.0]

### Changed

- use plugin base ^2
- change interface of execute

### Removed

- all copier after task (they often break the execution)

## [2.1.0]

### Added

- github action to run `task check`

### Fixed

- remove useless option values not needed by latest pylint

## [2.0.1]

### Changed

- ignore safety for librdf dependency

## [2.0.0]

### Changed

- migration to copier 6

## [1.0.0]

### Added

- initial version for copier 5

