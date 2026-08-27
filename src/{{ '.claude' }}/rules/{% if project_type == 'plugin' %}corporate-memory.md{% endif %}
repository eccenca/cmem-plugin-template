# This project is an eccenca Corporate Memory plugin

The package provides one or more DataIntegration tasks built on
[cmem-plugin-base](https://github.com/eccenca/cmem-plugin-base). A task is a
class decorated with `@Plugin`, registered through `WorkflowPlugin` or
`TransformPlugin`, and configured by `PluginParameter` entries.

The text a user reads inside Corporate Memory - the plugin label, description
and documentation, and every parameter and action description - follows the
conventions in the `plugin-documentation` skill. Use that skill whenever you
add or edit one of those blocks.

Tests follow the conventions in the `plugin-testing` skill.

The code itself - reaching a deployment, logging, the icon, port declarations,
cancellation and progress reporting - follows the `plugin-implementation`
skill. Use it whenever you write or change a task body, its `@Plugin` block or
its ports.

## Talking to a deployment

Plugin code reaches a deployment through
[`cmem-client`](https://pypi.org/project/cmem-client/), built from the context
it was handed: `get_client(context)`. **`cmem.cmempy.*` is
deprecated** - existing calls to it are legacy, and no new code should import
it. The `plugin-implementation` skill has the detail.

Integration tests and the install tasks talk to a real Corporate Memory
deployment, configured through `cmemc` environment variables in `.env`:
`CMEM_BASE_URI`, `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET` and
`OAUTH_GRANT_TYPE`. Without them, tests marked `needs_cmem` are skipped rather
than failed.

`TestExecutionContext` and `TestPluginContext` need a deployment as well: they
construct a `TestUserContext`, which fetches a real OAuth token when it is
built. A test that constructs one is an integration test, however little the
plugin itself does, and needs the marker.

`task check` therefore changes that deployment when `.env` is populated: it
runs the integration tests, which create their own project and assets and
delete them again afterwards. That is expected and
needs no permission, but it is a real deployment other people may be using, so
never point a test at assets you did not create.

`task install` and `task uninstall` change what is installed in that
deployment. Ask before running them, and never run them to work around a
failing test.
