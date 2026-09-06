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
`src/{% if github_page %}.github{% endif %}/workflows/check.yml` (rendered
into user projects) are entirely
independent, and they drift apart silently. Before concluding that a change
affects template users, check which side of the split it is on.

Several names exist on both sides with unrelated contents and unrelated
purposes: `CHANGELOG.md`, `Taskfile.yaml`, `README.md`, `LICENSE`, `.github/`
and `tests/`. The `tests/` pair is the sharpest trap — root `tests/` holds
copier answer files driving the template's own checks, while `src/tests/` holds
the example test code rendered into user projects.

`template-triage` and `release` exist only at the root and have no `src/`
counterpart at all: triage works through the feedback arriving from generated
projects and edits `src/`, which would be nonsense inside a generated project.

The `release` skill is a seventh twin, and the only one where following the
wrong copy would do real damage. `.claude/skills/release/` releases *this*
repository — no PyPI package, no GitHub Release, a `main` that fast-forwards
onto `develop`. The rendered one under `src/` releases a *generated* project,
where pushing a tag publishes to PyPI and is irreversible.

## Files in `src/` are Jinja, including their names

Filenames themselves carry Jinja conditionals, which is why `find src` returns
paths like:

```text
src/tests/{% if project_type == 'plugin' %}test_example.py{% endif %}.jinja
src/{{ package_dir }}/{% if project_type == 'plugin' %}example_workflow.py{% endif %}.jinja
```

A file whose name renders empty is simply not created, and a *directory* whose
name renders empty takes its whole subtree with it. Quote these paths in shell
commands — the braces and spaces will otherwise be mangled.

`src/.github/` is the one deliberate exception. Its delivery is gated by
`_exclude` in `copier.yml` rather than by its name, because dependabot has to
address `src/.github/workflows` by a literal path and rejects braces in a
`directory:` as a glob. See the dependency automation section below.

The agent support directory uses the same mechanism for a different reason. It
is named `src/{{ '.claude' }}/`, an expression that always renders to
`.claude`, because a literal `src/.claude/` would be picked up by Claude Code
*in this repository*: sessions working on the template would silently load the
generated project's rules and skills, including a `release` skill describing a
release procedure this repository does not follow.

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

The `tests/*.yml` files are copier answer files. `plugin`,
`plugin-github-pypi`, `generic-project` and `generic-github-pypi` cover
`project_type` against `github_page`/`pypi` answered together; `plugin-github` and
`plugin-pypi` split them apart, because since 9.0.0 the two questions select
different files: `plugin-github` is the only case rendering a github project
with no publish workflow, and `plugin-pypi` the only one rendering the gitlab
pipeline's manual `pypi` job. `task clean` removes the `*_dir` directories.

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

Three things about that second entry are easy to get wrong.

**The path is the workflow directory itself.** The `github-actions` ecosystem
does *not* append `.github/workflows` to a configured directory — it treats the
directory as the place the workflow files already are. `directory: "/src"`
therefore matches nothing and fails **silently**: dependabot reports zero
dependencies rather than an error. This was verified with a local
`dependabot update github_actions eccenca/cmem-plugin-template -d <path> -b develop`
dry run, which is the cheapest way to re-check it if the behaviour ever changes.
Note that the dry run resolves the path against the **remote** branch, so a
change to that path can only be verified after it has been pushed.

**The path must be a literal, and both workflows must end in `.yml`.**
Dependabot rejects a `directory:` containing glob characters, and Jinja braces
count — 9.0.0 pointed the entry at
`/src/{% if github_page %}.github{% endif %}/workflows` and dependabot answered
`The property '#/updates/1/directory' must not include a glob pattern`, which
invalidates the **whole file**: even the `/` entry stopped producing updates.
That is why `src/.github/` and `src/.github/workflows/publish.yml` are literal
paths whose delivery is gated by `_exclude` in `copier.yml`, instead of by the
conditional directory and file names used everywhere else in `src/`. The
`_exclude` entries are Jinja and are evaluated per answer, so a generated
project receives exactly what the conditional names delivered before — verified
across all six test cases, byte for byte, against the 9.0.0 render.

Two details make that safe to touch. Setting `_exclude` normally replaces
copier's built-in defaults, but this template sets `_subdirectory`, and copier
only applies `DEFAULT_EXCLUDE` when the subdirectory is the repository root
(`_template.py`) — so the defaults were never active here and nothing is lost by
overriding them. And `publish.yml` needs its literal name for a second reason:
the `github-actions` ecosystem only scans `*.yml`/`*.yaml`, so under its old
name `{% if pypi %}publish.yml{% endif %}` it was never scanned at all, even
before the path broke.

