# The Components wiki

Everything an extension draws or needs of Qt comes from the SDK. This wiki says how to use every
component of `ctx.ui.components` and the helper `translate`, with an example for each.

> **The rule.** An extension imports nothing from `PySide6` or `shiboken6`, in its code or in its
> tests. A widget, a table, a badge, a dialog, a timer, an icon, a translated text, a worker thread:
> all of them are asked of `ctx.ui.components` or `kubescope.sdk`. When something is missing it is added
> to the SDK and to the app, never imported from Qt. Every extension has a test that fails on such an
> import, and a change to the look of the app reaches every extension at once.

Needs SDK 1.13 and an app that has it (KubeScope 2.10). Ask for `kubescope-sdk>=1.13.0,<2.0.0` in your
`pyproject.toml`, and `min_app = "2.10.0"` in your manifest (and, if you want to keep it off apps you have not tried, `max_app = "3.0.0"`).

## The pages

| Page | What is in it |
| ---- | ------------- |
| [1. Pages and layouts](1-pages-and-layouts.md) | `widget`, `page`, `row`, `column`, `form`, `card`, `scroll`, `spacer`, `grid_scroll`, `grid_cell`, `error_banner` |
| [2. Tables](2-tables.md) | `data_table`, `header_sorter`, `table_item`, badges, check boxes in cells, the right click |
| [3. Buttons, fields and texts](3-buttons-fields-and-texts.md) | `button`, `icon_button`, `switch_button`, `search_box`, `filter_select`, `text_field`, `number_field`, `time_field`, `text_area`, `checkbox`, `label`, `muted_label`, `command_box`, `check_matrix` |
| [4. Dialogs and menus](4-dialogs-and-menus.md) | `dialog`, `confirm`, `ask`, `guide`, `open_file`, `menu`, `show_menu` |
| [5. Notices, panels and search](5-notices-panels-and-search.md) | `side_panel`, `notice_card`, `counter_button`, `palette` |
| [6. Services](6-services.md) | `translate`, `timer`, `after`, `background`, `icon`, `image`, `open_url`, `copy_text`, `on_resize`, `bottom_of`, `is_alive`, `let_window_shrink` |
| [7. A chat with an assistant](7-chat.md) | `chat_view`, `chat_dock` |
| [8. Testing](8-testing.md) | the test kit, a fake `ui`, what to assert |
| [9. Recipes](9-recipes.md) | a whole page, a section of the Settings, a panel, from Qt code to components |
| [10. Reference](10-reference.md) | every component, alphabetically, with its signature |

## In ten lines

```python
from kubescope.sdk import CONTEXT_CHANGED, translate


class WidgetsPage:
    def __init__(self, ctx):
        self.ctx = ctx
        c = ctx.ui.components
        self.widget = c.widget(shown=self.load)  # what the app puts in the window
        self.search = c.search_box(translate("WidgetsPage", "Search..."))
        self.table = c.data_table(
            [translate("WidgetsPage", "NAME"), translate("WidgetsPage", "STATUS")],
            [300],
        )
        c.page(self.widget, filters=c.row(self.search, None), body=self.table)
        ctx.events.on(CONTEXT_CHANGED, lambda **_: self.load())

    def load(self): ...


ctx.add_page("Cloud", "Widgets", "List", lambda: WidgetsPage(ctx).widget)
```

A page is a plain object that holds its widget. The app asks the factory for the widget, calls `shown()` on it
when the page is opened, and the rest is yours.

## Where things are

- The protocol, with the docstring of each call: [`context.py`](../../src/kubescope/sdk/context.py), class
  `Components`.
- The implementation: `kubescope/extensions/components.py` of the app.
- Extensions that use all of this: [kubescope-aws](https://github.com/dcotecnologia/kubescope-aws),
  [kubescope-ext-plugins](https://github.com/dcotecnologia/kubescope-ext-plugins),
  [kubescope-ext-custom-resources](https://github.com/dcotecnologia/kubescope-ext-custom-resources),
  [kubescope-notifications](https://github.com/dcotecnologia/kubescope-notifications),
  [kubescope-search](https://github.com/dcotecnologia/kubescope-search) and
  [kubescope-ai-gabi](https://github.com/dcotecnologia/kubescope-ai-gabi).
