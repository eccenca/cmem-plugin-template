<!-- markdownlint-disable MD013 -->
# Open Tasks

Backlog of known work items that are not tied to a specific release.

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
