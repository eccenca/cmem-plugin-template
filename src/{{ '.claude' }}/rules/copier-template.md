# Working in this project

This repository was generated from the
[cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) copier
template and stays connected to it through `copier update`.

## Some files belong to the template

`Taskfile.yaml`, `.pre-commit-config.yaml`, the pipeline definitions
(`.gitlab-ci.yml`, and `.github/workflows/` where it exists) and everything
under `.claude/` are rendered from the template. Edits there are not preserved:
the next `copier update` either reverts them or turns them into a merge
conflict.

Add project specific build steps to `TaskfileCustom.yaml` instead - note the
`.yaml` spelling, since only that one is included. Project specific agent
instructions belong in `CLAUDE.md`, which the template never writes and which
is read alongside these rules. Personal tool permissions belong in
`.claude/settings.local.json`, which is git-ignored.

When something in a template owned file is genuinely wrong, fix it upstream in
the template and update, rather than patching the generated copy.

## Checks are not negotiable

Run `task check` before considering a change finished. It runs ruff, mypy,
deptry, trivy and pytest, and it is the same suite the pipeline runs.
`task format:fix` repairs formatting and the mechanical lint findings.

Ruff is configured in `pyproject.toml` with `select = ["ALL"]` and a curated
`ignore` list. Fix what a rule complains about. Do not add `# noqa`, do not
extend the `ignore` list and do not loosen a mypy setting to make a check pass;
if a rule really is wrong for this project, say so and let a human decide.

## Every user visible change gets a changelog entry

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/). Add an
entry under `## [Unreleased]` in the matching `### Added`, `### Changed`,
`### Fixed` or `### Removed` section. The trigger is whether a user would
notice, not whether behaviour changed.