**A green check on such a pull request is not evidence.** `task check` renders
the test cases and runs each generated project's *Taskfile*; it never executes
the generated `.github/workflows/check.yml`. CI therefore passes regardless of
whether a bumped action actually works. Review these bumps by reading the
upstream release notes, not by trusting the check mark.

Dependency constraints in `src/pyproject.toml.jinja` are still bumped entirely
by hand — no ecosystem entry covers them, because the file is Jinja and not
valid TOML.

## Feedback from generated projects

Generated projects report findings back through the `template-feedback` skill
shipped in `src/{{ '.claude' }}/skills/`. Two things point at it: the rule in
`src/{{ '.claude' }}/rules/copier-template.md`, which names the moments worth
reporting, and a blocking `Stop` hook that speaks only when the working tree
shows evidence of template friction — a template owned file was edited, a
`# noqa` or `# type: ignore` was added, a rule joined the ruff ignore list, a
`copier update` left conflicts behind. The hook is
`src/{{ '.claude' }}/hooks/template-feedback.py`, which `settings.json` runs
directly rather than through a task, because a task runner writes to stdout and
picks its own exit codes, and stdout is the hook's JSON channel. A project
switches the hook off with an empty
`.claude/no-template-feedback` file, which is project owned and therefore
survives `copier update`.

Nothing is filed unattended. The skill drafts, shows the user the exact title
and body, and only then files — and `gh issue create` is deliberately left out
of the shipped permission allowlist, so the harness prompts as well. The two
gates are independent on purpose, because filing is the one irreversible,
public thing this feature does.

Reports arrive as issues labelled `template-feedback`, through
`.github/ISSUE_TEMPLATE/template-feedback.yml`. They deliberately **do not name
the project they came from**: most generated projects are private and some are
customer specific, while this tracker is public. They carry `_commit`,
`project_type` and whether `github_page`/`pypi` are answered instead, which is
what a fix actually needs. Do not ask a reporter to identify their repository.

Work through them with the `template-triage` skill. The loop only converges if
both halves happen:

- **Accepted** — change `src/` on a feature branch, one commit per issue with
  its `CHANGELOG.md` entry, green `task check`, no tag.
- **Declined** — close the issue **and** add the reasoning to *Deliberate
  decisions — please do not re-raise these* below.

That section is consequently no longer just a note to reviewers. The reporting
skill tells every generated project's agent to read it before filing, so it is
both the public answer to "why was this rejected" and the only thing keeping
the same finding from arriving again from the next repository. Keep writing it
for someone who has never seen this repository.

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

Changes to *delivery scope* — which files a generated project receives at all —
are major as well, and 9.0.0 is the precedent: gating the pipelines on
`github_page` and `pypi` removed working workflows from projects whose answers
were merely stale. The test is whether `copier update` can take something away,
not how large the diff is.

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

In the generated `.gitlab-ci.yml`, `build` declares
`needs: [mypy, pytest, trivy, deptry]` while `pypi` declares
`needs: [ruff, build]`. A lint failure therefore does not stop artifacts from
being built, but does stop them from being published.

This is accepted. A lint failure is already visible as a red `ruff` job in the
same pipeline, and is caught again before anything reaches PyPI, so adding
`ruff` to `build.needs` would change the pipeline of every downstream project
in exchange for a failure that is not actually escaping.

Report #67 re-raised this on a new argument: that the artifacts are consumable
by things other than the `pypi` job — a downstream job, a manual download, a
Marketplace package build — so a lint failure does escape after all. That does
not change the decision, because in the pipeline the template actually ships,
`pypi` is the **only** consumer of `build`, and it declares `needs: [ruff,
build]`. Every other consumer named is one a project adds itself, or a person
choosing to download from a pipeline that is visibly red. A project that does
add such a consumer and wants the stricter gate can add `ruff` to `build.needs`
in its own repository; that is not a reason to change it for everyone.

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
  it and expecting an immediate effect will not work. The same is true of
  `.github/ISSUE_TEMPLATE/`: the template-feedback form does not appear on the
  new-issue page until a release has carried it onto `main`.
- A pull request against `develop` gets **no closing reference** for the issues
  it fixes. `Fixes #59` in the body of a PR targeting a non-default branch
  creates no link at all — `gh pr view --json closingIssuesReferences` comes
  back empty — and since every pull request here targets `develop`, that
  applies to all of them. The working form is a closing keyword in the **commit
  subject**, `… , fixes #59`, rather than the bare `(#59)` reference: GitHub
  acts on it when the commit reaches `main`. The consequence is that issues
  close at **release time**, not at merge, which is later than people expect —
  say so rather than letting someone read it as broken automation.
- Every entry therefore sets `target-branch: develop`, without which dependabot
  opens pull requests against `main` — a branch the release model forbids
  merging into. Setting `target-branch` to a non-default branch also disables
  dependabot **security** updates for that ecosystem. This is a nominal loss:
  security updates only ever target the default branch anyway, so they would
  land on `main`, where they could not be merged.

