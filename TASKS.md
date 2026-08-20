<!-- markdownlint-disable MD013 -->
# Open Tasks

Backlog of known work items that are not tied to a specific release.

## Let dependabot cover the generated workflows in `src/`

`.github/dependabot.yml` declares the `github-actions` ecosystem with
`directory: "/"`, so it only ever sees the template's own workflow at
`.github/workflows/check.yml`. The workflows rendered into generated projects
(`src/.github/workflows/check.yml` and `publish.yml`) are outside that scope and
therefore never get automatic bumps.

The consequence is silent drift: by 8.6.0 the generated workflows had fallen two
majors behind the template's own on `actions/checkout` (v5 vs. v7) and
`mikepenz/action-junit-report` (v4 vs. v6), plus one major on
`arduino/setup-task` and `actions/setup-python`. They were bumped by hand for
that release, and without a fix the drift restarts immediately.

Note that shipping a `dependabot.yml` *into* generated projects is deliberately
not the answer — template users are expected to pick up new versions by updating
to the latest template release, not by drifting forward on their own.

**Proposed fix:** add a second `updates:` entry to the root
`.github/dependabot.yml` scoped to the `src` directory:

```yaml
  - package-ecosystem: "github-actions"
    directory: "/src"
    schedule:
      interval: "daily"
```

The files under `src/.github/workflows/` contain no copier Jinja, so they are
valid YAML and should parse cleanly.

**Open question to verify first:** the `github-actions` ecosystem historically
only scanned `.github/workflows` at the repository root, and non-root
`directory` support is not confirmed for this repository. Validate with a
throwaway PR before relying on it. If dependabot cannot be pointed at `src/`,
fall back to a scheduled check (or a release checklist item) that diffs the
action versions in `.github/workflows/` against those in
`src/.github/workflows/`.

## Decide whether `actions/cache` in the generated workflow should be bumped

`src/.github/workflows/check.yml` pins `actions/cache@v4` for the Trivy DB
cache. It was left untouched during the 8.6.0 action bumps because the
template's own workflow does not use `actions/cache`, so no newer version has
been proven green in this repository.
