# 9. Recipes

[Wiki](README.md) · previous: [Testing](8-testing.md) · next: [Reference](10-reference.md)

## A list page

A page with filters, a summary line, buttons, a table that sorts, badges, a right click, a refresh timer and a
count. This is the shape of the pages of the AWS, Plugins and Custom Resources extensions.

```python
from functools import partial

from kubescope.sdk import CONTEXT_CHANGED, translate
from kubescope.sdk.models import natural_key


class WidgetsPage:
    def __init__(self, ctx):
        self.ctx = ctx
        self.rows = []
        self.sort = None  # (column, descending)
        c = self.c = ctx.ui.components
        self.widget = c.widget(shown=self.shown, hidden=self.hidden)

        # the filters
        self.origin = c.filter_select(
            [(translate("WidgetsPage", "All"), ""), ("Helm", "helm")]
        )
        self.search = c.search_box(translate("WidgetsPage", "Search all columns..."))
        self.case = c.switch_button("Aa", translate("WidgetsPage", "Match case"))
        for control in (
            self.origin.currentIndexChanged,
            self.search.textChanged,
            self.case.toggled,
        ):
            control.connect(self.filter)

        # the actions
        self.summary = c.label(variant="summary")
        self.details = c.button(
            translate("WidgetsPage", "Details"),
            icon=c.icon("info", ctx.ui.themed("#3220a0")),
            on_click=self.show_details,
        )

        # the table
        self.table = c.data_table(
            [
                translate("WidgetsPage", "NAME"),
                translate("WidgetsPage", "STATUS"),
                translate("WidgetsPage", "AGE"),
            ],
            [300, 120],
        )
        self.sorter = c.header_sorter(self.table, self.ordered)
        c.on_context_menu(self.table, self.menu)
        self.table.itemSelectionChanged.connect(self.sync_buttons)

        # what says what is going on
        self.notice = c.label(variant="muted", wrap=True)
        self.banner = c.error_banner(
            translate("WidgetsPage", "Details"),
            translate("WidgetsPage", "Hide"),
            translate("WidgetsPage", "Dismiss"),
        )
        self.count = c.label(variant="muted")

        c.page(
            self.widget,
            filters=c.row(self.origin, self.search, self.case, None),
            actions=c.row(self.summary, None, self.details, spacing=6),
            notice=self.banner.frame,
            body=self.table,
            footer=c.row(
                self.count,
                None,
                c.label(
                    translate("WidgetsPage", "Data fetched from the cluster"), "muted"
                ),
            ),
        )

        self.timer = c.timer(30_000, self.load, self.widget)
        ctx.events.on(CONTEXT_CHANGED, lambda **_: self.load())

    # the page opened and hidden
    def shown(self):
        self.load()
        self.timer.start()

    def hidden(self):
        self.timer.stop()

    # reading, off the UI thread
    def load(self):
        context = self.ctx.current_context
        if not context:
            self.notice.setText(translate("WidgetsPage", "Select a context."))
            return
        self.ctx.ui.run_action(
            partial(read, self.ctx.cluster, context),
            self.arrived,
            on_error=self.failed,
            quiet=True,
        )

    def arrived(self, rows):
        self.rows = rows
        self.banner.dismiss()
        self.render()

    def failed(self, message):
        self.banner.show_error(
            message.splitlines()[0],
            message,
            (translate("WidgetsPage", "Details"), translate("WidgetsPage", "Hide")),
        )

    # drawing
    def render(self):
        rows = self.rows
        if self.sort:
            column, descending = self.sort
            rows = sorted(
                rows, key=lambda row: natural_key(row.cells[column]), reverse=descending
            )
        self.table.setRowCount(len(rows))
        for y, row in enumerate(rows):
            for x, text in enumerate(row.cells):
                item = self.c.table_item(text, tip=text)
                if x == 1:
                    self.c.set_badge(item, text)  # the status as a badge
                self.table.setItem(y, x, item)
        self.filter()

    def filter(self, *_):
        text = self.search.text().strip().lower()
        shown = 0
        for y in range(self.table.rowCount()):
            cells = " ".join(
                self.table.item(y, x).text().lower()
                for x in range(self.table.columnCount())
            )
            visible = text in cells
            self.table.setRowHidden(y, not visible)
            shown += visible
        self.count.setText(
            translate("WidgetsPage", "{visible} of {total}").format(
                visible=shown, total=len(self.rows)
            )
        )

    def ordered(self, column, descending):
        self.sort = (column, descending)
        self.render()

    def sync_buttons(self):
        self.details.setEnabled(bool(self.table.selectionModel().selectedRows()))

    def show_details(self): ...

    def menu(self, x, y):
        row = self.table.rowAt(y)
        if row < 0:
            return
        self.table.selectRow(row)
        menu = self.c.menu(self.widget)
        menu.addAction(translate("WidgetsPage", "Details"), self.show_details)
        self.c.show_menu(menu, self.table, x, y)


def activate(ctx):
    if ctx.ui is None:  # the terminal has no pages
        return
    ctx.add_page(
        "Cloud",
        "Widgets",
        translate("Ext", "List"),
        lambda: WidgetsPage(ctx).widget,
        subtitle=translate("Ext", "The widgets of the cluster"),
    )
```

## A section of the Settings

A section the app puts in a card and loads and saves with the rest of the Settings.

