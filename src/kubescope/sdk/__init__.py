"""The API the extensions of KubeScope are written against.

An extension imports from here and from nothing else of the app. This
package imports nothing of the app either, so it can be published on its
own. The API is unstable while `API_VERSION` is below 1.
"""

from kubescope.sdk.commands import CommandError
from kubescope.sdk.context import (
    API_VERSION,
    PERMISSIONS,
    App,
    AwsAccess,
    AwsScope,
    Cli,
    ClusterAccess,
    Context,
    Forwards,
    PermissionDenied,
    Settings,
    SettingsPanel,
    Ui,
    WriteModeOff,
    Writes,
)
from kubescope.sdk.contributions import (
    CliCommand,
    DockContribution,
    PageContribution,
    SettingsSection,
    ShortcutContribution,
    TabKind,
    ThemeContribution,
)
from kubescope.sdk.events import (
    CONTEXT_CHANGED,
    EVENTS,
    LANGUAGE_CHANGED,
    NOTIFICATION,
    SETTINGS_SHOWN,
    SHUTDOWN,
    THEME_CHANGED,
    WRITE_MODE_CHANGED,
    Events,
)

__all__ = [
    "API_VERSION",
    "App",
    "AwsAccess",
    "AwsScope",
    "CONTEXT_CHANGED",
    "EVENTS",
    "LANGUAGE_CHANGED",
    "NOTIFICATION",
    "PERMISSIONS",
    "SETTINGS_SHOWN",
    "SHUTDOWN",
    "THEME_CHANGED",
    "Cli",
    "CliCommand",
    "ClusterAccess",
    "CommandError",
    "Context",
    "DockContribution",
    "Forwards",
    "Events",
    "PageContribution",
    "PermissionDenied",
    "Settings",
    "SettingsPanel",
    "SettingsSection",
    "ShortcutContribution",
    "TabKind",
    "ThemeContribution",
    "Ui",
    "WRITE_MODE_CHANGED",
    "WriteModeOff",
    "Writes",
]
