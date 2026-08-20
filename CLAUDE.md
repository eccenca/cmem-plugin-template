<!-- markdownlint-disable MD013 -->
# Working on this repository

This is a [copier](https://copier.readthedocs.io/) template that generates
Python project skeletons. Nothing here is an application — almost every file is
either template input or template output. The notes below cover the parts of
that structure that are easy to get wrong.

## The root / `src/` split is the most important distinction

`copier.yml` sets `_subdirectory: src`, so **only `src/` is rendered into
generated projects**. Everything at the repository root belongs to the template
itself and is never seen by template users.

This split has bitten before. Concrete example: the GitHub Action versions in
`.github/workflows/check.yml` (root, the template's own CI) and in
`src/.github/workflows/check.yml` (rendered into user projects) are entirely
independent, and they drift apart silently. Before concluding that a change
affects template users, check which side of the split it is on.

Several names exist on both sides with unrelated contents and unrelated
purposes: `CHANGELOG.md`, `Taskfile.yaml`, `README.md`, `LICENSE`, `.github/`
and `tests/`. The `tests/` pair is the sharpest trap — root `tests/` holds
copier answer files driving the template's own checks, while `src/tests/` holds
the example test code rendered into user projects.

## Files in `src/` are Jinja, including their names

Filenames themselves carry Jinja conditionals, which is why `find src` returns
paths like:

```text
src/tests/{% if project_type == 'plugin' %}test_example.py{% endif %}.jinja
src/{{ package_dir }}/{% if project_type == 'plugin' %}example_workflow.py{% endif %}.jinja
```

A file whose name renders empty is simply not created. Quote these paths in
shell commands — the braces and spaces will otherwise be mangled.

## Two project types

The first copier question, `project_type`, selects between:

- `plugin` — an eccenca Corporate Memory plugin, depending on `cmem-plugin-base`
- `generic` — a plain Python project using only the build plan and config

Most conditionals in `src/` branch on this. When changing anything under `src/`,
consider whether it applies to one type or both.

## How to test a change

There is no test suite for the template itself. `task check` generates real
projects and runs *their* checks:

1. `check:generate:cases` renders every test case in `tests/*.yml` into a
   `<case>_dir` directory at the repository root and git-inits it.
2. `check:validate:cases` runs `poetry update && task check` inside each one.

The `tests/*.yml` files are copier answer files, one per supported
configuration (`plugin`, `plugin-github-pypi`, `generic-project`). `task clean`
removes the `*_dir` directories.

Note the blind spot this creates: the generated projects only exercise the
example code that ships in `src/`. A lint rule tightened for plugin source code,
for instance, will pass here as long as the example plugin does not happen to
violate it — while still breaking real downstream projects.

Never edit files inside a `*_dir` directory. They are generated output and are
deleted by `task clean`.

## Dependency automation belongs to the template, not to generated projects

Generated projects intentionally ship without `dependabot.yml` or any other
self-updating configuration. Template users are expected to pick up new
dependency and action versions by updating to the latest template release
(`copier update`), not by drifting forward independently. If each generated
project self-updated, the template would stop describing what a current project
looks like.

The corollary is that pinned versions inside `src/` must be bumped deliberately
as part of a release, by the *template's* automation rather than by the
generated project. `.github/dependabot.yml` therefore carries two
`github-actions` entries: one for `/` (the template's own CI) and one for
`/src/.github/workflows` (the workflows rendered into user projects).

Two things about that second entry are easy to get wrong.

**The path is the workflow directory itself.** The `github-actions` ecosystem
does *not* append `.github/workflows` to a configured directory — it treats the
directory as the place the workflow files already are. `directory: "/src"`
therefore matches nothing and fails **silently**: dependabot reports zero
dependencies rather than an error. This was verified with a local
`dependabot update github_actions eccenca/cmem-plugin-template -d <path> -b develop`
dry run, which is the cheapest way to re-check it if the behaviour ever changes.

**A green check on such a pull request is not evidence.** `task check` renders
the test cases and runs each generated project's *Taskfile*; it never executes
the generated `.github/workflows/check.yml`. CI therefore passes regardless of
whether a bumped action actually works. Review these bumps by reading the
upstream release notes, not by trusting the check mark.

Dependency constraints in `src/pyproject.toml.jinja` are still bumped entirely
by hand — no ecosystem entry covers them, because the file is Jinja and not
valid TOML.

## Changelog conventions

`CHANGELOG.md` (the root one) follows Keep a Changelog and has established
conventions worth matching:

- `cmem-plugin-base` bumps name the matching Corporate Memory release, e.g.
  `use cmem-plugin-base v4.20.0 (Corporate Memory 26.2)`. This is the entry
  template users care about most — it determines plugin API compatibility.
- A `github:` or `gitlab:` prefix means the **generated** pipeline. Changes to
  the template's own CI are not usually listed at all.
- A `plugin:` prefix marks entries that apply only to `project_type == 'plugin'`.
- Fixes to code that was never released are folded into the entry describing the
  change, not listed separately under `### Fixed`.
- Nested bullets are used to warn about consequences, e.g. a lint rule that may
  start failing checks in existing projects.

## Releasing

The release procedure is codified as a skill: `.claude/skills/release/SKILL.md`,
invocable as `/release` (optionally `/release 8.6.0`). Follow it rather than
improvising a tag — it encodes the preconditions, the version derivation rules
and the branch model.

In short: `main` is a pointer that fast-forwards onto `develop` at release time
and never carries its own commits, a release is a single commit renaming
`## [Unreleased]` to `## [X.Y.Z] YYYY-MM-DD` with the subject `release X.Y.Z`,
and the annotated PGP-signed tag `vX.Y.Z` is the release artifact. This
repository publishes nothing to PyPI and deliberately creates no GitHub
Releases.

Historically, major versions were reserved for toolchain-level changes — a
Python version switch, replacing the linter, a `cmem-plugin-base` major bump.
Dependency bumps and lint configuration changes are minor releases.

## Ruff configuration

Lint rules for generated projects live in `src/pyproject.toml.jinja` under
`[tool.ruff.lint]`, which selects `ALL` and then subtracts. Keep the `ignore`
list alphabetically sorted, and keep the trailing `#` comment explaining why
each rule is off. Rules that should only relax inside tests belong in
`[tool.ruff.lint.per-file-ignores]` under `"tests/**/*.py"`, not in the global
list.

Because `select = ["ALL"]` is used, a ruff upgrade can enable newly stabilised
rules and break generated projects. Adding the new rule to `ignore` is a normal
part of a ruff version bump.

## Deliberate decisions — please do not re-raise these

The following look like oversights during a review, but are intentional. They
have each been considered and left as they are.

### The GitLab `build` job does not need `ruff`

In `src/.gitlab-ci.yml`, `build` declares
`needs: [mypy, pytest, trivy, deptry]` while `pypi` declares
`needs: [ruff, build]`. A lint failure therefore does not stop artifacts from
being built, but does stop them from being published.

This is accepted. A lint failure is already visible as a red `ruff` job in the
same pipeline, and is caught again before anything reaches PyPI, so adding
`ruff` to `build.needs` would change the pipeline of every downstream project
in exchange for a failure that is not actually escaping.

### The GitLab `pypi` job is manual, not tag-restricted

`pypi` is gated only by `when: manual`; there is no `rules` clause limiting it
to tag pipelines, unlike the GitHub `publish.yml` workflow which triggers on
tags. It previously carried a comment claiming tag-only behaviour, which was
removed in 8.6.0 because the comment was wrong, not the pipeline.

### Custom task files must be named `TaskfileCustom.yaml`

Only the `.yaml` spelling is included by the generated `Taskfile.yaml`. The
header comment wrongly said `TaskfileCustom.yml` from 3.1.0 until 8.6.0, so
projects created in that window may contain a `TaskfileCustom.yml` that is
silently ignored. A fallback include for the `.yml` spelling was considered and
rejected: the feature is rarely used, and one canonical spelling is preferable
to two.

### Releases push directly to `main`, bypassing its branch protection

`main` has classic branch protection requiring a pull request with one approving
review, so pushing a release to it prints `Bypassed rule violations for
refs/heads/main`. This is intended, not an oversight: `enforce_admins` is
disabled on that protection, meaning the configuration deliberately permits
maintainers to push directly.

`main` is a release pointer that fast-forwards onto `develop`, not a branch that
receives reviewed work — the review already happened on `develop`, and the
commit being fast-forwarded to is one CI has built. Routing releases through a
pull request would create a merge commit on `main` and break the invariant that
`main` never carries commits of its own.

The rules that protect history are still enforced for everyone: force pushes and
branch deletion are both blocked. The pull request requirement exists to stop
casual direct pushes, not releases.

### `main` stays the default branch, so dependabot needs `target-branch`

`main` is the GitHub default branch even though it only ever fast-forwards onto
`develop`. That is a deliberate choice about what the repository landing page
shows, and it is safe for template users: copier resolves
`copier copy gh:eccenca/cmem-plugin-template` to the latest PEP 440 **tag**, not
to the default branch, and `check.yml` lists `branches: [main, develop]`
explicitly, so neither depends on which branch is default.

It does cost two things, both accepted:

- Dependabot reads `.github/dependabot.yml` from the **default branch only**, so
  a change to that file is inert until a release fast-forwards `main`. Editing
  it and expecting an immediate effect will not work.
- Every entry therefore sets `target-branch: develop`, without which dependabot
  opens pull requests against `main` — a branch the release model forbids
  merging into. Setting `target-branch` to a non-default branch also disables
  dependabot **security** updates for that ecosystem. This is a nominal loss:
  security updates only ever target the default branch anyway, so they would
  land on `main`, where they could not be merged.

Note that closing an unwanted dependabot pull request is not free — dependabot
reads it as "ignore this release" and will not offer that version again.

### The generated `actions/cache` key is knowingly constant

`src/.github/workflows/check.yml` caches the Trivy DB under a constant key with
no `restore-keys`, so after the first save the cache is a permanent hit and is
never refreshed. Trivy manages its own database TTL and re-downloads a stale DB,
so the step is closer to inert than harmful. It is recorded in `TASKS.md` rather
than fixed inline, because changing the key changes CI behaviour in every
generated project.

The root `.github/workflows/check.yml` deliberately does *not* copy that pattern:
it uses a rotating `${{ github.run_id }}` key with `restore-keys`. The root
workflow also caches the Trivy DB for a second reason — it keeps `actions/cache`
in use here, so that its version bumps are proven green by this repository
instead of shipping unexercised.