Note that closing an unwanted dependabot pull request is not free — dependabot
reads it as "ignore this release" and will not offer that version again.

### Both Trivy caches rotate, but their paths deliberately differ

Both `check.yml` files now cache the Trivy DB under a rotating
`${{ github.run_id }}` key with `restore-keys`. The generated workflow used a
constant key until 8.8.0, which meant the database was saved once and never
replaced; `TASKS.md` carried that as a known item until it was fixed.

What must *not* be unified is the `path`. The root workflow needs an absolute
`${{ github.workspace }}/.trivycache` because `task check` runs trivy from
inside each generated `*_dir`, while a generated project runs it from its own
repository root and a relative `.trivycache` is correct there. A future tidy-up
that makes the two steps identical will break one of them.

The root workflow also caches the Trivy DB for a second reason — it keeps
`actions/cache` in use here, so that its version bumps are proven green by this
repository instead of shipping unexercised.

Note that `task check` cannot verify any of this: it runs each generated
project's *Taskfile* and never executes the generated `check.yml`.

### Generated projects get `.claude/rules/`, never a `CLAUDE.md`

Agent support is delivered as `.claude/rules/`, `.claude/settings.json` and
`.claude/skills/`. The template writes no `CLAUDE.md`, no `AGENTS.md` and no
`.mcp.json` into a generated project, and this is not an oversight.

Claude Code auto-loads `*.md` under `.claude/rules/` as project documentation —
verified against 2.1.226 by answering a question from a rules file in a
repository with no `CLAUDE.md` at all. That buys three things a shipped
`CLAUDE.md` cannot:

- **No collisions.** Six eccenca plugin repositories already carry a
  hand-written `CLAUDE.md` (`cmem-plugin-llm`, `cmem-plugin-email`,
  `cmem-plugin-loopwf`, `cmem-plugin-random`, `cmem-plugin-claudetest`,
  `rdf-canonicalization`). A template-owned `CLAUDE.md` would land on a file
  that exists in the destination but not in the previous render, which copier
  resolves with conflict markers. `.claude/rules/` is a path no project has.
- **Agent writes are harmless.** The `#` memory shortcut and `/init` write to
  `CLAUDE.md` by name, whatever a "do not edit, this is generated" header says.
  Leaving that file to the project means those writes cannot become update
  conflicts. Nothing in Claude Code writes to `.claude/rules/`.
- **Both are read.** A project's own `CLAUDE.md` is loaded alongside the rules,
  so nobody has to choose.

The cost is accepted: rules are Claude-Code-specific (Codex and Cursor read
`AGENTS.md`), and they are in context on *every* request, which is why the two
rules files stay short and carry only things an agent cannot read off the
repository — copier ownership, the lint policy, the changelog convention.

The MCP servers are documented in `README.md` rather than shipped as
`.mcp.json` for a related reason: their URL describes the developer's own
deployment, `.mcp.json` expands variables from the process environment rather
than from the project's `.env`, and their browser OAuth cannot reuse the
`client_credentials` service account that `.env` holds.

### Almost nothing verifies the shipped agent files

`task check` renders the test cases and runs each generated project's
*Taskfile*. It never starts an agent, so a conditional directory name that
renders empty removes a skill silently and every check stays green — the same
failure mode as the dependabot `directory:` bug above.

The one exception is `check:hook:case`, which pipes both `stop_hook_active`
states into the hook script inside each generated project and
asserts silence. It covers the single agent file whose failure would be loud
rather than invisible: a blocking `Stop` hook that speaks when it should not
stops every session in every generated project from ending. It says nothing
about whether the hook fires on the *right* evidence — that is still a hand
run.

Verification is manual, at authoring time, in a rendered case:

```bash
TEST_CASE=plugin task check:generate:case
cd plugin_dir && claude -p "Which files in this repository belong to the template?"
```

The answer has to come from `.claude/rules/`. Check the generic case too — it
must contain `.claude/settings.json`, `.claude/rules/copier-template.md` and
only the `copier-update` skill, plus `release` when `github_page` is answered,
with no plugin material.

### `src/Taskfile.yaml` is deliberately not a copier template

It is the one file under `src/` that needs a copier answer — the package
directory, for the ruff, mypy and coverage targets — and yet has no `.jinja`
suffix. It takes the value the long way round instead: `.copier-answers.env` is
rendered by copier, the Taskfile loads it through `dotenv:`, and `$package_dir`
is expanded by the shell when a command runs.

