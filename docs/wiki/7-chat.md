# 7. A chat with an assistant

[Wiki](README.md) · previous: [Services](6-services.md) · next: [Testing](8-testing.md)

The Gabi extension is a chat with an assistant of the computer (Claude Code, Codex). The chat itself —
the round button in the corner, the panel, the conversation as bubbles, the message field, the files
attached, the ring that says how full the conversation is — is drawn by the app. The extension says what
the conversation does.

## `chat_dock(host, name, texts)`

The round button in the corner of `host` (`ui.central`) and the chat panel it opens. The panel can be resized
by its borders, taken out into a window of its own, or made to fill the page of the window (the focus mode);
its size, whether it is out and where are kept by you.

```python
self.dock = c.chat_dock(ui.central, "Gabi", {"Ask Gabi": translate("Dock", "Ask Gabi"),
                                              "Settings": translate("Panel", "Settings"), ...})
self.dock.bubble.clicked.connect(self.open_or_close)
self.dock.panel.closed.connect(self.put_away)
self.dock.restore(settings.assistant_panel)           # the size and place kept
self.dock.state_changed.connect(lambda: setattr(settings, "assistant_panel", self.dock.state()))
```

`texts` are the words of the button and the panel, by their English text, as you translated them
(`Ask Gabi`, `Settings`, `Clear history`, `Close`, `New session`, `Put it back in the window`,
`Open in a window of its own`, `Leave the focus mode`, `Focus mode: the chat fills the page`). One you do not
give stays in English. On a language change: `dock.retranslate(new_texts)`.

| Member | |
| ------ | - |
| `bubble` | the round button; `bubble.setVisible(...)` shows it or not |
| `panel` | the panel: signals `closed`, `new_session_requested`, `focus_requested`, `clear_requested`, `settings_requested`; `show_chat(widget)`, `set_engine(text)`, `title`, `engine` |
| `open()`, `close()`, `dispose()`, `place()` | open or put the panel away; `dispose()` undoes the window of its own; `place()` puts it where it belongs after the host changed |
| `is_open`, `is_floating`, `is_focused`, `is_yielding` | its state |
| `set_focus(bool)`, `set_yielding(bool)`, `set_floating(bool)`, `toggle_floating()` | the modes |
| `gutter` | how much of the corner the button takes: give it to `ui.reserve_corner(ctx.id, gutter)` |
| `content_area` | set it to `ui.content_area`, so the focus mode fills the pages |
| `state()`, `restore(state)`, `state_changed` | what to keep, and to put back |
| `restyle()`, `retranslate(texts)` | the theme or the language changed |

## `chat_view(texts)`

The conversation laid out as a chat: what the person writes on the right, what comes back on the left, and
the composer under it. Put it in the panel: `dock.panel.show_chat(view)`.

```python
view = c.chat_view(
    {
        "welcome": "Hi, I'm Gabi.",
        "placeholder": "Ask Gabi...",
        "Send": "Send",
        "Stop": "Stop",
        "Attach": "Attach",
        "Open {name}": "Open {name}",
        "{count} lines": "{count} lines",
    }
)
```

`texts` are its words by their English text (`welcome`, `placeholder`, `Send`, `Stop`, `Attach`,
`Open {name}`, `{count} lines` and the file filter `Images and text files ({patterns});;All files (*)`). On a
language change: `view.set_texts(new_texts)`.

### What the person does: signals

| Signal | When |
| ------ | ---- |
| `submitted` | Enter, or the Send button (Shift+Enter goes to the next line) |
| `stop_requested` | the Stop button |
| `attach_requested` | the Attach button: answer with `choose_files` |
| `image_pasted(png_bytes)` | a picture was pasted into the field |
| `files_pasted(paths)` | files were pasted from a file manager |
| `text_pasted(text)` | a long text (2000 characters or more) was pasted: attach it instead of typing it |
| `ring_clicked` | the ring: answer with `show_ring_menu` |
| `usage_expired` | the cache of the prompt is over: say the usage again |

### What you tell it

| Call | |
| ---- | - |
| `add_bubble(role, text, clock, files=(), on_open=...)` | a bubble at the end. `role` is `user` (right), `assistant` (left, as markdown) or `app` (left, dashed: a note the assistant does not see). Returns the text of the bubble, with `setText(text)` to grow an answer as it comes. `files` are attached files shown as pills, `on_open(file)` opens one |
| `drop_last_bubble()` | take the last one back (an answer that failed) |
| `set_busy(bool)` | while the assistant answers, Send is Stop |
| `show_status(text)` | a line under the conversation; empty takes no room |
| `set_usage(text, tip, fraction, ring_tip, expires_in)` | the tokens used under the field; `fraction` (0 to 1) fills the ring; the line is asked for again `expires_in` ms later (0: never) |
| `show_ring_menu(lines, compact_text, can_compact, on_compact, auto_text, auto_on, on_auto)` | the menu of the ring |
| `show_chips(items, on_open, on_detach)` | the files attached, each with a × to take it off |
| `choose_files(title, patterns)` | ask which files to attach: a list of paths |
| `open_attachment(item)` | open a copy with the program of the system; the text of why not, or `""` |
| `add_action_card(text, run_text, cancel_text, on_run, on_cancel)` | a change the assistant asked for, waiting for the person; `remove_card(card)` takes it away |
| `restyle()`, `set_texts(texts)` | the theme or the language changed |

An attached file is any object with `name`, `kind` (`image` or `text`), `data` (bytes) and `text`.

The parts are attributes for a test: `input`, `send_button`, `stop_button`, `attach_button`, `status`,
`usage_label`, `ring`, `cards`, `chips`, `chip_bar`, `thread_view`, `thread_scroll`, `welcome`, `composer`.

## Putting it together

```python
class Conversation:
    def __init__(self, ctx, session):
        c = ctx.ui.components
        self.c = c
        self.session = session
        self.view = c.chat_view(texts())
        self.view.submitted.connect(self.submit)
        self.view.stop_requested.connect(self.stop)

    def submit(self):
        text = self.view.input.toPlainText().strip()
        self.view.input.clear()
        self.view.add_bubble("user", text, now())
        self.view.set_busy(True)
        self.answer = None

        def produce():
            stream = self.session.send(text)
            try:
                yield from stream
            finally:
                stream.close()

        self.worker = self.c.background(
            produce,
            on_piece=self.piece,
            on_error=self.failed,
            on_finished=self.finished,
            stream=True,
        )

    def piece(self, piece):
        self.text = getattr(self, "text", "") + piece
        if self.answer is None:
            self.answer = self.view.add_bubble("assistant", self.text, now())
        else:
            self.answer.setText(self.text)

    def stop(self):
        self.worker.stopped = True

    def failed(self, message):
        self.view.show_status(message)

    def finished(self):
        self.view.set_busy(False)
```

`kubescope-ai-gabi` is the whole of it: the extension keeps the session, the history, the actions the
assistant may ask for and the settings; the app draws.
