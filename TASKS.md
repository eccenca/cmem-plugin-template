<!-- markdownlint-disable MD013 -->
# Open Tasks

Backlog of known work items that are not tied to a specific release.

## Refresh the Trivy DB cache key in the generated workflow

`src/.github/workflows/check.yml` caches the Trivy database with a constant key
and no `restore-keys`:

```yaml
      - name: Cache Trivy DB
        id: cache-trivydb
        uses: actions/cache@v6
        with:
          path: .trivycache
          key: ${{ runner.os }}-trivydb
```

`actions/cache` only writes a cache entry on a miss. With a key that never
changes, the first run saves the database and every run afterwards is a hit, so
the cached copy is never replaced. The step therefore does not do what it looks
like it does.

The practical impact is small: trivy tracks its own database TTL and re-downloads
a stale one, so the likely outcome is a cache that saves nothing rather than a
scan against outdated vulnerability data. But the step spends time restoring a
directory whose contents trivy is about to discard.

**Proposed fix:** the pattern used by the template's own workflow since this was
noticed — a rotating key with a prefix fallback:

```yaml
          key: ${{ runner.os }}-trivydb-${{ github.run_id }}
          restore-keys: ${{ runner.os }}-trivydb-
```

This is a behaviour change in every generated project's CI, so it wants its own
changelog entry with the `github:` prefix rather than riding along with a bump.

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

## Narrow the `.gitignore` shipped to generated projects

`src/.gitignore` ends with a block of project-specific patterns that are broader
than they look:

```gitignore
version.py
co
*.xml
*.html
```

`*.xml` and `*.html` are presumably meant to exclude the generated reports in
`dist/`, but they are unanchored and therefore match everywhere in the project. A
plugin shipping an XML resource, a fixture, or an HTML documentation page gets it
silently untracked, which is a confusing failure to diagnose. The reports are
already covered by the existing `dist/` entry.

`co` looks like a stray typo rather than an intended pattern, and `version.py`
predates the switch to `poetry-dynamic-versioning`.

**Proposed fix:** anchor the report patterns to where reports are actually
written, or drop them as redundant with `dist/`, and remove `co`. Check whether
`version.py` is still produced by anything before removing it.

Note this changes behaviour for existing projects on `copier update` — files that
were silently ignored may suddenly appear as untracked.

## Improve the template's own test coverage

Two gaps in `tests/`:

- The answer files carry stale `_commit:` markers (`v6.4.0-8-gedec671` and
  similar). They are ignored by `copier copy`, so nothing breaks, but they
  misrepresent which template version the cases were written against.
- There is no case combining `project_type: generic` with `github_page` or
  `pypi: true`. Those Jinja branches in `README.md.jinja` and
  `pyproject.toml.jinja` are only ever exercised for plugins, so a badge or
  metadata bug specific to generic projects would ship unnoticed.

Adding a fourth case costs one answer file and one more CI run.

## Align the copier version pin in the template's own CI

`.github/workflows/check.yml` installs `copier>=8.3.0`, while the README requires
copier >= v9. The README is the correct one: `copier.yml` uses `validator:` for
`project_slug`, which needs copier 9. The mismatch is latent today only because
`>=8.3.0` resolves to a 9.x release anyway.

## Remove the inert pytest `addopts`

`src/pyproject.toml.jinja` contains `[tool.pytest.ini_options] addopts = ""`,
which sets nothing. Either drop it or replace it with the options the project
actually wants. Harmless, but it invites the reader to think something is
configured.
