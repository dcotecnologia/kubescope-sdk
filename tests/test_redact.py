import pytest

from kubescope.sdk.redact import redact


def _fake(*parts: str) -> str:
    """Join a made-up secret from pieces, so no literal in this file looks like
    a real one to the secret scanner."""
    return "".join(parts)


@pytest.mark.parametrize(
    ("template", "hidden"),
    [
        ("Authorization: Bearer {}", _fake("abcdef12", "34567890")),
        ("token={}", _fake("not-a-", "real-value-", "12345")),
        ("aws_secret_access_key = {}", _fake("FAKE", "SECRETVALUE", "1234567")),
        ("key {} in use", _fake("AK", "IA", "ABCDEFGHIJKLMNOP")),
        ("exec token {}", _fake("k8s-aws-", "v1.", "ZmFrZS1wcmVzaWduZWQ")),
        (
            "jwt {}",
            _fake("ey", "JhbGciOiJIUzI1NiJ9.", "eyJzdWIiOiIxMjM0", ".c2ln-fake"),
        ),
        ('{{"password": "{}"}}', _fake("fake-", "pass-", "value-1")),
    ],
)
def test_redact_hides_secrets(template: str, hidden: str) -> None:
    text = template.format(hidden)

    assert hidden not in redact(text)
    assert "redacted" in redact(text)


def test_redact_keeps_ordinary_text() -> None:
    line = "Exit 0 after 0.31s: kubectl --context prod get pods -n default"
    assert redact(line) == line
