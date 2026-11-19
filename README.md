# KubeScope SDK

[![CI](https://github.com/dcotecnologia/kubescope-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/dcotecnologia/kubescope-sdk/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fdcotecnologia%2Fkubescope-sdk%2Fbadges%2Fcoverage.json)](https://github.com/dcotecnologia/kubescope-sdk/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/dcotecnologia/kubescope-sdk)](https://github.com/dcotecnologia/kubescope-sdk/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.15](https://img.shields.io/badge/python-3.15-3776AB.svg?logo=python&logoColor=white)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-D7FF64.svg?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff/)
[![KubeScope SDK](https://img.shields.io/badge/KubeScope-SDK-326CE5.svg?logo=kubernetes&logoColor=white)](https://github.com/dcotecnologia/kubescope)

The contract between [KubeScope](https://github.com/dcotecnologia/kubescope), the Kubernetes desktop
console, and the **extensions** written for it.

An extension is a Python project that depends on this package and on nothing else of the app. KubeScope
implements what is described here and hands it to the extension when it starts, as `activate(ctx)`. The
extension reads clusters, reads an AWS account, draws its own pages, panels and settings, runs programs of
the computer and adds commands to the terminal, always through the services the person allowed it in its
manifest.

```python
from kubescope.sdk import Context


def activate(ctx: Context) -> None:
    ctx.add_page(
        "Cloud",
        "Databases",
        "Overview",
        lambda: build_widget(ctx),
        visible=lambda: ctx.current_context is not None,
    )
```

> **Status.** The API is unstable while `API_VERSION` is `"0"`: names and signatures can still change
> between releases. A manifest declares the API it was written for (`api = "0"`), and the app refuses an
> extension for another one.

## Why an extension

KubeScope stays small and every feature that is not for everyone becomes an extension that can be
installed and uninstalled from **Settings → Extensions**, from a folder or from a GitHub repository. Two
projects are written this way and are good places to read real code:

| Extension | What it does |
| --------- | ------------ |
| [kubescope-gabi](https://github.com/dcotecnologia/kubescope-ai-gabi) | An assistant that answers about the cluster using a coding assistant installed on the computer |
| [kubescope-aws](https://github.com/dcotecnologia/kubescope-aws) | The AWS RDS databases of the account of the selected cluster |

## What an extension can do

| It can | Through | Permission |
| ------ | ------- | ---------- |
| Read workloads, Pods, logs, usage, resources and their documents | `ctx.cluster` | `cluster.read` |
| Scale, restart, evict, delete and replace, in the write mode only | `ctx.writes` | `cluster.write` |
| Read the AWS account of a cluster context (RDS, EC2, EKS, Systems Manager) | `ctx.aws` | `aws.read` |
| Start a port forward to a database through Systems Manager, in the write mode | `ctx.forwards` | `forward` |
| Run programs of the computer | `kubescope.sdk.programs`, `kubescope.sdk.flatpak` | `subprocess` |
| Show messages, run work off the UI thread, show details and logs, add shortcuts, use Qt | `ctx.ui` | `ui.window` |
| Add a page with its entry in the side menu | `ctx.add_page` | `ui.page` |
| Add a section to the Settings | `ctx.add_settings_section` | `ui.settings` |
| Add a command to the `kubescope` terminal program | `ctx.add_cli_command` | `cli` |
| Do in the window what a person does by hand | `ctx.invoke` | none |
| Keep preferences and files of its own | `ctx.settings`, `ctx.data_directory` | none |
| Hear the app: context, theme, language, write mode, shutdown | `ctx.events` | none |
| Offer commands to other extensions and to the app | `ctx.register_command` | none |

See [docs/permissions.md](docs/permissions.md) for what each permission means and what the person sees
before installing.

## Documentation

| Guide | Read it to |
| ----- | ---------- |
| [Getting started](docs/getting-started.md) | Write, run and install your first extension |
| [The manifest](docs/manifest.md) | Know every field of `kubescope-extension.toml` and how it is checked |
| [The context](docs/api.md) | Look up every service and call of `ctx`, with the models and the helpers |
| [Contributions](docs/contributions.md) | Add pages, settings sections, shortcuts, commands and panels |
| [Permissions and security](docs/permissions.md) | Ask for the least, and know what is and is not enforced |
| [Testing](docs/testing.md) | Test an extension without the app, and inside it |

## Install

An extension lists the SDK as a dependency:

```toml
[project]
dependencies = ["kubescope-sdk>=1.0.0"]

[tool.uv.sources]
kubescope-sdk = { git = "https://github.com/dcotecnologia/kubescope-sdk", branch = "main" }
```

The only dependency of the SDK is PySide6, so an extension that draws a widget needs nothing else; the SDK
itself imports neither Qt nor the app, and a test enforces it.

## Design rules

- **A contract, not the app.** `Context` and the services are `Protocol`s. The extension never imports the
  app, so it can be installed, tested and type-checked without it.
- **Least authority.** Every power is a permission in the manifest, shown to the person before anything of
  the extension runs.
- **Read by default, write on purpose.** Everything that changes a cluster or starts a process raises
  `WriteModeOff` until the person turns the write mode on.
- **One extension never stops another.** An extension that raises while loading, or in a handler, is
  logged and taken back; the app and the others carry on.

## Develop

```bash
make setup                       # dependencies and the pre-commit hook
make test FILE=tests/test_sdk.py # one test file; `make test` runs them all
make lint typecheck
```

## License

MIT, like KubeScope.
