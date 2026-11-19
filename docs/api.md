# The context

`activate(ctx)` receives one `Context`. Everything an extension can do goes through it, and everything on it
is a `Protocol` of `kubescope.sdk`: the app implements it, and an extension never imports the app.

```python
from kubescope.sdk import Context


def activate(ctx: Context) -> None: ...
```

A service that needs a permission raises `PermissionDenied` when the extension did not ask for it in its
manifest. Calls that read a cluster or an AWS account take a while: make them off the UI thread with
`ctx.ui.run_action`.

## Identity and state

| Member | What it gives |
| ------ | ------------- |
| `ctx.id` | The id of the extension, as its manifest says |
| `ctx.permissions` | The permissions its manifest asked for, as a `frozenset` |
| `ctx.settings` | Preferences of its own: `get(key, default)` and `set(key, value)`. Anything JSON can hold. They are saved with the app's settings and no other extension sees them |
| `ctx.data_directory` | A folder that is its own, for files it writes down. It may not exist yet: create it |
| `ctx.current_context` | The cluster context the window is on, or `None` |
| `ctx.snapshot()` | What the window shows, in words |
| `ctx.app` | `write_mode`, `language`, `resolved_language`, `language_name`, `language_names` |
| `ctx.on_unload(callback)` | Call `callback` when the extension is unloaded, to close what it created |

## Events

`ctx.events.on(event, handler)` calls `handler` with keyword arguments on every `event` and returns the
function that stops it. Handlers are removed when the extension is unloaded. A handler that raises is logged
and skipped.

| Event | Payload |
| ----- | ------- |
| `CONTEXT_CHANGED` | `context: str \| None` |
| `WRITE_MODE_CHANGED` | `write_mode: bool` |
| `THEME_CHANGED` | none |
| `LANGUAGE_CHANGED` | none |
| `SHUTDOWN` | none |

Accept `**_` in a handler so that a payload added later does not break it.

## Reading a cluster: `ctx.cluster` · `cluster.read`

`ClusterAccess` reads with the credentials and the kubeconfig of the context you name. A failure raises
`ClusterError`.

| Call | Returns |
| ---- | ------- |
| `get_workloads(context, namespace=None, kinds=...)` | `(namespaces, workloads)` |
| `get_pods(context, namespace=None)` | `(namespaces, pods)` |
| `get_pod_logs(context, namespace, pod_name, container, tail_lines=500, since_time=None, since_seconds=0, limit_bytes=0)` | The log as text |
| `get_pod_container_usage(context, namespace, pod_name)` | CPU and memory by container, or `None` |
| `get_usage(context, namespace=None)` | Usage by `(kind, namespace, name)` |
| `get_resources(context, namespace, kind)` | `(namespaces, resources)` of any kind |
| `get_resource_details(context, kind, namespace, name)` | The document of one resource |
| `describe_kube()` | The programs and kubeconfig the app reads the cluster with, in words |

The models (`Workload`, `PodInfo`, `ClusterResource`, `NodeInfo`, `EventInfo`, ...) are frozen dataclasses in
`kubescope.sdk.models`.

## Changing a cluster: `ctx.writes` · `cluster.write`

Every call raises `WriteModeOff` unless the person turned the write mode on, so ask the person before you
call one, and tell them why when it is refused. Each call is made off the UI thread.

`scale_deployment`, `restart_deployment`, `evict_pod`, `delete_pod`, `delete_resource` and
`replace_resource`, each with the context, namespace and name.

## The AWS account: `ctx.aws` · `aws.read`

| Call | What it does |
| ---- | ------------ |
| `uses_aws(context)` | Whether this computer works with AWS: an account plugged in, an SSO profile, or an EKS context |
| `scope(context)` | `AwsScope(region, profile, account)` of an EKS context; `ClusterError` when it is not one |
| `regions()` | The AWS regions |
| `run(context, command, region="")` | The JSON answer of an AWS CLI command such as `["rds", "describe-db-instances"]`, with the profile or keys of the context |

