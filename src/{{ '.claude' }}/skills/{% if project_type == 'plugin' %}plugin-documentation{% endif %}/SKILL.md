---
name: plugin-documentation
description: Write or revise the user-facing text of a DataIntegration task - the @Plugin label, description and documentation, and the descriptions of its parameters and actions. Use whenever a @Plugin, PluginParameter or PluginAction block is added or edited.
---

# Documenting a DataIntegration task

This governs the text a user reads inside eccenca Corporate Memory: the `label`,
`description` and `documentation` of the `@Plugin` decorator, and the
`description` of every `PluginParameter` and `PluginAction`. It does not govern
Python docstrings, error messages or identifiers. Those are read by developers
and follow the ordinary code conventions.

`documentation` is rendered as Markdown, so backticks, `**bold**` and links all
work. `description` is a single line shown next to the task in the task list.

## Ground every claim in the code

Read `execute()` and the constructor before describing what a task does. Never
write behaviour you have not confirmed, and never carry a claim over from the
previous version of the text just because it was already there.

When the real behaviour is awkward, write it down anyway. A failure that does
not stop the task, a report that keeps only the last of several errors, a
dependency that is silently left in place: users meet these whether or not the
documentation admits them. Do not fix such things during a documentation pass.
Document them accurately, and collect them as findings for the user to turn
into their own work items.

## The documentation never restates a parameter

The task documentation and the parameter descriptions have separate jobs. The
documentation explains the task; each parameter description explains that
parameter. Saying the same thing twice means the two will disagree after the
next change.

A parameter may be named in the documentation only where it changes the *shape*
of the task, because the shape cannot be understood without it: an input port
that appears or disappears, or modes that exclude each other. Even then, say
what happens to the task rather than what the parameter does.

```
Wrong - this is the parameter description, moved
    If the Manifest JSON parameter is provided, the manifest is read from it
    and the input port is removed. If it is left empty, the manifests come
    from the input port.

Right - this is the shape of the task
    Manifests arrive on the input port, which is replaced by a parameter when
    the manifest is configured on the task itself.
```

## Four beats, in this order

1. **What the task does.** One or two sentences, in the present tense.
2. **What flows through the ports.** What arrives, what leaves, in what form.
   When there is no output port, say so and say what that means: the task is a
   terminal step and hands nothing on.
3. **Where the task sits.** How it combines with its sibling tasks, and the
   chain it usually appears in.
4. **Caveats and surprising behaviour.** What the task trusts without checking,
   what it will not do, what a user is likely to get wrong.

Length follows content. Most tasks land somewhere around fifteen to twenty
lines. Do not pad a simple task to match a complex one, and do not cut a
complex one down to match a simple one. A task with three mutually exclusive
modes genuinely needs more words than one with a single input port.

## Parameters

The first sentence says what the parameter controls. Add further sentences only
for interactions a user cannot guess: which other parameter it excludes, which
port it brings into existence, why the default is what it is.

Boolean parameters start with `If enabled, ...` and describe the enabled state.
Mark a parameter `advanced=True` when a user can reasonably ignore it, and let
the description explain the situation in which they cannot.

## Choice parameters explain their values in the labels

The dropdown is where the value is chosen, so that is where the explanation
belongs. Put it in the choice label and keep the description to the one line
that says what the parameter controls.

```python
IMPORT_CONFLICT_POLICIES = OrderedDict(
    [
        (REPLACE, "Replace - delete the installed package, install the new one"),
        (SKIP, "Skip - leave the installed package untouched, continue"),
        (FAIL, "Fail - abort the task with an error"),
    ]
)
```

Never spell the values out a second time in the description. If a value needs
more explanation than a label can hold, that belongs in the caveats beat of the
task documentation, not in a bulleted repeat of the dropdown.

## Cross-references

Refer to sibling tasks by their label in bold, matching how they appear in the
task list, and do not link them. The label is what the user is looking at, and
nothing can rot. Links to documentation outside the package are fine where a
stable URL exists.

## Naming the product

eccenca Marketing governs how the product is named in anything a user can read.

- The **first mention in each block of user-visible text** is the full name,
  **eccenca Corporate Memory**. The block is the unit, not the file: a user may
  meet a `documentation` block, a `description` or a README without having seen
  any of the others.
- **Plain "Corporate Memory" afterwards.** Repeating the full name in every
  sentence reads badly, and naming the product more often than the text needs
  reads worse.
- **"CMEM" is never acceptable** in prose, at any position.
- **Identifiers are exempt everywhere** and stay verbatim - `cmem-plugin-base`,
  `cmem_plugin_*` module paths, `CMEM_BASE_URI`, `documentation.eccenca.com`.
  `cmemc` is exempt for a stronger reason: it is the separately branded eccenca
  command line client, a product name of its own rather than an abbreviation, so
  it is never expanded.

In practice a short text - a `description`, a parameter description - is usually
better with no product name in it at all. The task is already running inside the
product, so naming it there spends words on context the reader has, and the
question of which form applies does not come up. The `example_workflow.py` this
project shipped with is the model: its documentation block never names the
product.

## Vocabulary

Use one word per concept across the whole package. Two names for the same thing
read as two different things.

If the repository carries a glossary, apply it and extend it rather than
inventing a synonym. Do not infer terminology from what the existing code says
most often: majority usage is frequently the wrong usage, and counting
occurrences will confidently give you the term the team has been trying to
retire. When no glossary exists and the choice is not obvious, ask.

Spelling follows the surrounding eccenca libraries, which use American English.

## Finish the change

Add a `CHANGELOG.md` entry under `### Changed` in the `## [Unreleased]`
section. The trigger is whether a user would notice, not whether behaviour
changed, so reworded descriptions and restructured documentation both qualify.

Then check the result as a user would see it, by loading the descriptors rather
than rereading the source:

```python
from cmem_plugin_base.dataintegration.discovery import discover_plugins

for plugin in discover_plugins("<package_dir>").plugins:
    print(plugin.label, plugin.description)
    print(plugin.documentation)
    for parameter in plugin.parameters:
        print(" ", parameter.label, "-", parameter.description)
```

This catches an unrendered f-string, a description that reads well in the
source and badly in a list, and a choice label that is still the bare key.