```python
class MySettings:
    def __init__(self, ctx, settings, apply):
        c = ctx.ui.components
        self.settings, self._apply = settings, apply
        self.widget = c.widget(load=self.load, save=self.save)
        self.enabled = c.checkbox(translate("MySettings", "Show the assistant"))
        self.program = c.filter_select()
        self.path = c.text_field(
            translate("MySettings", "Found on the path of the system")
        )
        browse = c.button(translate("MySettings", "Browse..."), on_click=self.browse)
        self.interval = c.number_field(15, 3600, 30)
        layout = c.column(
            self.enabled,
            self.program,
            c.label(translate("MySettings", "Where the program is"), "muted"),
            c.row((self.path, 1), browse),
            c.row(c.label(translate("MySettings", "Look every")), self.interval, None),
            None,
            spacing=14,
        )
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)
        self.c = c

    def browse(self):
        path = self.c.open_file(self.widget, translate("MySettings", "Where is it?"))
        if path:
            self.path.setText(path)

    def load(self):
        self.enabled.setChecked(self.settings.enabled)
        self.path.setText(self.settings.path)

    def save(self) -> bool:
        self.settings.enabled = self.enabled.isChecked()
        self.settings.path = self.path.text().strip()
        self._apply()
        return True  # False keeps the Settings from saving


ctx.add_settings_section(
    "My extension", lambda: MySettings(ctx, settings, apply).widget
)
```

Under a check box, a note aligned with its text: `note = c.label(text, "muted", wrap=True)` and
`note.setContentsMargins(26, 0, 0, 0)`.

## A bell and a panel

```python
class Bell:
    def __init__(self, ctx):
        ui = ctx.ui
        c = ui.components
        self.bell = c.counter_button(
            c.icon("bell", "#ffffff"), translate("Bell", "Notifications"), "myBell"
        )
        self.panel = c.side_panel(
            ui.central,
            translate("Bell", "Notifications"),
            [],
            lambda: c.bottom_of(self.bell, ui.central) + 6,
            empty_text=translate("Bell", "Nothing to report."),
        )
        self.bell.clicked.connect(
            lambda: self.panel.close_panel() if self.panel.opened else self.open()
        )
        self.panel.on_closed = lambda: self.bell.setChecked(False)
        self.panel.is_inside = lambda point: self.bell.rect().contains(
            self.bell.mapFromGlobal(point)
        )
        ui.add_top_bar_button(ctx.id, self.bell)

    def open(self):
        cards = [c.notice_card(...) for item in items]
        self.panel.show_cards(cards)
        self.panel.open_panel()
        self.bell.setChecked(True)
```

## A dialog with a form

```python
class UpdateDialog:
    def __init__(self, parent, c, row):
        self.version = c.filter_select()
        self.version.setEditable(True)
        self.command = c.command_box(height=90)
        self.problem = c.label(variant="muted", wrap=True)
        update = c.button(translate("Update", "Update"), "primary")
        cancel = c.button(translate("Update", "Cancel"))
        cancel.setDefault(True)
        self.dialog = c.dialog(
            parent,
            translate("Update", "Update {name}").format(name=row.name),
            c.column(
                c.form([(translate("Update", "Version"), self.version)]),
                self.command,
                self.problem,
            ),
            [cancel, update],
            width=640,
        )
        update.clicked.connect(self.dialog.accept)
        cancel.clicked.connect(self.dialog.reject)

    def exec(self) -> bool:
        return bool(self.dialog.exec())
```

## From Qt code to components

| You were writing | Write instead |
| ---------------- | ------------- |
| `class MyPage(QWidget)` | `class MyPage:` with `self.widget = c.widget(shown=...)` |
| `QVBoxLayout(self)`, `setContentsMargins(32, 24, 32, 22)` | `c.page(self.widget, filters=..., body=...)` |
| `QHBoxLayout()` + `addWidget` + `addStretch` | `c.row(a, b, None, d)` |
| `QTableWidget` + styling + header setup | `c.data_table(headers, widths)` |
| `QTableWidgetItem(text)` + `setForeground` | `c.table_item(text, tip)` |
| `item.setData(BADGE_ROLE, ...)` | `c.set_badge(item, status)` |
| `QPushButton` + `setProperty("variant", ...)` | `c.button(text, variant)` |
| `QLineEdit` / `QComboBox` / `QSpinBox` with the variant | `c.text_field()` / `c.filter_select()` / `c.number_field()` |
| `QLabel` with `setProperty("variant", "muted")` | `c.label(text, "muted")` |
| `QMessageBox.question(...)` | `c.ask(...)` or `c.confirm(...)` |
| `QDialog` + layout + buttons | `c.dialog(parent, title, body, buttons)` |
| `QTimer(self)` / `QTimer.singleShot` | `c.timer(...)` / `c.after(...)` |
| `QThread` + `Signal` | `c.background(function, on_done=..., stream=...)` |
| `QCoreApplication.translate` / `self.tr` | `translate("Context", "Text")` |
| `QDesktopServices.openUrl(QUrl(url))` | `c.open_url(url)` |
| `QApplication.clipboard().setText(...)` | `c.copy_text(...)` |
| `QFileDialog.getOpenFileName` | `c.open_file(parent, title, start)` |
| `Qt.SortOrder.DescendingOrder` | the `descending` boolean the sorter gives you |
| `item.setCheckState(Qt.CheckState.Checked)` | `c.set_item_checked(item, True)` |
| `QIcon` drawn with `QPainter` | `c.icon(name, color)` |
| `shiboken6.isValid(widget)` | `c.is_alive(widget)` |
| a worker that reads a cluster | `ctx.ui.run_action(function, on_success, ..., on_error=...)` |

If what you need is not in the table, it is a component the SDK does not have yet: ask for it (or add it, with
its test) in the SDK and in `kubescope/extensions/components.py` of the app, rather than importing Qt.
