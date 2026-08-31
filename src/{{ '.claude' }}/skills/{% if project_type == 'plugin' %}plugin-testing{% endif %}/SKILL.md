---
name: plugin-testing
description: Write or fix tests for a DataIntegration task - what can be tested standalone, when a test needs an eccenca Corporate Memory deployment and how to mark it, and how to create and clean up test assets. Use when adding, changing or debugging tests in this project.
---

# Testing a DataIntegration task

Tests run with `task check:pytest`, which collects coverage and a memray
report. `pytest-dotenv` loads `.env`, so the same eccenca Corporate Memory
credentials the plugin uses are available to the tests.

## Two kinds of test, and the line between them

A test that only exercises Python - a transform plugin, a helper, parameter
validation - runs anywhere and must never require credentials.

Everything else needs a deployment and is marked:

```python
needs_cmem = pytest.mark.skipif(
    os.environ.get("CMEM_BASE_URI", "") == "",
    reason="Needs eccenca Corporate Memory configuration",
)
```

The marker skips rather than fails, which is what keeps the suite green in a
pipeline without secrets. A missing marker turns a contributor's first
`task check` into a failure they cannot fix, so the marker is not optional.

**`TestExecutionContext` needs a deployment.** It builds a `TestUserContext`,
which fetches a real OAuth token on construction. Any test that constructs one
is an integration test and must carry `@needs_cmem`, even when the plugin
itself never calls out. The same is true of `TestPluginContext`.

A test that needs anything *else* - a third party API, a scratch instance to
run integration tests against - declares its own environment variables, named
`TESTING_<SERVICE>_<THING>`, and gates on them the same way:

```python
needs_hcloud = pytest.mark.skipif(
    os.environ.get("TESTING_HCLOUD_TOKEN", "") == "",
    reason="Needs a Hetzner Cloud API token",
)
```

The prefix is what makes it possible to tell, in a `.env` file or in a
group-level list of CI variables, which entries drive the test suite and which
configure the product. Pick it before writing the `skipif`: the name ends up in
`.env`, in the pipeline configuration and in every marker that reads it, so
renaming it later is a change in three places at once.

The Corporate Memory connection variables are the exception. `CMEM_BASE_URI`,
`OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET` and `OAUTH_GRANT_TYPE` keep their
established `cmemc` names, because the plugin and `cmemc` read them too - they
configure the product and are not test-only.

## Testing a workflow plugin

Construct the plugin with its parameters, call `execute()` with the inputs it
expects, and assert on the entities that come back - their number, their values
and the schema paths they are supposed to match:

```python
@needs_cmem
def test_execution() -> None:
    """Test plugin execution"""
    result = MyPlugin(number_of_entities=100).execute(inputs=(), context=TestExecutionContext())
    for entity in result.entities:
        assert len(entity.values) == len(result.schema.paths)
```

Assert the plugin's own contract as well: that an output port declared as
absent really produces none, and that a parameter combination the documentation
calls exclusive is rejected.

## Testing a transform plugin

`transform()` takes a sequence of input value sequences and returns a sequence
of strings. No context, no credentials, so cover the awkward cases here: empty
input, several inputs at once, and the boundaries the implementation actually
computes.

## Test assets in a deployment

A test that needs a project, dataset or graph creates it in a fixture, yields,
and deletes it afterwards - including when the test fails. Name assets after
the package so a leftover is traceable and two projects never collide.

Use `cmem_client` for setup and teardown rather than driving the plugin, so a
broken plugin fails the assertion instead of the fixture. Never point a test at
assets that happen to exist in the deployment: the next person runs the suite
somewhere else.

## Finishing

Run `task check:pytest` before finishing, and `task check` before considering
the change done. Tests are not user visible, so a change that only adds or
fixes tests needs no `CHANGELOG.md` entry - the behaviour change that made the
test necessary does.
