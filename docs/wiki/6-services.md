# 6. Services

[Wiki](README.md) · previous: [Notices, panels and search](5-notices-panels-and-search.md) · next: [A chat with an assistant](7-chat.md)

What an extension needs of Qt besides widgets: translating, timers, threads, icons, images, links, the
clipboard.

## `translate(context, text)`

```python
from kubescope.sdk import translate

title = translate("MyPage", "Instances")
count = translate("MyPage", "{count} instances").format(count=3)
```

The text comes back in the language of the app. `context` names where it is used, as the language files of
the extension keep it (`languages/<code>.json`). Write the **context and the text as literals** at the call:
the tool that lists the texts of an extension (`pyside6-lupdate`, run by `make i18n`) finds the call by its
name `translate` and reads those two literals. A variable in place of the literal is not found.

Call it when you draw, not when the module loads, so a change of language is followed: build the texts in
the function that builds the page, and again where you handle a language change. Until the app starts, in a
test of the extension on its own, the text comes back as it is.

## `timer(interval_ms, callback, owner=None, single_shot=False)`

A timer that calls `callback` every `interval_ms` once started (once, with `single_shot`). It goes away with
`owner`, a widget.

```python
self.timer = c.timer(30_000, self.load, self.widget)  # every 30 seconds
self.timer.start()  # in shown()
self.timer.stop()  # in hidden()
self.timer.is_active()

retry = c.timer(3000, self.retry, single_shot=True)  # once; start() again to repeat
retry.start()
```

It is a `QTimer`: `setInterval`, `interval()`, `isActive()`, `start()`, `start(msec)`, `stop()` and the
`timeout` signal work.

## `after(delay_ms, owner, callback)`

Calls `callback` once, in `delay_ms`, unless `owner` is gone by then.

```python
c.after(500, self.widget, self.read_again)
```

## `background(function, on_piece=None, on_done=None, on_error=None, on_finished=None, stream=False)`

Runs `function` off the UI thread and tells you on it. It returns a handle with `stopped` and `wait(ms)`.

| Callback | Called with |
| -------- | ----------- |
| `on_done(answer)` | what `function` returned |
| `on_piece(piece)` | each piece a generator gives (`stream=True`) |
| `on_error(message)` | the text of the exception it raised |
| `on_finished()` | at the end, whatever happened |

```python
# one answer
self.worker = c.background(
    lambda: read_the_cluster(context),
    on_done=self.arrived,
    on_error=self.failed,
    on_finished=lambda: setattr(self, "worker", None),
)


# an answer that comes in pieces, which the person can cut short
def produce():
    stream = session.send(question)
    try:
        yield from stream
    finally:
        stream.close()  # stops the program when the answer was cut short


self.worker = c.background(
    produce,
    on_piece=self.piece,
    on_error=self.failed,
    on_finished=self.finished,
    stream=True,
)
self.worker.stopped = (
    True  # the person pressed Stop: no more pieces, and the generator is closed
)
```

Everything the callbacks do happens on the UI thread, so they can touch widgets. `function` runs in another
thread: it must not touch widgets. For a plain call that gives one answer, `ctx.ui.run_action(function,
on_success, *arguments, on_error=None, quiet=False)` is the shorter way; use `background` when you need to
stop it, wait for it or have its pieces.

To end cleanly, `handle.stopped = True` and `handle.wait(3000)` before the page goes.

## `icon(name, color, **options)`

An icon of the app by name, in `color`.

| Name | Looks like |
| ---- | ---------- |
| `update` | an arrow rising from a base |
| `info` | a circle with an i |
| `trash` | a bin |
| `bell` | a bell |
| `send` | a paper plane |
| `stop` | a square |
| `attach` | a plus |
| `popout`, `dock` | a square with an arrow leaving or entering it |
| `gear` | a cog |
| `chat-trash` | a bin, for clearing the chat |
| `close`, `plus` | a cross, a plus |
| `focus` | four corners (`active=True` for the ones that leave the mode) |
| `sparkle` | a speech bubble with a star (`size=`, `inside=` color) |

```python
color = ui.themed("#3220a0")
details.setIcon(c.icon("info", color))
c.icon("focus", color, active=True)
c.icon("sparkle", "#ffffff", size=28, inside=ui.themed("#3020a5"))
```

The color is fixed when the icon is made: draw it again when the theme changes (`THEME_CHANGED` event).

## `image(data, size)` and `set_image(label, image)`

`image` makes an image from the bytes of a file (a PNG, a JPEG) scaled to fit `size` pixels; `None` when the
bytes are not an image that can be drawn. `set_image` shows it in a label; `image_label(size)` is a square to
show it in.

```python
logo = c.image_label(56)
image = c.image(data, 56)
if image is not None:
    c.set_image(logo, image)
```

Keep the image you made to draw again without reading the file again.

## `open_url(url)`

Opens an address in the browser of the person. `c.open_url(chart.link)`.

## `copy_text(text)`

Puts a text on the clipboard. `c.copy_text(command)`.

## `on_resize(widget, callback)`

Calls `callback()` (no arguments) when `widget` is resized: the catalog uses it on the viewport of its scroll
area to fit more cards side by side.

```python
c.on_resize(area.viewport(), self.fit_columns)
```

## `bottom_of(widget, host)`

Where the bottom edge of `widget` is, as a y in the coordinates of `host`: a panel under a button of the top
bar starts at `c.bottom_of(self.bell, ui.central) + 6`.

## `is_alive(widget)`

Whether a widget still exists. The app deletes a page it built when it builds its menu again; a refresh button
that reaches a page it kept asks first.

```python
if current and c.is_alive(current[0].widget):
    current[0].reload()
```

## `let_window_shrink(window, shrink)`

Lets the main window (`ui.window`) be made as small as its layout allows (a page that needs no width), or gives
back the least it asked. Calling it twice with the same value does nothing the second time.

## Services that are not components

`ctx.ui` has the calls that are not about looking: `show_message`, `run_action`, `pick_item`, `show_json`,
`open_log`, `show_settings`, `themed`, `show_system_notification`, `add_top_bar_button`, `reserve_corner`,
`content_area`, `hide_side_menu`. See [the context](../api.md#the-window-ctxui--uiwindow).
