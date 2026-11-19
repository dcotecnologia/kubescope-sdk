"""Hide the secrets that may appear in a line of text.

Whatever an extension sends, shows or writes down that came from the cluster
or from a program goes through this first: tokens, keys and passwords are
replaced, so that a log or a chat can be read and shared.
"""

import re

_SECRETS = (
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{8,}"), r"\1[redacted]"),
    (
        re.compile(
            r"(?i)((?:token|secret|password|passwd|authorization|access[_-]?key"
            r"|session[_-]?token|x-amz-[a-z-]*)[\"']?\s*[:=]\s*[\"']?)[^\s\"',;&]+"
        ),
        r"\1[redacted]",
    ),
    (re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "[redacted-key-id]"),
    (re.compile(r"\bk8s-aws-v1\.[A-Za-z0-9_-]+"), "[redacted]"),
    (
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]*"),
        "[redacted]",
    ),
)


def redact(text: str) -> str:
    """Hide tokens, keys and passwords that may appear in a line of text."""
    for pattern, replacement in _SECRETS:
        text = pattern.sub(replacement, text)
    return text
