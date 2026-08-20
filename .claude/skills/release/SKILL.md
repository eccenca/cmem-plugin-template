---
name: release
description: Cut a release of the cmem-plugin-template repository itself - verify preconditions, rename the changelog heading, commit, sign the tag and push. Use when asked to release, tag or publish a new version of this template.
---

# Release procedure for cmem-plugin-template

This describes how **this repository** is released. It does not apply to
projects generated from the template — those publish to PyPI from a
tag-triggered workflow and have different mechanics.

There is no PyPI package and no GitHub Release for this repository. The
annotated, PGP-signed tag `vX.Y.Z` together with the `CHANGELOG.md` entry it
points at *is* the release. Never create a GitHub Release.

Accepts an optional version argument, e.g. `/release 8.6.0`. Without it, derive
the version and confirm with the user (step 2).

## Branch model

`main` is a pointer that fast-forwards onto `develop` at release time. It never
carries commits of its own, so `main` is always an ancestor of `develop`.
Releases are cut from `develop`; the tag goes on a commit that already exists
on `develop`, which means the commit CI built is the commit that gets tagged.

**Hotfixes are out of scope.** Releasing a fix without shipping the unreleased
work already on `develop` is a statement of intent that cannot be read from the
repository state. If step 1 finds `main` is not an ancestor of `develop`, stop
and hand over to the user.

## 1. Preflight — run all of this before changing anything

These checks must pass **before** any commit is made, so that a failure leaves
the repository untouched rather than half-released. Stop at the first failure
and report the specific reason; do not attempt to fix it silently.

1. **Right repository.** `git remote get-url origin` contains
   `eccenca/cmem-plugin-template`.
2. **On develop.** `git rev-parse --abbrev-ref HEAD` is `develop`.
3. **Clean tree.** `git status --porcelain` is empty.
4. **In sync with origin.** `git fetch origin`, then `git rev-parse develop` and
   `git rev-parse origin/develop` are equal. If `develop` is ahead, tell the
   user to push first — the next check depends on it.
5. **Normal branch state.** `git merge-base --is-ancestor main develop` succeeds.
   If it fails, this is the hotfix or divergence case: stop.
6. **Changelog is ready.** `CHANGELOG.md` contains a `## [Unreleased]` heading
   followed by at least one `### Added|Changed|Deprecated|Removed|Fixed|Security`
   section with at least one bullet. A section containing only the `TODO:`
   placeholder means the changelog was never filled in: stop.
7. **Signing works.** Verify gpg can sign non-interactively *now*, rather than
   discovering it cannot after the release commit exists:

   ```bash
   echo test | gpg --local-user "$(git config user.signingkey)" --sign --output /dev/null
   ```

   If this fails or blocks, stop and ask the user to unlock their key (they can
   run the command themselves with the `!` prefix), then start again.
8. **CI is green on exactly this commit.**

   ```bash
   gh run list --branch develop --limit 10 --json headSha,conclusion,status
   ```

   There must be a run whose `headSha` equals `git rev-parse develop` with
   `status` `completed` and `conclusion` `success`. Do **not** accept the most
   recent successful run on `develop` if its `headSha` differs — that releases
   commits nothing has built. If the run is missing, in progress, or failed,
   stop and say which, with the run URL. Do not wait or poll; releasing is not
   urgent.

## 2. Determine the version

If a version was passed as an argument, use it. Validate that it is a plain
`X.Y.Z` and higher than `git tag --sort=-v:refname | head -1`.

Otherwise derive it from the `## [Unreleased]` content, state the reasoning, and
ask the user to confirm before continuing:

- **Patch** (`X.Y.Z+1`) — the section contains *only* `### Fixed`.
  Precedent: 8.4.1, 8.3.1, 8.2.1.
- **Major** (`X+1.0.0`) — toolchain-level upheaval: a Python version switch,
  replacing a core tool, a `cmem-plugin-base` **major** bump, or a template-wide
  restructure. Precedent: 8.0.0 (Python 3.13 + safety→trivy), 7.0.0 (project
  types), 6.0.0 (ruff replacing four tools), 5.0.0 (Python 3.11 + base 4.x).
- **Minor** (`X.Y+1.0`) — everything else, including `cmem-plugin-base` minor
  bumps, dependency updates and lint configuration changes. This covers the
  large majority of releases.

Judgement calls belong to the user. A lint rule that may break existing projects
is *arguably* breaking but has historically been a minor — say so and let them
decide rather than choosing silently.

Then confirm the tag does not already exist: `git rev-parse vX.Y.Z` must fail.

## 3. Release commit

Rename the heading in `CHANGELOG.md`, changing nothing else:

```diff
-## [Unreleased]
+## [X.Y.Z] YYYY-MM-DD
```

Use today's local date (`date +%F`). Commit `CHANGELOG.md` **only** — if
anything else is staged, stop:

```bash
git add CHANGELOG.md
git commit -m "release X.Y.Z"
```

Commits are not signed in this repository (`commit.gpgsign` is unset); only tags
are. Note the subject is `release X.Y.Z`, not `change log` — the latter is used
for ordinary changelog edits and does not identify a release.

## 4. Create the signed tag

Tag before pushing anything, so a signing failure leaves only a local commit:

```bash
git tag -s "vX.Y.Z" -m "vX.Y.Z"
```

The tag name and message are both exactly `vX.Y.Z`. If signing fails despite the
preflight, stop and ask the user to create the tag themselves. The release
commit already exists and is harmless; nothing needs undoing.

## 5. Push

In this order, so that an interruption never leaves a tag pointing at a commit
no branch reaches:

```bash
git push origin develop
git checkout main
git merge --ff-only develop
git push origin main
git checkout develop
git push origin "vX.Y.Z"
```

`--ff-only` is deliberate: it fails loudly rather than creating a merge commit
if the branch state is not what step 1 asserted.

### The push to main reports a bypassed rule — this is expected

`main` carries classic branch protection requiring a pull request with one
approving review, but `enforce_admins` is disabled, so a maintainer pushing the
release directly is permitted by design. Git will print:

```text
remote: Bypassed rule violations for refs/heads/main:
remote: - Changes must be made through a pull request.
```

This is not an error and the push succeeds. Do not stop, do not retry, and do
not open a pull request instead. The protection exists to prevent casual direct
pushes by non-maintainers; `main` here is a release pointer rather than a review
target, and routing the release through a PR would create a merge commit on
`main` and break the fast-forward model this procedure depends on. Force pushes
and branch deletion remain blocked for everyone, which are the rules that
actually protect history.

## 6. Open the next cycle

After the tag is pushed, add a fresh empty section on `develop` so the tagged
changelog stays clean and the next contributor has a heading to write under.
Insert directly above the version heading just released:

```markdown
## [Unreleased]

TODO: add at least one Added, Changed, Deprecated, Removed, Fixed or Security section
```

```bash
git add CHANGELOG.md
git commit -m "open next development cycle"
git push origin develop
```

`develop` is now one commit ahead of `main`, which is the normal resting state.
The next release fast-forwards `main` again.

## 7. Report

Tell the user the version, the tagged commit, and that `main`, `develop` and the
tag are pushed. Do not create a GitHub Release.

## Known caveat

The tagged commit is not byte-identical to the commit CI verified in step 1 — it
differs by the changelog-only release commit. This is inherent to renaming the
heading at release time and is how every previous release worked. It is
acceptable because no check depends on `CHANGELOG.md`.
