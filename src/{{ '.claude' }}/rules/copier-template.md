# Working in this project

This repository was generated from the
[cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) copier
template and stays connected to it through `copier update`.

## Some files belong to the template

`Taskfile.yaml`, `.pre-commit-config.yaml`, the pipeline definition for this
project's host (`.github/workflows/` or `.gitlab-ci.yml`) and everything under
`.claude/` are rendered from the template. Edits there are not preserved:
the next `copier update` either reverts them or turns them into a merge
conflict.

Add project specific build steps to `TaskfileCustom.yaml` instead - note the
`.yaml` spelling, since only that one is included. Project specific agent
instructions belong in `CLAUDE.md`, which the template never writes and which
is read alongside these rules. Personal tool permissions belong in
`.claude/settings.local.json`, which is git-ignored.

When something in a template owned file is genuinely wrong, fix it upstream in
the template and update, rather than patching the generated copy. The way to
do that is to report it: use the `template-feedback` skill, which checks what
the template has already decided and drafts an issue for you to confirm. Reach
for it when you wanted to edit a template owned file, when a lint or typing
rule had to be worked around, when a `copier update` conflict will recur for
everyone, or when something these rules or the shipped skills claim turns out
to be wrong. A finding that only applies to this project is not template
feedback.

## Checks are not negotiable

Run `task check` before considering a change finished. It runs ruff, mypy,
deptry, trivy and pytest, and it is the same suite the pipeline runs.
`task format:fix` repairs formatting and the mechanical lint findings.

Ruff is configured in `pyproject.toml` with `select = ["ALL"]` and a curated
`ignore` list. Fix what a rule complains about. Do not add `# noqa`, do not
extend the `ignore` list and do not loosen a mypy setting to make a check pass;
if a rule really is wrong for this project, say so and let a human decide.

A few rules cannot be satisfied at all in the right context, and obeying them
then writes the bug they exist to prevent - `S701` asks for HTML autoescaping,
which corrupts a Jinja template that renders JSON. When that happens, do not
guess: describe why the rule is wrong here and let a human decide. If they
agree, the resolution is a `# noqa` on the offending line with the reason in a
comment above it - never a new entry in the `ignore` list, which would also
silence the rule for code nobody has looked at. Report it with the
`template-feedback` skill too, since a rule that is wrong here is usually wrong
in other projects as well.

## Every user visible change gets a changelog entry

`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/). Add an
entry under `## [Unreleased]` in the matching `### Added`, `### Changed`,
`### Fixed` or `### Removed` section. The trigger is whether a user would
notice, not whether behaviour changed.

Do not cite an issue or Jira ticket. The people reading this file cannot open
them, so the entry has to stand on its own.
