---
name: plugin-implementation
description: Write or change the code of a DataIntegration task - reaching a Corporate Memory deployment, logging, the plugin icon, declaring ports, honouring cancellation, reporting progress, and writing custom parameter types with autocompletion. Use whenever a WorkflowPlugin or TransformPlugin body, its @Plugin block, its ports or its parameter types are added or edited.
---

# Implementing a DataIntegration task

These are the conventions the eccenca plugin fleet converged on. They are not
style preferences - each one exists because the obvious alternative behaves
worse inside a running workflow.

## Reaching a Corporate Memory deployment

Use [`cmem-client`](https://pypi.org/project/cmem-client/), declared as
`cmem-client = "^1.0.0"`. Build it from the context you were handed rather than
from configuration:

```python
from cmem_client.client import Client

def execute(self, inputs: Sequence[Entities], context: ExecutionContext) -> Entities | None:
    client = Client.from_context(context=context)
```

`Client.from_context()` carries the executing user's identity. In tests, where
there is no execution context, use `Client.from_env()` instead.

Sub-APIs live under the same package, for example
`from cmem_client.repositories.graphs import ImportConflictPolicy`.

**`cmempy` is deprecated.** Do not add imports from `cmem.cmempy.*`, and do not
use `setup_cmempy_user_access()`. Plenty of existing plugins still call it -
that is legacy, not a pattern to copy. `cmem-plugin-base` continues to depend
on `cmem-cmempy` transitively, which does not make it available for new code.

## Logging

The base class already provides a logger as `self.log`. Use it:

```python
self.log.info("Fetched %s records", count)
```

Do not create a module logger with `logging.getLogger(__name__)`. `self.log` is
a `PluginLogger` that routes into DataIntegration under
`plugins.python.<plugin_id>`, so its output is visible where an operator looks
for it; a private logger is not.

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

## Declaring ports

Say what the task accepts and produces; do not leave it implicit.

```python
input_ports=FixedNumberOfInputs([FixedSchemaPort(schema=MY_SCHEMA)]),
output_port=FixedSchemaPort(schema=MY_SCHEMA),
```

Use `UnknownSchemaPort` when the schema is only known at runtime, and
`FlexibleNumberOfInputs` when the task genuinely accepts any number of inputs.
A task that consumes nothing declares `FixedNumberOfInputs([])`.

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
