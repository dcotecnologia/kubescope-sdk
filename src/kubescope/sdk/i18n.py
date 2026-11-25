"""Translate a text of an extension into the language of the app.

An extension writes `translate("Context", "Text")`; the app puts the
translator of its window here when it starts, so the SDK itself needs no
Qt. Until then (a test of the extension on its own) the text comes back
as it is. The tool that lists the texts of an extension finds the calls
by the name `translate`.
"""

from collections.abc import Callable

_translator: Callable[[str, str], str] | None = None


def set_translator(translator: Callable[[str, str], str] | None) -> None:
    """Called by the app: the function that translates a context and a text."""
    global _translator
    _translator = translator


def translate(context: str, text: str) -> str:
    """The text in the language of the app; `context` names where it is used,
    as the languages files of the extension keep it."""
    if _translator is None:
        return text
    return _translator(context, text)
