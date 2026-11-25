# 4. Dialogs and menus

[Wiki](README.md) · previous: [Buttons, fields and texts](3-buttons-fields-and-texts.md) · next: [Notices, panels and search](5-notices-panels-and-search.md)

Every dialog gets the frame and the buttons of the window of the app. For a message with no choice
(an information, a warning), use `ctx.ui.show_message(icon, title, text)`; for a choice, use the calls below.

## `dialog(parent, title, body, buttons, width=0)`

A dialog (`QDialog`) with `body` (a layout or a widget) above a row of `buttons` at the right, in the order
given. Call `exec()` on it; connect the buttons to `accept` and `reject`.

```python
copy = c.button("Copy", "primary", on_click=lambda: c.copy_text(command))
close = c.button("Close")
dialog = c.dialog(
    self.widget,
    translate("Install", "Install {name}").format(name=chart.name),
    c.column(note, box),
    [copy, close],
    width=620,
)
close.clicked.connect(dialog.accept)
if dialog.exec():  # True when it was accepted
    ...
```

A form in a dialog:

```python
update = c.button("Update", "primary")
cancel = c.button("Cancel")
cancel.setDefault(True)
dialog = c.dialog(
    self.widget,
    "Update web",
    c.column(c.form(rows), self.command, self.problem),
    [cancel, update],
    width=640,
)
update.clicked.connect(dialog.accept)
cancel.clicked.connect(dialog.reject)
```

Keep the object that holds the fields (`self.chart`, `self.command`) next to the dialog: read them after `exec()`.
To enable or disable the accepting button as the form changes, `update.setEnabled(...)`.

## `confirm(parent, title, text, ok="OK", detail="", warning=False)`

Asks to confirm something; `True` when the person chose `ok`. Cancel is the default, so an Enter does not go
through with it. `detail` is a longer text under `text` (the commands about to run, say); `warning=True` shows
the warning icon.

```python
if not c.confirm(
    self.widget,
    translate("Page", "Uninstall"),
    translate("Page", "Uninstall {count} from the cluster? This will run:").format(
        count=2
    ),
    translate("Page", "Uninstall"),
    detail="helm uninstall a\nhelm uninstall b",
    warning=True,
):
    return
```

## `ask(parent, title, text)`

A Yes or No question, with the words of the system; `True` for Yes, and No is the default.

```python
if c.ask(self.widget, "Assistant", translate("Page", "Forget every conversation?")):
    ...
```

## `guide(parent, title, text, detail, buttons, close_text)`

A message with a longer `detail` and a button for each `(text, callback)` of `buttons`: it runs its callback
and closes the message. The first is the main one. A last button, `close_text`, only closes it.

```python
c.guide(
    self.widget,
    "Gabi",
    translate("Gabi", "Gabi needs Claude Code or Codex."),
    steps,
    [
        (translate("Gabi", "Open Settings"), self.open_settings),
        (translate("Gabi", "Claude guide"), lambda: c.open_url(url)),
    ],
    translate("Gabi", "Close"),
)
```

## `open_file(parent, title, start="")`

Asks the person to choose a file to open: its path as a text, or an empty text when they gave up.

```python
path = c.open_file(
    self.widget, translate("Settings", "Where is claude?"), str(Path.home())
)
if path:
    field.setText(path)
```

## Menus: `menu(parent=None)`, `show_menu(menu, table, x, y)`

```python
menu = c.menu(self.widget)
menu.addAction(translate("Page", "Details"), partial(self.details, row))
menu.addAction(translate("Page", "Logs"), partial(self.logs, row))
c.show_menu(menu, self.table, x, y)  # at the place of the right click in a table
```

See [Tables](2-tables.md#the-right-click-on_context_menutable-handler-and-show_menumenu-table-x-y).

## A banner instead of a dialog

For something that went wrong while loading, a [banner](1-pages-and-layouts.md#error_bannerdetails_textdetails-hide_texthide-dismiss_textdismiss)
in the page is quieter than a dialog and does not stop the person.

## What a dialog is not

A dialog does not block the other windows of an extension in a test: see [8. Testing](8-testing.md) for
`answer_dialogs` and `refuse_modals`.
