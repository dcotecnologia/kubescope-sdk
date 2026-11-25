# 8. Testing

[Wiki](README.md) · previous: [A chat with an assistant](7-chat.md) · next: [Recipes](9-recipes.md)

A test of an extension imports no Qt class either. The app lends a kit, `kubescope.extensions.testing`, and the
real components, `kubescope.extensions.components.UiComponents`, which draw on the offscreen platform. The
app is a **development dependency** of the tests of the extension (not of the extension):

```toml
[dependency-groups]
dev = ["kubescope>=2.9.0", "pytest>=9.2.0", ...]
```

## The fixture file

```python
# tests/conftest.py
import pytest
from kubescope.extensions import testing
from kubescope.extensions.components import UiComponents


@pytest.fixture(autouse=True)
def delete_the_windows():
    """A window that outlives a test crashes the run when it ends."""
    yield from testing.cleanup()


@pytest.fixture(autouse=True)
def no_blocking_dialogs(monkeypatch):
    testing.refuse_modals(
        monkeypatch
    )  # a test that opens a dialog fails instead of hanging


class FakeUi:
    """`ctx.ui`: runs an action at once and remembers what was shown."""

    def __init__(self) -> None:
        self.components = UiComponents()
        self.window = self.components.widget()
        self.messages = []

    def themed(self, color, text=False):
        return color

    def show_message(self, icon, title, text):
        self.messages.append((icon, title, text))

    def run_action(self, function, on_success, *arguments, on_error=None, quiet=False):
        try:
            answer = function(*arguments)
        except Exception as error:
            if on_error is None:
                raise
            on_error(str(error))
            return
        on_success(answer)
```

The fake `ui` runs an action **at once**, so a test needs no thread and no waiting. Give a `UiComponents()` as
its `components`: it is the real thing.

## The kit: `kubescope.extensions.testing`

| Call | What it does |
| ---- | ------------ |
| `application()` | the application of the tests, made when it is first asked |
| `settle()` | let what was posted happen (a timer of 0, a deletion) |
| `cleanup()` | for a fixture: delete the windows a test showed |
| `find(widget, kind)`, `find_all(widget, kind)` | the first, or all, of the widgets of that kind in `widget` |
| `buttons(widget)` | the buttons in `widget`, by their text |
| `texts(widget, kind="label")` | the text of every widget of that kind (`"text"` reads `toPlainText()`) |
| `badge_of(item)` | the colors a cell was given as a badge, or `None` |
| `click(widget, x=5, y=5, kind="press", button="left")` | a mouse event on a widget: `press`, `release` or `move`, of the `left` or `right` button |
| `refuse_modals(monkeypatch)` | dialogs and message boxes raise instead of blocking |
| `answer_dialogs(monkeypatch, act)` | run `act(dialog)` when a dialog is executed; it is rejected unless `act` returns a number |
| `still_panels(monkeypatch)` | the panels of the app show and go at once |
| `png_bytes(width, height, color)`, `write_png(path, ...)` | a solid picture, made by hand |

`kind` is `button`, `label`, `combo`, `text`, `table`, `check`, `line`, `spin`, `time`, `frame`, `scroll` or
`list`.

## What to assert

```python
def test_the_instances_are_listed(ctx):
    page = RdsPage(ctx)
    page.widget.show()
    page.shown()

    table = page.table
    assert table.rowCount() == 2
    assert table.item(0, 0).text() == "orders"
    assert testing.badge_of(table.item(0, 4)) is not None  # the status is a badge
    assert page.notice.text() == "2 instances"


def test_the_menu_of_a_row(ctx, monkeypatch):
    page = RdsPage(ctx)
    page.load()
    offered = []
    monkeypatch.setattr(
        page.components,
        "show_menu",
        lambda menu, table, x, y: offered.append([a.text() for a in menu.actions()]),
    )
    page._menu(5, page.table.rowViewportPosition(0) + 5)
    assert offered == [["Details", "Logs"]]


def test_a_click_on_a_header_sorts(ctx):
    page.sorter.clicked(0)  # ascending
    page.sorter.clicked(0)  # descending


def test_a_dialog(ctx, monkeypatch):
    testing.answer_dialogs(
        monkeypatch, lambda dialog: testing.buttons(dialog)["Close"].click()
    )
    page.forward(instance)


def test_a_confirmation(ctx, monkeypatch):
    monkeypatch.setattr(
        UiComponents,
        "confirm",
        lambda self, parent, title, text, ok="OK", detail="", warning=False: True,
    )
```

Patch the **component** (`UiComponents.confirm`, `page.components.show_menu`, `UiComponents.open_url`) rather than
a Qt class: it is the seam the SDK gives you.

## Timers, workers and the clock

- A `timer` is a real timer: assert `timer.is_active()` and call its `timeout.emit()` to make it tick.
- `background` runs a real thread: wait for it with `handle.wait(3000)` and `testing.settle()`, or give your
  page a fake `ui` whose `components.background` runs the function at once.
- `after(ms, owner, callback)`: patch `page.components.after` to record the call.

## Translating

Without the app a text comes back as it is. To see a test with another language, give the SDK a translator:

```python
from kubescope.sdk import set_translator

set_translator(lambda context, text: {"Instances": "Instâncias"}.get(text, text))
```

and put it back with `set_translator(None)` after.

## The guard

Each extension has this test; copy it:

```python
def test_it_imports_no_qt_class_but_takes_them_from_the_sdk() -> None:
    offenders = []
    for path in sorted([*SRC.rglob("*.py"), *TESTS.rglob("*.py")]):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            offenders += [
                f"{path.name}: {name}"
                for name in names
                if name.split(".")[0] in ("PySide6", "shiboken6")
            ]
    assert offenders == []
```
