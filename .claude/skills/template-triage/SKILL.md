---
name: template-triage
description: Triage template-feedback issues reported from generated projects - decide each one against the deliberate decisions, implement the accepted ones in src/ with changelog entries on a feature branch, and draft the decline text for the rest. Use when asked to triage, review or work through the template-feedback issues.
---

# Triaging template feedback

Projects generated from this template report findings back as issues labelled
`template-feedback`, filed through
`.github/ISSUE_TEMPLATE/template-feedback.yml`. The reporting side is the
`template-feedback` skill shipped in `src/{{ '.claude' }}/skills/`.

**This skill belongs to this repository, not to generated projects.** Like
`release`, it has a twin under `src/` that does something entirely different -
see the root / `src/` split in `CLAUDE.md`.

A finding arrives from a project you cannot see, filtered through an agent that
could not name it. Treat the report as a claim to verify, not as a fact.

## What triage is for

Every accepted finding changes `src/`, and everything in `src/` reaches every
downstream project on its next `copier update`. Every declined finding has to
end up somewhere the *next* project's agent will look, or the same report
arrives again from the next repository, and the one after that. Both halves
matter; the decline half is the one that gets skipped.

## Preconditions

1. The working tree is clean and you are on `develop`.
2. Create a feature branch - never work on `develop` directly:

   ```bash
   git switch -c feature/template-feedback-triage
   ```

3. List what is waiting:

   ```bash
   gh issue list --repo eccenca/cmem-plugin-template \
       --state open --label template-feedback
   ```

## Decide each issue

Read the issue in full, then check it in this order and stop at the first hit:

1. **Already decided.** Compare against *Deliberate decisions - please do not
   re-raise these* in `CLAUDE.md`. If it is there, **decline it and do not
   implement it**, however well the issue argues its case. Re-opening a settled
   decision from a triage sweep is exactly how that section stops being worth
   reading. Changing one of those decisions is a human call, made deliberately,
   not a side effect of working through a list.
2. **Already fixed.** Check `## [Unreleased]` in `CHANGELOG.md` and the current
   state of `src/`. If it is fixed and waiting for a release, say so and close
   the issue pointing at the entry.
3. **Not template material.** The finding only holds for the project it came
   from, or it asks for something a project should put in `TaskfileCustom.yaml`
   or its own `CLAUDE.md`. Decline.
4. **Wrong side of the split.** The finding is about this repository's own CI,
   its own `Taskfile.yaml` or its own `.claude/` - not about `src/`. That is a
   real report, but it is not a change to what users receive. Handle it as
   ordinary work and drop the `template-feedback` framing.
5. Otherwise, **accept**.

Weigh an accepted finding against both `project_type`s and against
`github_page`/`pypi` being answered either way. A change that only makes sense
for plugins belongs behind the `project_type == 'plugin'` condition, not in the
shared path.

## Implement an accepted finding

One issue, one commit. A sweep that lands several findings in a single diff
cannot be reviewed finding by finding, and a bad one cannot be dropped without
unpicking the good ones.

For each accepted issue:

1. Make the change in `src/`. Remember that filenames there are Jinja, that a
   name rendering empty deletes the file, and that the pipelines and the
   `.github` directory are gated by `_exclude` in `copier.yml`.
2. Add a `CHANGELOG.md` entry under `## [Unreleased]`, following the
   conventions in `CLAUDE.md` - a `plugin:` prefix when it only applies to
   plugin projects, `github:`/`gitlab:` for the generated pipelines, and nested
   bullets when downstream projects will notice a consequence.
3. Commit both together, referencing the issue:

   ```bash
   git commit -S -m "<what changed> (#<issue>)"
   ```

Do not tag and do not release. Releasing is `/release`, and it is a separate,
deliberate step.

## Decline an issue

Declining is not just closing. Add the reasoning to the *Deliberate decisions -
please do not re-raise these* section of `CLAUDE.md`, in the same voice as the
entries already there: what it looks like, why it is not that, and what was
weighed. That section is what the reporting skill tells generated projects to
read before filing, so an entry there is what stops the finding coming back.

Then close the issue with a comment that says the same thing in short and links
to the section.

Skip the `CLAUDE.md` entry only for a finding nobody could reasonably repeat -
a one-off mistake in the report itself, not a judgement call about the
template.

## Finish

```bash
task check
```

This renders every test case and runs each generated project's checks. It must
be green before you report done. Note what it does *not* cover: it never runs
the generated `.github/workflows/`, and beyond the `check:hook:case` smoke test
it never exercises the shipped agent files. A finding about a skill or a
workflow needs a hand run in a rendered case.

Then summarise: what was accepted and implemented, what was declined and where
the reasoning now lives, and what still needs a human decision.
