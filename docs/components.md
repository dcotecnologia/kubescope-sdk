# Components

`ctx.ui.components` hands an extension the pre-formatted elements of the app, so a page looks like the
others without keeping a copy of their code. It is part of `ctx.ui` and needs the `ui.window` permission.

Everything it returns is a plain Qt (`PySide6`) widget or object; the SDK types them as `Any` because it
does not import Qt. Because the app draws them, a change to the look of the app reaches every extension
at once.

| Component | Builds |
| --------- | ------ |
| [`data_table`](#data_table) | The table of the lists of the app |
| [`header_sorter`](#header_sorter) | Sorting by a click on a header |
| [`set_badge`](#badges) · [`set_badge_colors`](#badges) · [`badge_delegate`](#badges) | The status pills |
| [`button`](#buttons) · [`switch_button`](#buttons) | Buttons and the switches of a search box |
| [`search_box`](#fields) · [`filter_select`](#fields) · [`text_field`](#fields) · [`number_field`](#fields) · [`muted_label`](#fields) | The search box, selects, fields and notes |

Needs SDK 1.11 and an app that has it (KubeScope 2.9): ask for `kubescope-sdk>=1.11.0,<2.0.0` in your
`pyproject.toml`.

## `data_table`

```python
table = ctx.ui.components.data_table(
    ["NAME", "STATUS", "VERSION", "AGE"],  # one column for each header
    [260, 120, 120],  # widths in pixels; the last column takes the rest
)
```

The table has what the lists of the app have:

- rows of the same height, a divider between them, no grid;
- one row selected at a time, and cells that cannot be edited;
- headers centered and clickable, the texts of the cells at the left;
- a text too long for its cell cut with an ellipsis, never wrapped;
- the badge delegate on every column (see [Badges](#badges)).

Fill it as any `QTableWidget`:

```python
table.setRowCount(len(rows))
for y, row in enumerate(rows):
    for x, text in enumerate(row.cells):
        table.setItem(y, x, QTableWidgetItem(text))
```

The headers are what you pass: upper-case them (and translate them) yourself.

### With a check box in the header

```python
table = ctx.ui.components.data_table(headers, widths, checkable=True)
header = table.horizontalHeader()  # a CheckHeader
header.set_column(0)  # the column whose section has the box; -1 for none
header.set_check_state(Qt.CheckState.Checked)
header.toggled.connect(
    lambda checked: ...
)  # the person checked (True) or cleared (False) all
```

Draw the boxes of the rows yourself, as checkable items of that column.

## `header_sorter`

A click on a header sorts by it, ascending first, and a second click reverses it. Ages, numbers and
versions sort by what they mean (`natural_key`), not by their letters.

```python
# 1. The sorter moves the rows of the table itself:
sorter = ctx.ui.components.header_sorter(table)
...
fill(table)
sorter.reapply()  # after filling it again, so the order the person chose stays


# 2. The page keeps a list and draws it again: it is told the column and the order
def sort(column: int, order: Qt.SortOrder) -> None:
    rows.sort(
        key=lambda row: natural_key(row.cells[column]),
        reverse=order == Qt.SortOrder.DescendingOrder,
    )
    render()


sorter = ctx.ui.components.header_sorter(table, sort)
```

`sorter.state` is `(column, order)` of the header last clicked, or `None`.

## Badges

A badge is a rounded pill, as wide as its column, in the colors of a status.

```python
item = QTableWidgetItem("Active")
ctx.ui.components.set_badge(item, "Active")
table.setItem(y, 1, item)
```

`set_badge(item, status)` picks the colors from the status, whatever its case:

| Status | Look |
| ------ | ---- |
| `Normal`, `Active`, `Deployed`, `Available`, `Running`, `Enabled` | green |
| `Warning`, `Creating`, `Updating`, `Deleting`, `Upgrading`, `Starting`, `Stopping`, `Pending…`, `Outdated` | amber |
| anything with `Fail`, `Error`, `Degraded` | red |
| anything else | grey |

For a state those words do not name, give the colors yourself, as `ctx.ui.themed` shows them:

```python
ctx.ui.components.set_badge_colors(
    item, ctx.ui.themed("#176b58"), ctx.ui.themed("#e5f4eb")
)
```

`data_table` has the delegate on every column. A table you build yourself gets it with
`table.setItemDelegateForColumn(column, ctx.ui.components.badge_delegate(table))`.

## Buttons

```python
install = components.button("Install", "primary", on_click=self.install)
more = components.button("Load more")  # secondary, the default
details = components.button("Details", icon=info_icon, on_click=self.details)
learn = components.button("Learn more", "link")
case = components.switch_button("Aa", "Match case")  # stays pressed
regex = components.switch_button(".*", "Regular expression")
```

`variant` is `primary` for the main action of a page or dialog, `secondary` for any other and `link` for
a text the person clicks. Do not set the `variant` property by hand: ask for the variant.

## Fields

```python
search = components.search_box("Search all columns...")  # with its clear button
origin = components.filter_select([("All origins", ""), ("Helm", "helm")])
name = components.text_field("Name")
port = components.number_field(1, 65535, 5432)  # a whole number
note = components.muted_label("Data fetched from the cluster API")
```

Their size and look are the ones of the lists and forms of the app. `filter_select` takes the items as
`(text, data)`; read the choice with `currentData()`.

## Testing a page that uses them

The components are the app's, so a test of your extension that does not run the app needs a fake. Give
your fake `ui` a `components` that builds plain Qt:

```python
class FakeComponents:
    def data_table(self, headers, widths, checkable=False):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(list(headers))
        return table

    def header_sorter(self, table, apply=None):
        return SimpleNamespace(state=None, reapply=lambda: None)

    def badge_delegate(self, parent):
        return QStyledItemDelegate(parent)

    def set_badge(self, item, status):
        item.setData(Qt.ItemDataRole.UserRole + 5, (status, ""))

    def set_badge_colors(self, item, text, fill):
        item.setData(Qt.ItemDataRole.UserRole + 5, (text, fill))

    def button(self, text, variant="secondary", icon=None, on_click=None):
        button = QPushButton(text)
        button.setProperty("variant", variant)
        if on_click:
            button.clicked.connect(lambda _=False: on_click())
        return button

    # ...and the same for switch_button, search_box, filter_select, text_field, muted_label
```

Or, if the tests of your extension already run the app (a development dependency), build the fake from
the real one: `UiComponents` of `kubescope.extensions.components`.

To test against the look itself, run the extension inside the app, where `ctx.ui.components` is the real
one.
