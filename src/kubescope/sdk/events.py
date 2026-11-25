"""The events the app tells the extensions about.

No Qt. An extension subscribes with `on` and gets the payload as keyword
arguments. The app never lets a handler that raises stop the others.
"""

from collections.abc import Callable
from typing import Protocol

CONTEXT_CHANGED = "context_changed"  # context: str | None
THEME_CHANGED = "theme_changed"
LANGUAGE_CHANGED = "language_changed"
WRITE_MODE_CHANGED = "write_mode_changed"  # write_mode: bool
SHUTDOWN = "shutdown"
# The Settings page was opened or left: shown: bool
SETTINGS_SHOWN = "settings_shown"
# The app has something to tell the person: level: str ("error", "warning" or
# "info"), title: str, message: str, key: str (the same key is the same
# notice), repeat: bool (whether the same key happening again counts) and
# context: str (the context in use when it happened, "" when it is about none),
# and, for a notice of something done: category: str ("action", "pod" or
# "task"), click: a function to call when it is clicked, or None, and system:
# bool (whether the system should be told, which the extension decides)
NOTIFICATION = "notification"

EVENTS = (
    CONTEXT_CHANGED,
    THEME_CHANGED,
    LANGUAGE_CHANGED,
    WRITE_MODE_CHANGED,
    SHUTDOWN,
    SETTINGS_SHOWN,
    NOTIFICATION,
)


class Events(Protocol):
    def on(self, event: str, handler: Callable[..., None]) -> Callable[[], None]:
        """Call `handler` on every `event`; returns the function that stops
        it."""
        ...
