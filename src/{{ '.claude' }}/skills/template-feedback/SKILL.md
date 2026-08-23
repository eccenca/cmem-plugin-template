---
name: template-feedback
description: Report a finding upstream to the cmem-plugin-template - check what has already been decided, draft a GitHub issue and file it after the user confirms. Use when a template owned file is wrong or in the way, when a lint rule had to be worked around, when a copier update conflict will recur for everyone, or when asked to report something to the template.
---

# Reporting a finding to the template

This project is generated from
[cmem-plugin-template](https://github.com/eccenca/cmem-plugin-template) and
receives changes only through `copier update`. Nothing here flows back on its
own, so a finding that would help other generated projects has to be filed as
an issue on the template repository.

The point is not to log everything that happened. It is to move the small
number of findings that are **about the template** out of this project, where
they die, and into the one place a fix can reach every project.

## Does this belong upstream?

Ask whether the finding would still make sense in a project that has nothing
to do with this one. Concretely, upstream material looks like:

- a lint or typing rule that had to be worked around here and would fire the
  same way anywhere
- a step in `Taskfile.yaml` or the pipeline that is missing, wrong or fails
  identically everywhere
- a statement in `.claude/rules/` or one of the shipped skills that turned out
  to be wrong or out of date
- a `copier update` conflict that every project will hit
- a pattern this project keeps writing by hand that the template could ship

Anything specific to this project - its business logic, its own dependencies,
a task only it needs - is not template feedback. Put those in
`TaskfileCustom.yaml`, in `CLAUDE.md`, or in this project's own tracker.

Wishes count. "The template could ship a skill for X" is a legitimate report
as long as it is argued for projects in general, not just this one.

## Check what has already been decided

Do this before drafting anything. Most findings have been seen before, and a
duplicate costs a maintainer more than it costs you.

1. Search the issues, open **and** closed:

   ```bash
   gh issue list --repo eccenca/cmem-plugin-template \
       --state all --label template-feedback --search "<keywords>"
   ```

   An **open** match means comment there instead of opening a second issue. A
   **closed** match means it was answered already - read the answer and stop.

2. Read the *Deliberate decisions - please do not re-raise these* section of
   the template's `CLAUDE.md`:
   <https://github.com/eccenca/cmem-plugin-template/blob/main/CLAUDE.md>

   That section is the list of findings that were considered and rejected on
   purpose - the GitLab `build` job not needing `ruff`, the `pypi` job being
   manual, the mypy badge, and others. If the finding is there, it is settled.
   Say so and stop.

3. Skim the template's `CHANGELOG.md` for the `## [Unreleased]` section. It may
   already be fixed and waiting for a release, in which case the answer is to
   update once that release is out.

## Draft the issue

Never file without showing the user the exact title and body first, and never
file without their explicit go-ahead in that turn. This is the only step in
this project that publishes something, it is permanent, and the tracker is
public while most generated projects are not.

**Do not name this repository, and do not paste code from it.** Many projects
generated from this template are private, some of them customer specific, and
naming one on a public tracker publishes a relationship that was not yours to
publish. Describe the finding in general terms; write a minimal synthetic
reproduction if one helps. If naming the project is genuinely useful, let the
user add it when they confirm - they know whether it is public.

What the maintainer needs instead of a name, taken from `.copier-answers.yml`:

- `_commit` - the template version this project was rendered from
- `project_type` - `plugin` or `generic`
- whether `github_page` and `pypi` are answered

Title: short and imperative, describing the change to the template - not the
symptom here. Body, following the repository's issue form:

```text
### The finding
<what got in the way, in general terms>

### Why this generalises
<at least one other kind of project this would help>

### Which part of the template
<the file under src/, if known>

### Suggested change
<what the template should do instead>

### Environment
Template version: <_commit>
project_type: <plugin|generic>
github_page answered: <yes|no>
pypi answered: <yes|no>
```

## File it

After the user confirms:

```bash
gh issue create --repo eccenca/cmem-plugin-template \
    --label template-feedback --title "<title>" --body "<body>"
```

This one is not pre-approved in `.claude/settings.json`, so it will ask for
permission. That is deliberate - the prompt is the last checkpoint before
something becomes public.

If `gh` is missing or not authenticated, do not stall and do not look for
another way to publish it. Print the finished title and body together with the
command above, and let the user file it. They can also use the form directly:
<https://github.com/eccenca/cmem-plugin-template/issues/new?template=template-feedback.yml>

## Turning it off

A project that does not want the session end check can create an empty
`.claude/no-template-feedback` file. This skill still works when invoked
directly; only the automatic reminder goes away.
