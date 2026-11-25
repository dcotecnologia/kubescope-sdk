# 5. Notices, panels and search

[Wiki](README.md) · previous: [Dialogs and menus](4-dialogs-and-menus.md) · next: [Services](6-services.md)

The notifications extension is built with all of these: a bell in the top bar that counts what was not read,
and a panel that slides in from the right with a card for each notice.

## `counter_button(icon, tip, name="counterButton")`

A flat 32 px button for the top bar, with a red badge for a count. It can be checked while its panel is open.

```python
self.bell = c.counter_button(
    c.icon("bell", "#ffffff"),
    translate("Notifications", "Notifications"),
    "notificationsBell",
)
self.bell.clicked.connect(self.toggle)
ui.add_top_bar_button(ctx.id, self.bell)  # the app puts it beside the Settings button

self.bell.set_unread(5)  # the badge: 99+ above 99, nothing at 0
self.bell.setChecked(True)  # pressed while the panel is open
self.bell.restyle(ui.themed)  # when the theme changes
```

| Member | |
| ------ | - |
| `set_unread(count)` | the number in the badge |
| `badge_text()`, `unread` | what it shows, and the count |
| `restyle(themed)` | take the colors of the theme in use |

## `side_panel(host, title, actions, top, close_text="✕", empty_text="")`

A panel that slides in from the right edge of `host` (give it `ui.central`), under the top bar. It has a title,
the `actions` buttons and a close button in its header, a scrolling list of cards, and a strip at its left
edge that is dragged to make it wider.

| Argument | |
| -------- | - |
| `host` | where it sits: `ui.central` |
| `title` | the title in its header |
| `actions` | buttons for the header, made with `button` |
| `top` | a function that says where it starts, as a y in `host`: `lambda: c.bottom_of(self.bell, host) + 6` |
| `close_text` | the text of the close button |
| `empty_text` | what it says when it has no card |

```python
mark_all = c.button(translate("Panel", "Mark all as read"), on_click=self.mark_read)
clear = c.button(translate("Panel", "Clear"), on_click=self.clear)
self.panel = c.side_panel(
    ui.central,
    translate("Panel", "Notifications"),
    [mark_all, clear],
    self.top,
    empty_text=translate("Panel", "Nothing to report."),
)

self.panel.on_closed = lambda: self.bell.setChecked(False)
self.panel.on_resized = lambda width: setattr(self.settings, "panel_width", width)
self.panel.is_inside = lambda point: self.bell.rect().contains(
    self.bell.mapFromGlobal(point)
)
self.panel.set_panel_width(self.settings.panel_width)
```

| Member | |
| ------ | - |
| `open_panel()`, `close_panel()`, `opened` | slide it in or out; whether it is open |
| `show_cards(cards)` | draw these cards, keeping where the person had scrolled to |
| `set_panel_width(width)` | its width, within what keeps it usable and what the window allows |
| `on_closed()` | called when it closes (the close button, Esc, a click outside) |
| `on_resized(width)` | called when the person lets go of the strip, with the width to keep |
| `is_inside(point)` | say that a click at that screen point is of its own button (the bell), which opens and closes it itself |
| `restyle()` | take the colors of the theme in use |
| `list`, `scroller`, `close_button` | the parts, for a test |

A click anywhere else of the window closes it, and so does Esc (only while it is open).

## `notice_card(title, kind, about, message, when, level, unread, tip, on_click, actions=())`

A card for the list of the panel:

```text
┌────────────────────────────────────┐
│ title                      kind    │
│ about                              │
│ message                            │
│ when                               │
│ action 1   action 2                │
└────────────────────────────────────┘
```

| Argument | |
| -------- | - |
| `title`, `kind` | the first line: a title at the left, a word at the right (`Error`) |
| `about` | where it is about (`prod · Pod/api · ns`); leave it empty to omit the line |
| `message`, `when` | the text and how long ago (`4× · 3m ago`) |
| `level` | `error`, `warning`, `info` or `normal`: the color of its left edge |
| `unread` | an unread one is tinted; a read one is crossed out |
| `tip` | its tip |
| `on_click` | called when it is clicked with the left button |
| `actions` | links under it: `(text, callback)` pairs |

```python
card = c.notice_card(
    item.reason,
    "Error",
    "prod · Pod/api",
    item.message,
    "3m ago",
    item.level,
    unread=True,
    tip=translate("Panel", "Mark as read"),
    on_click=lambda: self.read(item),
    actions=[(translate("Panel", "Go to context"), lambda: self.open(item))],
)
card.buttons  # the links, in order, for a test
self.panel.show_cards([card])
```

You may hang your own data on the card (`card.item = item`) for a test to find it.

## `palette(parent, title, placeholder, loading)`

The window that finds a screen, an action or a resource as one types, like a command palette: it opens
under the top of the window, filters as the person types, moves with the arrows, goes with Enter, and closes
when the window loses focus.

```python
dialog = c.palette(
    ui.window,
    translate("Search", "Search"),
    translate("Search", "Search screens, actions and resources..."),
    translate("Search", "Loading resources..."),
)

dialog.open_with(entries)  # entries have label, detail and run()
ui.run_action(
    ctx.cluster.search_resources,
    lambda hits: dialog.set_resources(hits, self.show),
    context,
    on_error=dialog.resources_failed,
    quiet=True,
)
```

| Member | |
| ------ | - |
| `open_with(entries)` | show it with these screens and actions; the note says it is loading |
| `set_resources(hits, run)` | add what was found in the cluster (`SearchHit`s); `run(hit)` goes to one |
| `resources_failed(text)` | say why none were found (or `""` to clear the note) |

An entry is any object with `label`, `detail` and a `run()`: `SearchEntry` of the search extension is a small
dataclass. At most 50 results are listed, best match first.
