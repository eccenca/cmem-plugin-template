<!-- markdownlint-disable MD013 -->
# Open Tasks

Backlog of known work items that are not tied to a specific release.

## Hosting is inferred from `github_page`, not asked

Since 9.0.0 the template generates one pipeline per project: `.github/workflows`
when `github_page` holds a URL, `.gitlab-ci.yml` when it is blank. That makes
`github_page` a hosting answer, which is not what it is. It records that a
github page exists, and a project can have one while being built somewhere
else.

`cmem-plugin-kaggle` is exactly that shape: `github_page` points at
`github.com/eccenca/cmem-plugin-kaggle`, while its only remote — and its only
pipeline — is `gitlab.eccenca.com`. Under the current rule it has to clear
`github_page` to keep its build plan, which also costs it the badges and the
homepage link that the answer legitimately provides.

The fix is a `hosting` question (`github`, `gitlab`, or `both`) that the
delivery conditions read instead of `github_page`, with a default computed as
`{% if github_page %}github{% else %}gitlab{% endif %}` so existing projects are
unaffected unless they say otherwise. The cost is an eighth question, asked
again on every `copier update` of every project, which is why it was not done
in 9.0.0 — the inference is right for 21 of the 22 projects that have answered.

Worth revisiting if a second counterexample appears, or if `both` turns out to
be a real case rather than a theoretical one.

**Verification:** render all four test cases plus a case answering the new
question against the grain of `github_page`, and confirm each project gets
exactly the pipeline files it can run.

## Migrate the generated `pyproject.toml` to PEP 621 `[project]` metadata

`src/pyproject.toml.jinja` still declares `name`, `version`, `description`,
`authors`, `license`, `readme`, `keywords` and `classifiers` under
`[tool.poetry]`. Poetry 2.x deprecates all of them in favour of the PEP 621
`[project]` table.

This is not latent. Running `poetry check` in a freshly generated project prints
nine deprecation warnings, and `poetry-check` is a pre-commit hook that fires on
every commit touching `pyproject.toml`. Every author using this template is
therefore trained to ignore `poetry check` output, which is exactly where a real
configuration error would eventually appear.

The migration is fiddly rather than hard, because the project is dynamically
versioned. `poetry check` spells out the required handling for each field: some
move to `[project]` verbatim, while `version`, `readme` and `classifiers` must
either move *and* be declared static, or stay in `[tool.poetry]` and be listed in
`[project.dynamic]`. `poetry-dynamic-versioning` needs `version` to remain
dynamic.

**Verification:** render each case in `tests/` and run `poetry check` until it is
silent, then `task build` to confirm the dynamic version is still applied to the
resulting artifacts.

This rewrites the metadata block of every generated project, so it deserves to
be the headline of its own release rather than a line item in a dependency bump.

## Enforce the documentation conventions in generated plugin projects

The conventions for user-facing plugin text - what belongs in the task
documentation versus a parameter description, how choice parameters explain
their values, one vocabulary per package - now ship with plugin projects as the
`plugin-documentation` skill. A skill only reaches authors who drive an agent,
and it can only advise. The mechanically checkable part of the ruleset should
ship as a test instead, so it holds in every generated project regardless of how
the code was written.

`cmem_plugin_base.dataintegration.discovery.discover_plugins("{{ package_dir }}")`
returns a descriptor per plugin carrying `label`, `description`, `documentation`,
`parameters` and `actions`, and each parameter descriptor carries `name`,
`label`, `description`, `param_type`, `default_value`, `advanced` and `visible`.
That is enough to assert the whole mechanical half without a running CMEM, so
unlike `test_example.py` the new test needs no `needs_cmem` marker and costs
nothing in CI.

Worth asserting: every plugin has a non-empty `description` and a `documentation`
block longer than a couple of lines; every parameter and every action has a
non-empty description; the label of a `ChoiceParameterType` value is not merely
its key restated, which is what catches a dropdown that explains nothing; and no
user-facing string contains a term from a per-project list of retired words.
That last one has to read an optional list supplied by the project rather than
hardcode anything, since the vocabulary is domain-specific and the template
cannot know it.

The test belongs next to the existing example, as
`src/tests/{% if project_type == 'plugin' %}test_plugin_documentation.py{% endif %}.jinja`.
The skill it complements is delivered from
`src/{{ '.claude' }}/skills/{% if project_type == 'plugin' %}plugin-documentation{% endif %}/`
- note that the root `.claude/skills/release` sits outside `src` and belongs to
the template itself, unlike the `release` skill of the same name under `src/`.

The real cost is not the test. It is that `example_workflow.DollyPlugin` and
`example_transform.Lifetime` have to satisfy it, otherwise every freshly
generated project starts with a red suite and the author's first act is to
delete the test. Writing the example plugins up to the standard is the larger
half of this work, and it doubles as the worked example the skill can point at.

**Verification:** render `tests/plugin.yml` and `tests/plugin-github-pypi.yml`
and run `task check` in both, confirming the suite is green before any of the
example files are removed.
