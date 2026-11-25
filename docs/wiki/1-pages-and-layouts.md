# 1. Pages and layouts

[Wiki](README.md) · next: [Tables](2-tables.md)

A page of an extension is a **plain Python object** that holds its widget. It does not subclass a Qt class.

```python
class MyPage:
    def __init__(self, ctx):
        self.ctx = ctx
        c = ctx.ui.components
        self.widget = c.widget(shown=self.shown, hidden=self.hidden)
        ...
        c.page(self.widget, filters=..., actions=..., notice=..., body=..., footer=...)

    def shown(self): ...  # the page was opened
    def hidden(self): ...  # the page was hidden


ctx.add_page("Section", "Group", "Title", lambda: MyPage(ctx).widget)
```

## `widget(shown=None, hidden=None, load=None, save=None)`

The widget of your page, or of your section of the Settings.

| Hook | Called when |
| ---- | ----------- |
| `shown()` | the page is opened (each time) |
| `hidden()` | the widget is hidden |
| `load()` | the Settings open, for a section of the Settings |
| `save() -> bool` | the person saves; return `True` when what was typed was kept, `False` to stop the save |

A hook you do not give is not there, so the app does not call it. For a section of the Settings:

```python
self.widget = c.widget(load=self.load, save=self.save)
ctx.add_settings_section("My extension", lambda: MySettings(ctx).widget)
```

Keep the page object alive as long as its widget: the widget holds the callbacks, and the callbacks hold the
object.

## `page(parent, *, filters=None, actions=None, notice=None, body=None, footer=None)`

Lays `parent` (your `self.widget`) out as the pages of the app are, in this order, top to bottom:

1. `filters` — a row: the select, the search box, the switches;
2. `actions` — a row: the line that says what is listed, and the buttons at the right;
3. `notice` — one widget: a muted note or an error banner;
4. `body` — the table or the cards; it takes what is left of the height;
5. `footer` — a row: a count at the left, a note at the right.

Leave out what the page does not have. The rows are layouts made with `row`:

```python
filters = c.row(
    c.label("NAMESPACE", "filter"),
    self.namespaces,
    self.search,
    c.switch_button("Aa", "Match case"),
    None,
)
actions = c.row(self.summary, None, self.details_button, self.update_button, spacing=6)
footer = c.row(self.count, None, c.label("Data fetched from the cluster", "muted"))
c.page(
    self.widget,
    filters=filters,
    actions=actions,
    notice=self.notice,
    body=self.table,
    footer=footer,
)
```

## `row(*items, spacing=12)` and `column(*items, spacing=10)`

A row (`QHBoxLayout`) and a column (`QVBoxLayout`). An item is:

| Item | Means |
| ---- | ----- |
| a widget | put it in |
| a layout | put it in (`row` inside a `column`, and the other way round) |
| `None` | a stretch: it pushes what follows to the right (or down) |
| `(widget, stretch)` | the widget with that stretch factor, e.g. `(self.search, 1)` |

```python
c.row(logo, None, mark1, mark2)  # logo at the left, marks at the right
c.column(c.label("Title", "title"), c.label("Body", "muted", wrap=True), None)
```

The layouts are real Qt layouts: `layout.setContentsMargins(0, 0, 0, 0)`, `layout.insertWidget(...)` and
`layout.count()` work, as the page of the AWS extension does to add a button before the others.

## `form(rows)`

Rows of a form (`QFormLayout`) for a dialog: `rows` is a sequence of `(text, field)`.

```python
c.form([("Chart", self.chart), ("Repository", self.repository), ("", self.reuse)])
```

## `card(*items, name="", min_height=0)`

A rounded box (`QFrame`) with the look of the cards of the app, with `items` one under the other (same items
as `column`). `name` is its object name, `min_height` its least height.

```python
card = c.card(
    c.row(logo, None, *marks),
    c.label("argo-cd", "title", wrap=True),
    (
        c.label(description, wrap=True, align="top-left"),
        1,
    ),  # takes the room that is left
    c.row(install, None, learn),
    name="pluginCard",
    min_height=190,
)
```

## `scroll(content)`

`content` in a scroll area without a frame; the area takes the width of the page and the content grows
down.

## `spacer(height)`

Empty room `height` pixels high, between the parts of a `column`.

## `grid_scroll(spacing=12)` and `grid_cell(grid, widget, row, column, column_span=1, center=False)`

Cards side by side. `grid_scroll` returns `(area, grid)`: put `area` in the page and add to `grid`.

```python
area, grid = c.grid_scroll(14)
c.page(self.widget, filters=c.row((self.search, 1), self.search_button), body=area)

for index, chart in enumerate(charts):
    c.grid_cell(grid, self.card_of(chart), index // columns, index % columns)
for column in range(columns):
    grid.setColumnStretch(column, 1)
c.grid_cell(
    grid, load_more, rows, 0, columns, center=True
)  # across all the columns, centered
```

To draw again, take the cards out of the grid and delete them:

```python
while (item := grid.takeAt(0)) is not None:
    if widget := item.widget():
        widget.deleteLater()
```

## `error_banner(details_text="Details", hide_text="Hide", dismiss_text="Dismiss")`

A red banner for what went wrong. It starts hidden.

```python
self.banner = c.error_banner(
    translate("Page", "Details"),
    translate("Page", "Hide"),
    translate("Page", "Dismiss"),
)
c.page(self.widget, notice=self.banner.frame, body=self.table)

self.banner.show_error(
    first_line(message), message.strip()
)  # a line; the whole error one click away
self.banner.dismiss()  # hide it
```

| Member | |
| ------ | - |
| `frame` | the widget to put in the page |
| `show_error(text, details, words=("Details", "Hide"))` | show it; `details` is the longer text behind the Details button (the button is hidden when it equals `text`) |
| `dismiss()`, `toggle_details()` | hide it; open or close the details |
| `label`, `details_label`, `details_button`, `dismiss_button` | the parts, for a test |

## Showing and hiding

Use `widget.setVisible(...)` and `widget.hide()` on what you built. A page that is not the current one is
hidden by the app; do not rely on `isVisible()` of a child of a page that was not shown.
