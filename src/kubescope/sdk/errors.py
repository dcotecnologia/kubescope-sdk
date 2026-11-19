"""What goes wrong when a cluster or a program is asked something, and small
helpers for the text of errors."""

class ClusterError(RuntimeError):
    """Raised when a request to the cluster or an AWS CLI command fails."""


def first_line(text: str) -> str:
    """The first non-empty line, for one-line summaries and logs."""
    return next((line.strip() for line in text.splitlines() if line.strip()), "")
