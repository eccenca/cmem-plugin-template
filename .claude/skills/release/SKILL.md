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

   Then check that it actually *covers* the user-visible changes. Everything
   under `src/` is rendered into generated projects, so anything listed by this
   needs a changelog entry:

   ```bash
   git diff --name-only "$(git describe --tags --abbrev=0)"..develop -- src/
   ```

   This matters most for dependabot's rendered-workflows entry, whose
   merged pull requests bump actions in every generated project but write no
   changelog line of their own. Batch them into one entry in the established
   form — `github: update actions in generated workflows` with a nested bullet
   listing the versions, as in the 8.6.0 entry. Changes *outside* `src/` are
   template-internal and are normally not listed at all.
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
9. **No other CI run is occupying the concurrency group.**

   ```bash
   gh run list --workflow check.yml --limit 20 --json status,headBranch,url \
     -q '[.[] | select(.status != "completed")]'
   ```

   This must be empty. The `check` job declares `concurrency:
   testing_environment`, a static group shared by **every** branch, and GitHub
   keeps only one *pending* job per group — a newly queued run cancels the one
   already waiting. Releasing pushes two branches in quick succession, so if a
   foreign run already holds the group, one of them is evicted and shows as
   cancelled.

   If a run is in flight, stop and say which branch holds the group. It is
   cosmetic, not a correctness problem, but a cancelled run on `main` is what
   the README's build badge displays.

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
git commit -S -m "release X.Y.Z"
```

Sign the commit. `commit.gpgsign` is unset in this repository, so `-S` has to be
passed explicitly — but every commit here is signed, and 9.0.0's two commits are
the only unsigned ones, made when this step wrongly said signing did not apply.
Note the subject is `release X.Y.Z`, not `change log` — the latter is used for
ordinary changelog edits and does not identify a release.

## 4. Create the signed tag

Tag before pushing anything, so a signing failure leaves only local commits:

```bash
git tag -s "vX.Y.Z" -m "vX.Y.Z"
```

The tag name and message are both exactly `vX.Y.Z`. If signing fails despite the
preflight, stop and ask the user to create the tag themselves. The release
commit already exists and is harmless; nothing needs undoing.

## 5. Open the next cycle — commit, but do not push yet

Add a fresh empty section on `develop` so the tagged changelog stays clean and
the next contributor has a heading to write under. Insert it directly above the
version heading just released:

```markdown
## [Unreleased]

TODO: add at least one Added, Changed, Deprecated, Removed, Fixed or Security section
```

```bash
git add CHANGELOG.md
git commit -S -m "open next development cycle"
```

This commit is made **before** pushing on purpose — see step 6. The tag already
points at the release commit, which is now `develop~1`, so the tagged changelog
is unaffected by it.

## 6. Push — exactly two branch pushes

```bash
git push origin develop
git checkout main
git merge --ff-only "vX.Y.Z"
git push origin main
git checkout develop
git push origin "vX.Y.Z"
```

`develop` is pushed **once**, carrying both the release commit and the
next-cycle commit. This matters: each branch push queues a CI run into the
shared `testing_environment` concurrency group, and GitHub holds only one
pending run per group, so a third push would cancel whichever run was waiting.
Two pushes means one run in progress and one pending — nothing is evicted. The
tag push triggers nothing, since the workflow filters on
`branches: [main, develop]`.

`main` fast-forwards onto the **tag**, not onto `develop` — at this point
`develop` is one commit ahead, and `main` must point at the released commit.
Using the tag name rather than `develop~1` makes that unambiguous. `--ff-only`
is deliberate: it fails loudly rather than creating a merge commit if the branch
state is not what step 1 asserted.

`develop` now sits one commit ahead of `main`, which is the normal resting
state. The next release fast-forwards `main` again.

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

## 7. Report

Tell the user the version, the tagged commit, and that `main`, `develop` and the
tag are pushed. Do not create a GitHub Release.

## Known caveat

The tagged commit is not byte-identical to the commit CI verified in step 1 — it
differs by the changelog-only release commit. This is inherent to renaming the
heading at release time and is how every previous release worked. It is
acceptable because no check depends on `CHANGELOG.md`.

It also resolves itself shortly afterwards: the push in step 6 sends `main` to
the tagged commit, so the run triggered on `main` builds exactly what was
tagged. The run triggered on `develop` builds the next-cycle commit, which is
the tagged tree plus one more changelog edit. Between them, both sides of the
release get built — which is the reason preflight check 9 exists, since a
cancelled `main` run would silently remove that coverage.
