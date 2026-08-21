---
name: copier-update
description: Update this project to a newer release of the cmem-plugin-template - run copier update, resolve the conflicts it leaves behind and verify the result. Use when asked to update the template, take a new template version or resolve copier conflicts.
---

# Updating to a newer template release

This project was generated from
[cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) and
records where it came from in `.copier-answers.yml`. Updating replays the
difference between the template release recorded there and the newest one onto
this repository.

This is how the project picks up new dependency constraints, new pipeline
steps, lint configuration and agent files. Generated projects intentionally
have no self-updating automation, so nothing arrives any other way.

## Before updating

The working tree must be clean and committed - `copier update` writes into the
tree and there is no way to tell its changes from uncommitted ones afterwards.
Work on a branch, not on the main branch.

Read what is coming first, so the diff is not a surprise:
<https://github.com/eccenca/cmem-plugin-template/blob/main/CHANGELOG.md>.
Entries prefixed `github:` or `gitlab:` concern the pipeline, `plugin:` entries
apply only to plugin projects, and nested bullets warn about consequences -
most often a newly enabled lint rule that will start failing checks here.

## Updating

```bash
copier update            # asks each question again, previous answer as default
copier update --defaults # keeps every previous answer
```

Copier needs version 9 or newer. Answer the questions as before unless the
project really has changed; `project_slug` in particular must not change, since
the package name is derived from it.

## Resolving what it leaves behind

Copier merges the template's changes into the files as they are here, so any
file this project edited after generation can conflict. Conflicts appear as
ordinary git conflict markers inside the file:

```text
<<<<<<< before updating
=======
>>>>>>> after updating
```

Resolve them by hand and keep the template's version of template owned files -
`Taskfile.yaml`, `.pre-commit-config.yaml`, `.gitlab-ci.yml`,
`.github/workflows/` and `.claude/`. If this project needed a change in one of
them, that change belongs in `TaskfileCustom.yaml`, in `CLAUDE.md`, or upstream
in the template.

`CHANGELOG.md`, `README.md` and `pyproject.toml` are the opposite case: they
carry real project content, so keep this project's text and take only the parts
the template actually changed, such as a bumped dependency constraint.

Example files that were deleted after generation can reappear when the template
changes them. Delete them again.

## After updating

```bash
poetry update
task check
```

A newly enabled lint rule or a bumped dependency can turn checks red here even
though nothing in this project changed. Fix the findings rather than switching
the rule off, and add a `CHANGELOG.md` entry under `## [Unreleased]` describing
what users notice - usually the new dependency versions.