`run` only reads: the app accepts a service and a verb from a list (RDS `describe-` and `list-` and the
download of a log, EC2 `describe-`, EKS `describe-` and `list-`, Systems Manager
`describe-instance-information`) and refuses every other command and every option that changes who or where
it asks (`--profile`, `--region`, `--endpoint-url`, `--output`, `--cli-*`, `--debug`, `file://`). The keys
stay in the app. If your extension needs another service, ask for it in an issue.

## Forwards: `ctx.forwards` · `forward`

`port_in_use(port)` and `start_ssm(context, title, command, local, target)`, which runs the
`aws ssm start-session` that forwards a port to a database and shows it on the Forwards page. It needs the
write mode, accepts only the session the app builds (a port forwarding document, an EC2 instance as target)
and returns `False` when the local port is in use.

## The window: `ctx.ui` · `ui.window`

`ctx.ui` is `None` when the app runs without a window (a terminal command).

| Member | What it does |
| ------ | ------------ |
| `window`, `central` | The main window and the widget panels in the corner sit on, for parenting your widgets |
| `show_message(icon, title, text)` | A message box; `icon` is `information`, `warning` or `critical` |
| `run_action(function, on_success, *args, on_error=None, quiet=False)` | Calls `function(*args)` off the UI thread; the answer comes to `on_success`, a failure to `on_error(message)` or to the app's own error handling |
| `pick_item(title, label, items)` | A select; returns `(item, accepted)` |
| `show_json(title, document)` | A document in a Details tab |
| `open_log(title, name, read)` | A text in a Logs tab, with a refresh button that calls `read` off the UI thread |
| `style_box(box)` | Gives a message box the buttons of the window |
| `show_settings(section="")` | Opens the Settings |
| `themed(color, text=False)` | A color of the light theme as it is in the theme in use |
| `reserve_corner(owner, pixels)` | Keeps the corner of the window clear for your own panel |

Your widgets are plain Qt (`PySide6`). The app's style sheet applies to them, so a button with
`setProperty("variant", "primary")` or `"secondary"` looks like the app's own. Use `ctx.ui.themed` for any
color you draw yourself.

## Doing what a person does: `ctx.invoke`

`ctx.invoke(command, report=callable, **arguments)` calls a command of the window by name. `report` receives
the text that says why a command could not do what was asked.

| Command | Arguments |
| ------- | --------- |
| `open_view` | `view` |
| `set_namespace` | `namespace` |
| `search` | `text`, `regex=False`, `case=False` |
| `switch_context` | `context` (returns `True` when the window is on it) |
| `open_page` | `page`: `overview`, `workloads_overview` or `settings` |
| `switch_tab` | `title` |
| `show_logs` | `namespace`, `pod`, `container=""` |
| `refresh` | none |
| `show_details` | `kind`, `namespace`, `name` |

An extension can offer its own commands with `ctx.register_command(name, command)`, named
`<id>.<name>`, and other extensions call them with `invoke`.

## Programs of the computer: `subprocess`

`kubescope.sdk.programs` finds a program even where the path of the app does not reach it (an app started
from a menu has a shorter path than a terminal), and `kubescope.sdk.flatpak` runs a command on the host when
the app is a Flatpak. Both are plain functions, not services: the permission `subprocess` tells the person
that the extension runs programs. Run them off the UI thread.

## Helpers

| Module | What it is |
| ------ | ---------- |
| `kubescope.sdk.errors` | `ClusterError`, and `first_line(text)` for one-line summaries |
| `kubescope.sdk.redact` | `redact(text)` scrubs tokens, passwords and keys from a text before it is logged or sent |
| `kubescope.sdk.paths` | `config_directory()` |
| `kubescope.sdk.timezone` | `to_zone(moment)` and `zone_now()` in the time zone of the settings |
| `kubescope.sdk.ansi` | Colors and a small Markdown renderer for a terminal |
| `kubescope.sdk.programs`, `flatpak` | See above |

## What is not wired yet

- `ctx.add_dock` and `ctx.add_tab_kind` are part of the API and are recorded by the app, but the window does
  not show them yet. For a panel in the corner, build your widget on `ctx.ui.central` and call
  `ctx.ui.reserve_corner` as the Gabi extension does; for details and logs use `show_json` and `open_log`.
- `RdsInstance`, `RdsLogFile` and `SsmTarget` are in `kubescope.sdk.models` for historical reasons; they
  belong to the AWS extension and will move.
