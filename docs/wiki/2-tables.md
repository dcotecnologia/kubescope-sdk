# 2. Tables

[Wiki](README.md) · previous: [Pages and layouts](1-pages-and-layouts.md) · next: [Buttons, fields and texts](3-buttons-fields-and-texts.md)

The table of the lists of the app: `data_table`, with its header sorting, its badges, its check boxes and its
right click.

## `data_table(headers, widths, checkable=False)`

```python
table = c.data_table(
    [
        translate("Page", "NAME"),
        translate("Page", "STATUS"),
        translate("Page", "AGE"),
    ],  # one column each
    [300, 120],  # the width in pixels of the first columns; the last takes the rest
)
```

What it gives you:

- rows of the same height with a divider between them, no grid;
- one row selected at a time (`SelectRows`, `SingleSelection`), cells that cannot be edited;
- headers centered and clickable; the texts of the cells at the left;
- a text too long for its cell cut with an ellipsis, never wrapped, with its whole text as the tip when you use
  `table_item`;
- every column draws badges (see below);
- it is a `QTableWidget`: `setRowCount`, `setItem`, `item(row, column)`, `selectRow`, `selectionModel()`,
  `isRowHidden`, `setRowHidden` and the signals (`itemSelectionChanged`, `cellDoubleClicked`, `itemChanged`)
  work as usual.

The headers are what you pass: translate them and write them in capitals yourself.

### Filling it

```python
table.setRowCount(len(rows))
for y, row in enumerate(rows):
    for x, text in enumerate(row.cells):
        table.setItem(y, x, c.table_item(text, tip=text))
```

### Hiding rows (a search)

```python
for y, row in enumerate(rows):
    table.setRowHidden(y, not matches(row))
```

## `table_item(text, tip="", checked=None)`

A cell with the text color of the theme in use. `tip` is its tip (give the whole text when the cell cuts it).
With `checked` the cell has a check box, checked or not.

## Badges

A badge is a rounded pill, as wide as its column, in the colors of a status.

```python
item = c.table_item("Active")
c.set_badge(item, "Active")  # the colors come from the word
c.set_badge_colors(item, themed_text, themed_fill)  # or give them yourself
table.setItem(y, 1, item)
```

`set_badge(item, status)` knows these words, whatever their case:

| Words | Look |
| ----- | ---- |
| `Normal`, `Active`, `Deployed`, `Available`, `Running`, `Enabled` | green |
| `Warning`, `Creating`, `Updating`, `Deleting`, `Upgrading`, `Starting`, `Stopping`, `Modifying`, `Outdated`, anything starting with `Pending` | amber |
| anything with `Fail`, `Error`, `Degraded`, `Incompatible` | red |
| anything else (`Helm`, `EKS`, an empty word) | grey |

A text that does not fit the pill is cut with an ellipsis. Draw the badge of an origin or a kind with
`set_badge(item, "")`: it is grey.

`badge_delegate(parent)` is the delegate that draws them; `data_table` has it for every column already.
A table you build yourself gets it with `table.setItemDelegateForColumn(n, c.badge_delegate(table))`.

## Sorting by a click on a header: `header_sorter(table, apply=None)`

A click sorts by that column, ascending first; a second click reverses it. Ages, numbers and versions sort by
what they mean (`kubescope.sdk.models.natural_key`), not by their letters.

```python
# 1. The sorter moves the rows of the table itself (the rows carry all they need in their items):
self.sorter = c.header_sorter(table)
...
fill(table)
self.sorter.reapply()  # after filling it again, so the order the person chose stays


# 2. You keep a list and draw it again: you are told the column and the order
def ordered(column: int, descending: bool) -> None:
    self.sort = (column, descending)
    rows.sort(key=lambda row: natural_key(cells(row)[column]), reverse=descending)
    self.render()


self.sorter = c.header_sorter(table, ordered)
```

`sorter.state` is `(column, order)` of the header clicked last, or `None`; `sorter.clicked(column)` is what a
click does (call it in a test).

## Check boxes in the rows

For many rows acted on at once (the Plugins page does it for update and uninstall).

```python
table = c.data_table(headers, widths, checkable=True)
header = table.horizontalHeader()  # a CheckHeader
header.set_column(0)  # the column whose section has the box; -1 for none
header.toggled.connect(self.check_all)  # True: every row checked, False: none

item = c.table_item(name, checked=False)  # a box in the cell
c.set_item_checked(item, True)  # check it, or None to take the box away
c.item_checked(item)  # True, False, or None when it has no box
table.itemChanged.connect(self.item_changed)  # the person checked or unchecked one

header.set_checked(
    True
)  # what the box of the header shows: True, False, or None for some
header.checked  # read it back
```

While you fill the cells, ignore `itemChanged` (set a flag), or the filling looks like the person's click.

## The right click: `on_context_menu(table, handler)` and `show_menu(menu, table, x, y)`

```python
c.on_context_menu(table, self.menu)  # handler(x, y): the place in the rows


def menu(self, x: int, y: int) -> None:
    row = self.table.rowAt(y)
    if row < 0:
        return
    self.table.selectRow(row)
    menu = c.menu(self.widget)
    menu.addAction(translate("Page", "Details"), self.show_details)
    c.show_menu(menu, self.table, x, y)  # opens it where the person clicked
```

`menu(parent)` is a `QMenu`: `addAction(text, callback)`, `addSeparator()`, `actions()`, `isEmpty()`.

## An empty table

Say why a table has no row yourself: a muted label in the `notice` of the page ("Select a context.",
"Loading...") or an [error banner](1-pages-and-layouts.md#error_bannerdetails_textdetails-hide_texthide-dismiss_textdismiss)
when the read failed, and a count in the `footer`.

## A whole list page

[9. Recipes](9-recipes.md#a-list-page) puts the filters, the table, the sorting, the badges, the menu and the
timer together.
