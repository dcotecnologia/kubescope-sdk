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
# The app has something to tell the person: level: str ("error", "warning" or
# "info"), title: str, message: str, key: str (the same key is the same
# notice) and repeat: bool (whether the same key happening again counts)
NOTIFICATION = "notification"

EVENTS = (
    CONTEXT_CHANGED,
    THEME_CHANGED,
    LANGUAGE_CHANGED,
    WRITE_MODE_CHANGED,
    SHUTDOWN,
    NOTIFICATION,
)


class Events(Protocol):
    def on(self, event: str, handler: Callable[..., None]) -> Callable[[], None]:
        """Call `handler` on every `event`; returns the function that stops
        it."""
        ...
