---
name: plugin-implementation
description: Write or change the code of a DataIntegration task - reaching an eccenca Corporate Memory deployment, logging, the plugin icon, declaring ports, honouring cancellation, reporting progress, and writing custom parameter types with autocompletion. Use whenever a WorkflowPlugin or TransformPlugin body, its @Plugin block, its ports or its parameter types are added or edited.
---

# Implementing a DataIntegration task

These are the conventions the eccenca plugin fleet converged on. They are not
style preferences - each one exists because the obvious alternative behaves
worse inside a running workflow.

## Reaching an eccenca Corporate Memory deployment

Build the client from the context you were handed rather than from
configuration, using `get_client()`:

```python
from cmem_plugin_base.dataintegration.client import get_client

def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
    client = get_client(context)
```

What comes back is a [`cmem-client`](https://pypi.org/project/cmem-client/)
`Client` carrying the executing user's identity. In tests, where there is no
execution context, use `Client.from_env()` instead.

**`get_client()` and `Client.from_context()` are the same call.** `get_client()`
is `Client.from_context(context=context)` with a guard in front of it: a context
without a `UserContext` raises `Context has no UserContext.` rather than failing
further downstream, and it is reached through `cmem-plugin-base`, which every
plugin already depends on. Prefer it in new code - but a plugin already calling
`Client.from_context()` is correct and must not be "brought in line", since
rewriting it the other way is the direction that loses the check.

Do not pass `self.log` to the `logger` argument of either call. Both want a
`logging.Logger` and `self.log` only resembles one - see *Logging* below.

Sub-APIs live under the cmem-client package, for example
`from cmem_client.repositories.graphs import ImportConflictPolicy`. A project
importing from `cmem_client` directly declares `cmem-client = "^1.0.0"`, so that
deptry sees a direct dependency rather than a transitive one.

**`cmempy` is deprecated.** Do not add imports from `cmem.cmempy.*`, and do not
use `setup_cmempy_user_access()`. Plenty of existing plugins still call it -
that is legacy, not a pattern to copy. `cmem-plugin-base` continues to depend
on `cmem-cmempy` transitively, which does not make it available for new code.

## Logging

The base class already provides a logger as `self.log`. Use it:

```python
self.log.info(f"Fetched {count} records")
```

Do not create a module logger with `logging.getLogger(__name__)`. `self.log` is
a `PluginLogger` that routes into DataIntegration under
`plugins.python.<plugin_id>`, so its output is visible where an operator looks
for it; a private logger is not.

`PluginLogger` is **not** a `logging.Logger`, it only resembles one. It offers
`debug()`, `info()`, `warning()` and `error()`, and each takes a single, already
formatted string. The `logging` idiom
`self.log.info("Fetched %s records", count)` raises `TypeError` at runtime, so
an f-string is the form to use - the ruff rule
`G004` (logging statement uses f-string) is in the `ignore` list accordingly.
The same gap is why `self.log` cannot be passed as a `logger` argument.

## The icon

Ship an SVG beside the plugin module and reference it by package:

```python
@Plugin(
    label="My task",
    icon=Icon(file_name="my_task.svg", package=__package__),
    ...
)
```

Always `package=__package__` rather than a hard-coded package name - it keeps
working when the module moves or the project is renamed.

What the SVG contains matters as much as where it lives, and neither
`task check` nor plugin discovery says a word about it - a wrong icon is only
found by somebody looking at the workspace.

Give the mark no colour of its own: put `fill="currentColor"` (or
`stroke="currentColor"`) on the root `svg` and name no `fill` on the shapes, so
it follows the surrounding text colour and stays legible on a light and a dark
workspace alike. Hard-coding a brand colour produces the one icon in the task
list that looks broken when the theme changes. Leave the background
transparent - no full-size `<rect>` - because every other icon in that list is,
and an opaque tile reads as a coloured block among them.

`cmem-plugin-parameters` and `cmem-plugin-pyshacl` are the icons to copy the
shape of.

## Declaring ports

Say what the task accepts and produces; do not leave it implicit.

```python
input_ports=FixedNumberOfInputs([FixedSchemaPort(schema=MY_SCHEMA)]),
output_port=FixedSchemaPort(schema=MY_SCHEMA),
```

A task that consumes nothing declares `FixedNumberOfInputs([])`.

Two independent things are being declared here, and they are easy to confuse.
`FixedNumberOfInputs` and `FlexibleNumberOfInputs` say how many inputs the task
takes. `FixedSchemaPort`, `FlexibleSchemaPort` and `UnknownSchemaPort` say what
a single port's schema is. `FlexibleNumberOfInputs` makes every one of its
inputs a flexible schema port, which is why the two get read as one choice.

Prefer a **fixed** schema on every port, and reach for a flexible one only when
the task really cannot know its schema. A fixed schema lets DataIntegration
check a connection while the workflow is being drawn, which turns a runtime
abort into an error the author sees in the editor.

A flexible **input** schema costs more than it looks - whether it is written
`FixedNumberOfInputs([FlexibleSchemaPort()])` or `FlexibleNumberOfInputs()`.
An operator declaring one has been seen to reject a file dataset outright,
aborting before it receives a single entity, with an entity count of 0 and

```text
array assignment index out of range: 0
```

A flexible port requests no paths, and reading a file dataset with an empty
requested schema appears to be the trigger - the same file read by a transform,
which requests named paths, is fine. The message names an array index, so it
reads like a bug in the plugin rather than a schema negotiation that never
happened. If a "process whatever arrives" task has to exist, say in its
documentation that its input comes from another task rather than from a dataset.

`UnknownSchemaPort` is the safer of the two escapes: it says the schema is not
known in advance, without asking DataIntegration to adapt this port to whatever
is connected.

A port can also depend on a parameter's current value instead of being fixed
at write time. Assign `input_ports`/`output_port` in `__init__` from a
condition on `self`, and the port the editor shows follows the parameter:

```python
self.input_ports = (
    FixedNumberOfInputs([])
    if self.source_file.strip()
    else FixedNumberOfInputs([FixedSchemaPort(schema=MY_SCHEMA)])
)
```

This is the standard way to offer two mutually exclusive ways of supplying the
same thing - a parameter here versus a connected input - rather than accepting
both and picking one at runtime. A boolean or an enum parameter drives the same
pattern with an `if`/`match` in place of the empty-string check.

## Honouring cancellation

A long-running task must stop when the user cancels the workflow. Check the
status inside the entity loop, and guard the access:

```python
from contextlib import suppress

for entity in inputs[0].entities:
    with suppress(AttributeError):
        if context.workflow.status() == "Canceling":
            break
    ...
```

The `suppress(AttributeError)` is required, not defensive noise:
`context.workflow` is absent in some contexts - notably the test contexts - and
an unguarded check raises there while working in production.

## Reporting progress

Report through the execution context so the workflow UI can show what is
happening:

```python
context.report.update(
    ExecutionReport(
        entity_count=processed,
        operation="write",
        operation_desc="entities written",
    )
)
```

- `operation` is a short label. Use **`read`**, **`write`**, **`wait`** or
  **`done`**; do not invent new verbs, and do not use past tense.
- `operation_desc` describes the counted thing in plural, so it reads correctly
  after the number: `"entities written"`, `"files uploaded"`.
- Update **inside** the loop, not only once at the end. A report emitted after
  the work is finished shows a user nothing while the task is running, which is
  exactly when they are looking.

## A constructor with six or more parameters

Ruff's `PLR0913` and `PLR0917` both complain about a long argument list, and a
task's constructor takes one argument per `PluginParameter` - so its arity is
decided by the configuration surface the task offers, not by a style choice.
Neither escape ruff suggests is available: keyword-only arguments change the
signature DataIntegration instantiates, and folding parameters into one object
breaks the one-argument-per-parameter mapping the framework depends on.

This is the standing exception the lint rules describe, so it needs no fresh
decision. Suppress both codes on the `def`, with the reason above it:

```python
# A plugin constructor takes one argument per PluginParameter, so its arity is
# fixed by the plugin's configuration surface, not by a style choice here.
def __init__(  # noqa: PLR0913, PLR0917
    self,
    ...
```

`PLR0917` became a stable rule in ruff 0.16, so a task that passed before may
start failing on it without anything in the task changing. Suppress it on the
constructor only - it stays a real finding on an ordinary function, which is
why it is not in the `ignore` list in `pyproject.toml`.

## Parameters that carry secrets

A password, token or API key is typed, never a plain string:

```python
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType

PluginParameter(
    name="api_key",
    label="API key",
    param_type=PasswordParameterType(),
)
```

The value arrives as a `Password`; call `.decrypt()` only where it is used.
Typing it as `str` puts the secret in plain text in the task configuration and
in the project export.

## Custom parameter types

A `PluginParameter` without an explicit `param_type` gets one derived from the
constructor's type annotation, and **that derivation cannot handle a union**.
An annotation like `JinjaCode | str` or `str | Password` raises
`TypeError: issubclass() arg 1 must be a class` while the module is imported,
which aborts discovery for the **whole package** - every plugin the package
ships disappears from the workspace, `task check` stays green, and the
traceback only shows up in `PluginDiscoveryResult.errors`.

So annotate a single type, or pass `param_type` explicitly. Writing a union is
almost always the moment you needed `param_type` anyway: `cmem-plugin-ssh`
declares `private_key: str | Password` and works only because it also passes
`param_type=PasswordParameterType()`.

Reach for a shipped type first - `ChoiceParameterType`, `GraphParameterType`,
`DatasetParameterType`, `PasswordParameterType`, and the `code`, `multiline`
and `resource` types. Write your own only when the value is a thing the user
should pick from a list that only your plugin can produce: a folder on a
remote host, a collection in a store, a model offered by an API.

Subclass `StringParameterType`, not `ParameterType` directly - the value is
carried as a string and `StringParameterType` already handles that:

```python
from typing import Any, ClassVar

from cmem_plugin_base.dataintegration.context import PluginContext
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType


class CollectionParameterType(StringParameterType):
    """Autocomplete the collections available on the configured server."""

    allow_only_autocompleted_values: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Return the collections matching all query terms."""
        results = [
            Autocompletion(value=name, label=f"{title} ({name})")
            for name, title in self._fetch(context)
        ]
        if not query_terms:
            return results
        return [
            r
            for r in results
            if all(term.lower() in (r.label or r.value).lower() for term in query_terms)
        ]
```

- An **empty `query_terms` must return everything**. That is the list the user
  sees before typing, and returning nothing looks like a broken parameter.
- Match against every term, not any of them - the UI splits what the user typed
  on whitespace.
- Return a **stable order**. Sort at the end; do not deduplicate with `set()`
  after sorting, because that throws the ordering away again.

### The flags

- `allow_only_autocompleted_values = True` makes the parameter a closed
  vocabulary: the UI refuses values that did not come from your list. Set it
  when a value the server does not know is always an error.
- `autocomplete_value_with_labels = True` tells the UI the labels matter and
  must be shown instead of the raw values.
- Implement `label()` when a stored value is not human-readable on its own. A
  saved task shows the raw value until `label()` resolves it, so a task
  configured last week displays an opaque id without it.

### Depending on other parameters

An autocompletion that needs a hostname, or credentials, declares the
parameters it reads:

```python
autocompletion_depends_on_parameters: ClassVar[list[str]] = [
    "hostname",
    "port",
    "password",
]
```

Their values arrive in `depend_on_parameter_values` **positionally, in exactly
this order** - `depend_on_parameter_values[2]` is `password` only because it is
third in the list. Reordering the list silently repoints every index, so read
them once at the top of `autocomplete()` and unpack by name:

```python
hostname, port, password = depend_on_parameter_values
```

A dependency that is itself a secret arrives as a `Password`, not a string, and
needs `password.decrypt()` before use.

Until every declared parameter has a value, no autocompletion happens at all -
so keep the list to what you genuinely need. Each extra entry is one more field
the user must fill before the list appears.

DataIntegration also **clears** a dependent parameter's own value whenever one
of the parameters it declares changes, and that propagates: in a chain of
token -> resource -> sub-resource, changing the token clears the resource,
which clears the sub-resource. Two things follow, and both change how such a
chain is designed. A chained parameter never holds a value left over from an
earlier selection, so there is no stale combination to validate against and no
caveat to write into the task documentation about one. And a chained parameter
can safely be made mandatory, because a user who invalidates it is asked to
choose again rather than being stranded on a value they cannot correct.
