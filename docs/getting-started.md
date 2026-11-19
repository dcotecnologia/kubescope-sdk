# Getting started

This guide writes an extension that adds a page to the side menu, runs it in KubeScope with hot reload and
installs it. It takes about ten minutes.

## 1. The layout

An extension is a folder with a `kubescope-extension.toml` and Python code. KubeScope looks for the
manifest in the folder you give it (down at most three levels) and runs the code from the folder, or from its
`src` folder when it has one.

```text
kubescope-hello/
├── kubescope-extension.toml
├── pyproject.toml
├── src/
│   └── kubescope/
│       └── hello/
│           ├── __init__.py        # activate(ctx)
│           └── page.py
└── tests/
```

`kubescope` is a **namespace package** shared by the app, the SDK and the extensions: there is no
`__init__.py` in `src/kubescope/`. Name your package `kubescope.<name>`.

## 2. The manifest

```toml
id = "acme.hello"
name = "Hello"
version = "0.1.0"
api = "0"
entry = "kubescope.hello:activate"
description = "Says hello from the side menu."
author = "ACME"
permissions = ["ui.page", "ui.window"]
```

Every field is described in [manifest.md](manifest.md). Ask only for the permissions you use: the person
sees them before installing.

## 3. The code

```python
# src/kubescope/hello/__init__.py
from kubescope.sdk import Context


def activate(ctx: Context) -> None:
    from kubescope.hello.page import HelloPage

    ctx.add_page(
        "Cloud", "Hello", "Greeting", lambda: HelloPage(ctx), subtitle="A first page"
    )
```

```python
# src/kubescope/hello/page.py
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from kubescope.sdk import CONTEXT_CHANGED, Context


class HelloPage(QWidget):
    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self.label = QLabel()
        QVBoxLayout(self).addWidget(self.label)
        ctx.events.on(
            CONTEXT_CHANGED, lambda context=None, **_: self.show_context(context)
        )
        self.show_context(ctx.current_context)

    def shown(self) -> None:  # optional: called each time the page is opened
        pass

    def show_context(self, context: str | None) -> None:
        self.label.setText(f"Hello, {context or 'nobody'}")
```

`activate(ctx)` runs when the extension is loaded. Whatever it registers (pages, shortcuts, handlers,
commands) is taken back when the extension is unloaded. To close something of your own (a thread, a
process), call `ctx.on_unload(callback)`.

## 4. The `pyproject.toml`

```toml
[project]
name = "kubescope-hello"
version = "0.1.0"
requires-python = ">=3.15,<3.16"
dependencies = ["kubescope-sdk>=0.1.0", "pyside6>=6.12.0"]

[tool.uv.sources]
kubescope-sdk = { git = "https://github.com/dcotecnologia/kubescope-sdk", branch = "main" }

[tool.setuptools.packages.find]
where = ["src"]
namespaces = true
```

The dependency on the SDK is for your editor and tests: when the app runs the extension it gives it the real
services. Do not import anything of `kubescope` but `kubescope.sdk` and your own package; a test like the
one in [testing.md](testing.md) keeps it so.

## 5. Run it with hot reload

In KubeScope open **Settings → Extensions**, tick **Development mode**, press **Install from a folder...**
and pick your `kubescope-extension.toml`. In development mode the folder is **not copied**: it runs where it
is, and the app reloads it when a file changes. Uninstalling it never deletes your folder.

Errors while loading show on the card of the extension, and the full traceback is in the log.

## 6. Install it for everyone

Push the folder to a GitHub repository and tag a release. Anyone can then use **Install from GitHub...** and
type `owner/name` (or the address of the repository). A dialog shows where it comes from, its version, its
permissions and the sha256 of its content before anything of it runs.

## What next

- [The context](api.md) to see what `ctx` offers.
- [Contributions](contributions.md) for pages, settings sections, shortcuts and terminal commands.
- [Permissions and security](permissions.md) before you publish.
- Real examples: [kubescope-aws](https://github.com/dcotecnologia/kubescope-aws) (a page that reads AWS) and
  [kubescope-gabi](https://github.com/dcotecnologia/kubescope-ai-gabi) (a panel, settings and terminal commands).
