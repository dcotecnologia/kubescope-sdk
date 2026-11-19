# KubeScope SDK

The API that [KubeScope](https://github.com/dcotecnologia/kubescope) and its extensions are written
against. An extension depends on this project and on nothing else of the app: the app implements
what is described here and hands it to the extension when it starts, as `activate(ctx)`.

> The API is unstable while `API_VERSION` is `"0"`.

## What is in it

| Module | What it is |
| ------ | ---------- |
| `context` | `Context`, what `activate(ctx)` receives, and the services it lends (`Ui`, `App`, `Settings`, `Writes`, `ClusterAccess`), with the permissions and the errors |
| `contributions` | What an extension adds to the app: a panel, a kind of tab, a section of the Settings, a shortcut, a command of the terminal |
| `events` | The events the app tells the extensions about |
| `commands` | The commands of the window that an extension can call |

This package has no dependencies and imports neither the app nor Qt; a test enforces it.

## Develop

```bash
uv sync
uv run pytest tests/test_x.py
uv run ruff check . && uv run ruff format --check .
uv run pyright
```

## License

MIT, like KubeScope.
