# 10. Reference

[Wiki](README.md) · previous: [Recipes](9-recipes.md)

Every component of `ctx.ui.components`, alphabetically, with its signature and the page that explains it. The
source of truth is the protocol `Components` in [`context.py`](../../src/kubescope/sdk/context.py), which
has the docstring of each.

| Component | Signature | What it is | Page |
| --------- | --------- | ---------- | ---- |
| `after` | `(delay_ms: int, owner: Any, callback: Callable[[], None])` | Call `callback` once, in `delay_ms`, unless `owner` is gone. | [6](6-services.md) |
| `ask` | `(parent: Any, title: str, text: str)` | A Yes or No question; True for Yes, and No is the default. | [4](4-dialogs-and-menus.md) |
| `background` | `(function: Callable[[], Any], on_piece: Callable[[Any], None] \| None=None, on_done: Callable[[Any], None] \| None=None, on_error: Callable[[str], None] \| None=None, on_finished: Callable[[], None] \| None=None, stream: bool=False)` | Run `function` off the UI thread and hear from it on it: `on_done(answer)`, `on_error(message)` and `on_finished()`. With `stream`, `function` is a generator and `on_piece(piece)` hears each piece as it is made. The handle has `stopped` (set it to cut a stream short; the generator is closed) and `wait(ms)`. | [6](6-services.md) |
| `badge_delegate` | `(parent: Any)` | The delegate that draws the cells marked by `set_badge` as the badges of the app, a rounded pill as wide as its column; `parent` is the table. | [2](2-tables.md) |
| `bottom_of` | `(widget: Any, host: Any)` | Where the bottom edge of `widget` is, as a y in the coordinates of `host`. | [6](6-services.md) |
| `button` | `(text: str, variant: str='secondary', icon: Any=None, on_click: Callable[[], None] \| None=None)` | A button (`QPushButton`) as the app has them. | [3](3-buttons-fields-and-texts.md) |
| `card` | `(*items: Any, name: str='', min_height: int=0)` | A rounded box (`QFrame`) with `items` one under the other; see `column` for what an item can be. | [1](1-pages-and-layouts.md) |
| `chat_dock` | `(host: Any, name: str, texts: dict[str, str])` | The round button in the corner of `host` and the chat panel it opens, which can be resized, taken out into a window or made to fill the page; `texts` are the words of the panel, by their English text. | [7](7-chat.md) |
| `chat_view` | `(texts: dict[str, str])` | A conversation with an assistant laid out as a chat, with its composer: bubbles (`add_bubble`), what is attached (`show_chips`), the status, the usage ring and the action cards. It tells what the person does through signals (`submitted`, `stop_requested`, `attach_requested`, `image_pasted`, `files_pasted`, `text_pasted`, `ring_clicked`). `texts` are its words in the language of the app. | [7](7-chat.md) |
| `check_matrix` | `(headers: Sequence[str], rows: Sequence[tuple[str, str]])` | A table of check boxes: a column for each of `headers` and a line for each `(key, text)` of `rows`. | [3](3-buttons-fields-and-texts.md) |
| `checkbox` | `(text: str, checked: bool=False, on_toggle: Callable[[bool], None] \| None=None)` | A check box (`QCheckBox`); `on_toggle` is told whether it is checked. | [3](3-buttons-fields-and-texts.md) |
| `column` | `(*items: Any, spacing: int=10)` | The same, one under the other (`QVBoxLayout`). | [1](1-pages-and-layouts.md) |
| `command_box` | `(text: str='', height: int=96)` | A box for a command or a text to read and copy (a read-only `QPlainTextEdit` in the fixed font). | [3](3-buttons-fields-and-texts.md) |
| `confirm` | `(parent: Any, title: str, text: str, ok: str='OK', detail: str='', warning: bool=False)` | Ask the person to confirm something; True when they chose `ok`. | [4](4-dialogs-and-menus.md) |
| `copy_text` | `(text: str)` | Put `text` on the clipboard. | [6](6-services.md) |
| `counter_button` | `(icon: Any, tip: str, name: str='counterButton')` | A flat 32 px button for the top bar, with a red badge for a count (`set_unread(count)`); it can be checked while its panel is open and takes the colors of the theme (`restyle(themed)`). | [5](5-notices-panels-and-search.md) |
| `data_table` | `(headers: Sequence[str], widths: Sequence[int], checkable: bool=False)` | A table as the lists of the app are: one column for each of `headers`, the first `len(widths)` with that width in pixels and the last stretched, rows of the same height with a divider, one row selected at a time, headers centered and clickable, cells that cannot be edited, a text too long cut with an ellipsis, and every cell able to be a badge (`set_badge`). | [2](2-tables.md) |
| `dialog` | `(parent: Any, title: str, body: Any, buttons: Sequence[Any], width: int=0)` | A dialog (`QDialog`) with `body` (a layout or a widget) above a row of `buttons` at the right; call `exec()` on it. | [4](4-dialogs-and-menus.md) |
| `error_banner` | `(details_text: str='Details', hide_text: str='Hide', dismiss_text: str='Dismiss')` | A red banner for what went wrong. | [1](1-pages-and-layouts.md) |
| `filter_select` | `(items: Sequence[tuple[str, Any]]=())` | A select (`QComboBox`) as the filters of the lists, with an item for each `(text, data)`. | [3](3-buttons-fields-and-texts.md) |
| `form` | `(rows: Sequence[tuple[str, Any]])` | Rows of a form (`QFormLayout`): a `(text, field)` for each. | [1](1-pages-and-layouts.md) |
| `grid_cell` | `(grid: Any, widget: Any, row: int, column: int, column_span: int=1, center: bool=False)` | Put `widget` in a cell of a grid (from `grid_scroll`), over `column_span` columns, centered in them when asked. | [1](1-pages-and-layouts.md) |
| `grid_scroll` | `(spacing: int=12)` | A scroll area with a grid in it, for cards side by side: | [1](1-pages-and-layouts.md) |
| `guide` | `(parent: Any, title: str, text: str, detail: str, buttons: Sequence[tuple[str, Callable[[], None]]], close_text: str)` | A message with a longer `detail` and a button for each `(text, callback)`, which runs its callback and closes it, and a last one (`close_text`) that only closes it. | [4](4-dialogs-and-menus.md) |
| `header_sorter` | `(table: Any, apply: Callable[[int, bool], None] \| None=None)` | Sort `table` when a header is clicked, ascending first and reversed on the next click, by what the cells mean (ages, numbers, versions). | [2](2-tables.md) |
| `icon` | `(name: str, color: str, **options: Any)` | An icon of the app by name, in `color`: `update`, `info`, `trash`, `bell`, `send`, `stop`, `attach`, `popout`, `dock`, `gear`, `chat-trash`, `close`, `plus`, `focus` (`active=True` for the leaving one) and `sparkle` (`size` and the `inside` color). | [6](6-services.md) |
| `icon_button` | `(icon: Any, tip: str, on_click: Callable[[], None] \| None=None, variant: str='link')` | A button that is only an icon (a `QIcon`), with its tip. | [3](3-buttons-fields-and-texts.md) |
| `image` | `(data: bytes, size: int)` | An image of those bytes, scaled to fit `size` pixels; `None` when it is not one that can be drawn. | [6](6-services.md) |
| `image_label` | `(size: int)` | A square, `size` pixels wide, for an image (`setPixmap`). | [3](3-buttons-fields-and-texts.md) |
| `is_alive` | `(widget: Any)` | Whether a widget still exists: the app deletes a page it built when it builds its menu again. | [6](6-services.md) |
| `item_checked` | `(item: Any)` | Whether the check box of a cell is checked; `None` when it has none. | [2](2-tables.md) |
| `label` | `(text: str='', variant: str='', wrap: bool=False, align: str='')` | A text (`QLabel`). | [3](3-buttons-fields-and-texts.md) |
| `let_window_shrink` | `(window: Any, shrink: bool)` | Let the main window be made as small as its layout allows (a page that needs no width), or give back the least it asked. | [6](6-services.md) |
| `menu` | `(parent: Any=None)` | A menu (`QMenu`), as the right click of a row opens. | [2](2-tables.md) |
| `muted_label` | `(text: str='')` | A note in the soft color of the app (`QLabel`). | [3](3-buttons-fields-and-texts.md) |
| `notice_card` | `(title: str, kind: str, about: str, message: str, when: str, level: str, unread: bool, tip: str, on_click: Callable[[], None], actions: Sequence[tuple[str, Callable[[], None]]]=())` | A card for a list of notices: `title` and `kind` on the first line, where it is `about`, its `message`, `when` it began and links `(text, callback)` under it. | [5](5-notices-panels-and-search.md) |
| `number_field` | `(minimum: int, maximum: int, value: int=0)` | A field for a whole number (`QSpinBox`) between `minimum` and `maximum`, as the forms of the app have them. | [3](3-buttons-fields-and-texts.md) |
| `on_context_menu` | `(table: Any, handler: Callable[[int, int], None])` | Call `handler(x, y)` on a right click in a table, with the place in its rows (`table.rowAt(y)` says which); open the menu with `show_menu`. | [2](2-tables.md) |
| `on_resize` | `(widget: Any, callback: Callable[[], None])` | Call `callback` when `widget` is resized. | [6](6-services.md) |
| `open_file` | `(parent: Any, title: str, start: str='')` | Ask the person to choose a file to open; its path, or an empty text when they gave up. | [4](4-dialogs-and-menus.md) |
| `open_url` | `(url: str)` | Open an address in the browser of the person. | [6](6-services.md) |
| `page` | `(parent: Any, *, filters: Any=None, actions: Any=None, notice: Any=None, body: Any=None, footer: Any=None)` | Lay `parent` (the widget of your page) out as the pages of the app: the `filters` row, the `actions` row, a `notice`, the `body` (which takes what is left) and the `footer` row; leave out what the page does not have. The rows are layouts, made with `row`. | [1](1-pages-and-layouts.md) |
| `palette` | `(parent: Any, title: str, placeholder: str, loading: str)` | The window that finds a screen, an action or a resource as one types, like a command palette: `open_with(entries)` shows it with entries that have `label`, `detail` and `run`; `set_resources(hits, run)` adds what was found in the cluster; `resources_failed(text)` says why not. | [5](5-notices-panels-and-search.md) |
| `row` | `(*items: Any, spacing: int=12)` | A row of widgets (`QHBoxLayout`). | [1](1-pages-and-layouts.md) |
| `scroll` | `(content: Any)` | `content` in a scroll area without a frame. | [1](1-pages-and-layouts.md) |
| `search_box` | `(placeholder: str='')` | The search box of the lists: a `QLineEdit` with the size and the clear button of the app. | [3](3-buttons-fields-and-texts.md) |
| `set_badge` | `(item: Any, status: str)` | Mark a cell (a `QTableWidgetItem`) as a badge in the colors of `status`, whatever its case: green when fine (Active, Normal), amber while it changes (Updating, Pending), red when it failed, grey for anything else. | [2](2-tables.md) |
| `set_badge_colors` | `(item: Any, text: str, fill: str)` | Mark a cell as a badge in those colors, for a state the words of `set_badge` do not name. | [2](2-tables.md) |
| `set_image` | `(label: Any, image: Any)` | Show an image from `image` in a label (see `image_label`). | [6](6-services.md) |
| `set_item_checked` | `(item: Any, checked: bool \| None)` | Give a cell a check box, checked or not; `None` takes it away. | [2](2-tables.md) |
| `set_time` | `(field: Any, text: str)` | Show a time given as `HH:mm` in a time field. | [3](3-buttons-fields-and-texts.md) |
| `show_menu` | `(menu: Any, table: Any, x: int, y: int)` | Open `menu` at the place `(x, y)` of the rows of `table`. | [2](2-tables.md) |
| `side_panel` | `(host: Any, title: str, actions: Sequence[Any], top: Callable[[], int], close_text: str='✕', empty_text: str='')` | A panel that slides in from the right edge of `host` (the `ui.central` widget), under the top bar (`top()` is where it starts): | [5](5-notices-panels-and-search.md) |
| `spacer` | `(height: int)` | Empty room `height` pixels high between the parts of a column. | [1](1-pages-and-layouts.md) |
| `switch_button` | `(text: str, tip: str)` | A square button that stays pressed, as the Aa (match case) and .* (regular expression) of a search box. | [3](3-buttons-fields-and-texts.md) |
| `table_item` | `(text: str, tip: str='', checked: bool \| None=None)` | A cell for a table (`QTableWidgetItem`) with the text color of the theme in use, and `tip` for its tip. | [2](2-tables.md) |
| `text_area` | `(placeholder: str='', max_height: int=0)` | A box of several lines of text to type in (`QPlainTextEdit`). | [3](3-buttons-fields-and-texts.md) |
| `text_field` | `(placeholder: str='')` | A line of text (`QLineEdit`) as the fields of the forms of the app. | [3](3-buttons-fields-and-texts.md) |
| `time_field` | `()` | A field for a time of the day, as `HH:mm` (`QTimeEdit`). | [3](3-buttons-fields-and-texts.md) |
| `time_text` | `(field: Any)` | The time of a time field, as `HH:mm`. | [3](3-buttons-fields-and-texts.md) |
| `timer` | `(interval_ms: int, callback: Callable[[], None], owner: Any=None, single_shot: bool=False)` | A timer that calls `callback` every `interval_ms` once it is started, or once with `single_shot`: `start()`, `stop()` and `is_active()`. | [6](6-services.md) |
| `widget` | `(shown: Callable[[], None] \| None=None, hidden: Callable[[], None] \| None=None, load: Callable[[], None] \| None=None, save: Callable[[], bool] \| None=None)` | The widget of your page, or of your section of the Settings, to give to `add_page` or `add_settings_section` and to lay out with `page`. | [1](1-pages-and-layouts.md) |

And, outside the components, in `kubescope.sdk`:

| Call | |
| ---- | - |
| `translate(context, text)` | the text in the language of the app: [Services](6-services.md#translatecontext-text) |
| `set_translator(translator)` | for the app, and for a test that wants another language: [Testing](8-testing.md#translating) |
