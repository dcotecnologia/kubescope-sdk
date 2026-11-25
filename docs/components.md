# Components

> **The rule:** an extension imports nothing from `PySide6` or `shiboken6`, in its code or in its tests.
> Everything it draws or needs of Qt comes from `ctx.ui.components` and from `kubescope.sdk` (`translate`).
> If something is missing, it is added to the SDK and to the app, never imported from Qt. Each extension has a
> test that fails on such an import.

The complete guide, with an example for every component, is the **[Components wiki](wiki/README.md)**:

| | |
| - | - |
| [1. Pages and layouts](wiki/1-pages-and-layouts.md) | `widget`, `page`, `row`, `column`, `form`, `card`, `scroll`, `grid_scroll`, `error_banner` |
| [2. Tables](wiki/2-tables.md) | `data_table`, `header_sorter`, `table_item`, badges, check boxes, the right click |
| [3. Buttons, fields and texts](wiki/3-buttons-fields-and-texts.md) | `button`, `search_box`, `filter_select`, `text_field`, `number_field`, `label`... |
| [4. Dialogs and menus](wiki/4-dialogs-and-menus.md) | `dialog`, `confirm`, `ask`, `guide`, `open_file`, `menu` |
| [5. Notices, panels and search](wiki/5-notices-panels-and-search.md) | `side_panel`, `notice_card`, `counter_button`, `palette` |
| [6. Services](wiki/6-services.md) | `translate`, `timer`, `after`, `background`, `icon`, `image`, `open_url`, `copy_text` |
| [7. A chat with an assistant](wiki/7-chat.md) | `chat_view`, `chat_dock` |
| [8. Testing](wiki/8-testing.md) | the test kit and a fake `ui` |
| [9. Recipes](wiki/9-recipes.md) | a whole page, a Settings section, a panel, from Qt code to components |
| [10. Reference](wiki/10-reference.md) | every component, with its signature |
