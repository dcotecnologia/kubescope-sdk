import sys
from pathlib import Path

from kubescope.sdk.paths import CONFIG_DIR_ENV, config_directory


def test_the_folder_can_be_chosen_with_the_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv(CONFIG_DIR_ENV, str(tmp_path / "chosen"))

    assert config_directory() == tmp_path / "chosen"


def test_config_directory_follows_the_platform(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv(CONFIG_DIR_ENV, raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "roaming"))
    assert config_directory() == tmp_path / "roaming" / "kubescope"
    monkeypatch.delenv("APPDATA")
    assert config_directory() == tmp_path / "AppData" / "Roaming" / "kubescope"

    monkeypatch.setattr(sys, "platform", "darwin")
    assert (
        config_directory() == tmp_path / "Library" / "Application Support" / "kubescope"
    )

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert config_directory() == tmp_path / "xdg" / "kubescope"
    monkeypatch.delenv("XDG_CONFIG_HOME")
    assert config_directory() == tmp_path / ".config" / "kubescope"
