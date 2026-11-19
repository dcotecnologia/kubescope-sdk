"""Small helpers for the text of errors."""


def first_line(text: str) -> str:
    """The first non-empty line, for one-line summaries and logs."""
    return next((line.strip() for line in text.splitlines() if line.strip()), "")
