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

## What the merge will not tell you

A conflict is raised only where copier could not decide. The cases that cost
the most time are the silent ones, and both directions have happened:

- **The template's new value is not applied.** The template set
  `cmem-cmemc` to `^25.3.0` in v7.3.0 and lowered it again to `>=24.2.0` in
  v8.0.0. Four repositories updated straight through that release and on to
  v9.6.1, and every one still carried the caret afterwards. No commit in them
  re-introduced it and no conflict was ever raised. It stayed harmless for a
  year, until click 8.5 began rejecting an empty colour that cmemc 25 passes
  through - and then several test suites failed at once with
  `Unknown color ''`.
- **This project's value is replaced by the template's.** A project carrying its
  own `[tool.ruff.lint] ignore` and `per-file-ignores` entries lost them
  wholesale to the template's shorter lists, and the update appeared to add 409
  lint findings. They were not debt; the configuration that had silenced them
  was gone.

So do not read "no conflicts" as "nothing to check". After updating, look at
`pyproject.toml` deliberately - at dependency constraints, and at every
list-valued setting, because a list is replaced whole rather than merged
entry by entry.

The reliable check is to render a throwaway project from the same answers and
diff against it, which shows both what should have arrived and what should not
have:

```bash
copier copy --trust --defaults --vcs-ref <the tag you updated to> \
  -d project_slug=<slug> -d project_type=<plugin|generic> \
  gh:eccenca/cmem-plugin-template /tmp/reference
diff /tmp/reference/pyproject.toml pyproject.toml
```

Treat a sudden jump in lint findings as suspected configuration loss rather
than real debt, and check that first.

## After updating

```bash
poetry update
task check
```

A newly enabled lint rule or a bumped dependency can turn checks red here even
though nothing in this project changed. Fix the findings rather than switching
the rule off, and add a `CHANGELOG.md` entry under `## [Unreleased]` describing
what users notice - usually the new dependency versions.
