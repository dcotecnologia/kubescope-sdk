# 3. Buttons, fields and texts

[Wiki](README.md) · previous: [Tables](2-tables.md) · next: [Dialogs and menus](4-dialogs-and-menus.md)

## Buttons

### `button(text, variant="secondary", icon=None, on_click=None)`

| `variant` | For |
| --------- | --- |
| `primary` | the main action of a page or a dialog (filled) |
| `secondary` | any other action (outlined); the default |
| `link` | a text the person clicks (a pointing hand over it) |

```python
install = c.button(
    translate("Page", "Install"), "primary", on_click=lambda: self.install(chart)
)
details = c.button(
    translate("Page", "Details"), icon=c.icon("info", color), on_click=self.details
)
learn = c.button(translate("Page", "Learn more"), "link", on_click=self.learn)
```

Do not set the `variant` property by hand: ask for the variant. `on_click` is called without arguments.
The button is a `QPushButton`: `setEnabled`, `setVisible`, `setText`, `setIcon`, `setDefault`, `setToolTip`,
`click()` and `clicked` work as usual. When the theme changes, colored icons are made again by you (see
`icon` in [Services](6-services.md#iconname-color-options)).

### `icon_button(icon, tip, on_click=None, variant="link")`

A button that is only an icon, with its words as the tip.

```python
trash = c.icon_button(
    c.icon("trash", color), translate("Page", "Uninstall"), self.remove
)
```

### `switch_button(text, tip)`

A square button that stays pressed: the `Aa` (match case) and `.*` (regular expression) of a search box.

```python
self.case = c.switch_button("Aa", translate("Page", "Match case"))
self.regex = c.switch_button(".*", translate("Page", "Regular expression"))
self.case.toggled.connect(self.filter)
```

## Fields

| Component | Gives | Read it with |
| --------- | ----- | ------------ |
| `search_box(placeholder="")` | the search box of the lists, with its clear button | `text()`, `textChanged`, `returnPressed` |
| `filter_select(items=())` | a select as the filters of the lists; `items` are `(text, data)` | `currentData()`, `currentIndexChanged` |
| `text_field(placeholder="")` | a line of text for a form | `text()`, `setText()`, `textChanged` |
| `number_field(minimum, maximum, value=0)` | a whole number | `value()`, `setValue()`, `valueChanged`, `setSuffix()` |
| `time_field()` | a time of the day as `HH:mm` | `time_text(field)`, `set_time(field, "08:30")` |
| `text_area(placeholder="", max_height=0)` | several lines to type in | `toPlainText()`, `setPlainText()` |
| `checkbox(text, checked=False, on_toggle=None)` | a check box | `isChecked()`, `toggled` |

```python
origin = c.filter_select(
    [("All origins", ""), ("Helm", "helm"), ("Cluster", "cluster")]
)
origin.currentData()  # "", "helm" or "cluster"

region = c.filter_select()
region.addItem("us-east-1", "us-east-1")  # or add items later
region.setEditable(True)  # to type a value that is not a choice

interval = c.number_field(15, 3600, 30)
interval.setSuffix(translate("Settings", " seconds"))

start = c.time_field()
c.set_time(start, "22:00")
c.time_text(start)  # "22:00"

ignored = c.text_area("Pod/batch-*\nprod/Deployment/api", 110)
keep = c.checkbox(translate("Dialog", "Keep the values"), True, on_toggle=self.preview)
```

## Texts

### `label(text="", variant="", wrap=False, align="")`

| `variant` | Look |
| --------- | ---- |
| `""` | the normal text |
| `muted` | a soft note |
| `summary` | the line that says what is listed ("12 add-ons") |
| `filter` | the small title of a filter ("NAMESPACE") |
| `title` | a larger bold title (a card's) |
| `mark` | a bold mark (a star, a tick) |
| `cardTitle` (or any other name the app styles) | passed through as the `variant` property |

`wrap=True` breaks it into lines. `align` is `left`, `right`, `center` or `top-left`.

```python
self.summary = c.label(variant="summary")
self.notice = c.label(variant="muted", wrap=True)
repository = c.label(chart.repository, align="right")
```

### `muted_label(text="")`

The same as `label(text, "muted")`.

### `command_box(text="", height=96)`

A read-only box in the fixed font, for a command or a text to read and copy.

```python
self.command = c.command_box(height=90)
self.command.setPlainText(" ".join(arguments))
copy = c.button(
    "Copy", "primary", on_click=lambda: c.copy_text(self.command.toPlainText())
)
```

### `check_matrix(headers, rows)`

A table of check boxes for a Settings section: a column for each of `headers`, a line for each `(key, text)`
of `rows`. It returns `(frame, boxes)`: put `frame` in the page; `boxes` has, for each header, a dict of its
check boxes by key.

```python
frame, (shown, told) = c.check_matrix(
    [translate("Panel", "Show"), translate("Panel", "Tell the system")],
    [("error", "Errors"), ("warning", "Warnings")],
)
shown["error"].setChecked(True)
told["warning"].isChecked()
```

## Images

`image_label(size)` is a square for an image; see [Services](6-services.md#imagedata-size-and-set_imagelabel-image).