Renaming it to `Taskfile.yaml.jinja` and rendering the value in looks obviously
better, and was tried. It is not, because a Taskfile already contains a
templating language of its own: Task's `{{.PACKAGE}}` uses the same delimiters
as Jinja, so every one of them has to be protected, in practice by wrapping
almost the entire file in a `{% raw %}` block. A person editing the file then
has to hold two templating languages in their head at once and remember which
side of the raw block a new line falls on. Keeping the file readable by hand is
worth more than rendering one value.

The weakness of the long way round is that the shell reads `package_dir` from
the process environment, where an exported variable of that name outranks the
`dotenv` entry — and an empty one used to drop the package from every command
line and let `task check` pass having looked at nothing. That is fixed **inside
the Taskfile**, by the internal `package:exists` task that every check and
format task depends on, not by converting the file. Report #83 is the write-up.
Any other file that already carries a second templating language gets the same
treatment.

### `co` in `src/.gitignore` is CMEM orchestration, not a typo

The project-specific block at the end of `src/.gitignore` contains a bare `co`
line. It reads exactly like a two-character typo and was described as one in
`TASKS.md` until 8.8.0, when the surrounding stale entries (`version.py` and the
unanchored `*.xml` / `*.html` patterns) were removed and it was deliberately
kept.

`co` is CMEM orchestration output, which is sometimes part of a project's build
plan. The line now carries a comment saying so. Do not re-derive it as a typo
from its appearance.

### The mypy badge is mypy's own, not a shields.io imitation

In the badge rows of `README.md`, `src/README.md.jinja` and
`src/README-public.md.jinja`, `mypy-shield` points at
`https://www.mypy-lang.org/static/mypy_badge.svg`. It is the only badge not
served by shields.io, so it renders flat — no gradient, no logo — while
`poetry`, `ruff` and `copier` beside it have both. This reads as an oversight
and is not one.

That SVG is the badge mypy itself publishes for exactly this use. Replacing it
with a hand-rolled `img.shields.io/badge/mypy-checked-...` would trade an
upstream-maintained asset for an imitation this repository would then own, and
because the same link pair ships in both `src/` READMEs, every generated project
would see a badge diff on its next `copier update` — for a purely cosmetic
gain. Leave it alone.

The Corporate Memory badge next to it is a different case and *was* changed: it
used to read its endpoint from `dev.documentation.eccenca.com` and now reads it
from `https://documentation.eccenca.com/latest/badge.json`. Both serve identical
JSON, so nothing about the rendered badge moved.

### The copier requirement is a support policy, not a technical floor

`copier.yml` sets `_min_copier_version: "9.0.0"` and the README requires
copier >= v9, but the template does not technically need 9.

`TASKS.md` used to justify the requirement by claiming `validator:` needs
copier 9. That is wrong — `validator:` was added in copier **6.2.0**. The
highest genuine requirement is **8.1.0**, for the computed values that
`package_name` and `package_dir` express as `when: false` questions; the CLI
usage documented in the README needs 8.0.0. copier 9.0.0's only breaking change
was a return code for unsafe templates, which does not affect this template.

The floor is set at 9.0.0 on purpose: 9.x is the only major this template is
actually tested against, and declaring 8.1.0 would claim support for a 2023
release that CI has never exercised. If the floor is ever revisited, revisit it
as a support decision — do not "correct" it downward on the grounds that the
template renders under copier 8.

### `task check` does not check documentation links

Generated projects ship user-facing documentation full of external links — the
eccenca documentation, PyPI, GitHub, and whatever a `@Plugin` `documentation=`
block points at — and nothing verifies that those links still resolve. Adding a
`check:links` task built on a link checker such as lychee, wired into
`task check`, has been proposed (report #73) and declined.

Link rot is real, but a link checker is the wrong instrument here because it
makes a check that must be deterministic depend on things the project does not
control. `task check` is the gate every contributor and every pipeline runs, and
it is documented as non-negotiable. A link checker fails it when the developer
is offline, when GitHub or PyPI rate-limit unauthenticated requests from a CI
runner, and when somebody else's site has a bad afternoon. A required check that
goes red for reasons unrelated to the change gets disabled or `--force`d, and
then it protects nothing — the same reasoning that kept an automated
product-name check out of `task check` in report #74.

It also costs more than it looks. The toolchain is otherwise entirely Poetry
managed, so every generated project, every contributor machine and every runner
would need a non-Python binary installed for it.

And most of the links in a freshly generated project are the template's own —
`documentation.eccenca.com`, the badge endpoints, `python-poetry.org`,
`taskfile.dev`. Those are fixed here, once, for everybody. Checking them again
in each of fifty downstream projects re-verifies the template's URLs fifty
times over and still says nothing about the one link a plugin author actually
added.

A project that wants the check can add a `check:links` task to its own
`TaskfileCustom.yaml`, which is exactly what that file is for, and run it on a
schedule rather than on every commit — which is the cadence link rot deserves.
