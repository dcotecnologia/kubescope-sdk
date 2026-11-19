"""Where KubeScope keeps what it writes down. No Qt.

`KUBESCOPE_CONFIG_DIR` overrides the folder, which is what the tests and a
person who wants it elsewhere use.
"""

import os
import sys
from pathlib import Path

CONFIG_DIR_ENV = "KUBESCOPE_CONFIG_DIR"


def config_directory() -> Path:
    """The folder of the settings and of everything else the app keeps."""
    override = os.environ.get(CONFIG_DIR_ENV)
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "kubescope"
