"""What an extension can add to the app, as plain data.

No Qt. The window reads these entries and builds the widgets; the
`factory` of each is whatever builds it (the SDK never imports Qt).
Every entry knows which extension put it there, so removing an extension
removes its entries.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DockContribution:
    """A panel in the corner of the window, with a button that opens it."""

    extension: str
    key: str
    factory: Callable[..., Any]
    shortcut: str = ""


@dataclass(frozen=True)
class PageContribution:
    """A page of the window, with its entry in the side menu: `title` in the
    menu `group` of the `section`. `factory` builds its widget the first time
    it is opened; `visible` says whether the entry shows."""

    extension: str
    section: str
    group: str
    title: str
    factory: Callable[..., Any]
    subtitle: str = ""
    visible: Callable[[], bool] | None = None
    refresh: Callable[[], None] | None = None  # the refresh button of the header


@dataclass(frozen=True)
class TabKind:
    """A kind of tab the window can open, besides its own."""

    extension: str
    key: str
    factory: Callable[..., Any]


@dataclass(frozen=True)
class SettingsSection:
    """A section of the Settings, built by the extension."""

    extension: str
    title: str
    factory: Callable[..., Any]


@dataclass(frozen=True)
class ShortcutContribution:
    """A keyboard shortcut of the window that runs a function of the extension;
    `default` is the key the person gets until they change it. With
    `application` it works from every window of the app, not only the main one."""

    extension: str
    action: str
    label: str
    default: str
    handler: Callable[[], None]
    application: bool = False


@dataclass(frozen=True)
class CliCommand:
    """A subcommand of `kubescope`, run with the rest of the arguments."""

    extension: str
    name: str
    run: Callable[[list[str]], int]
