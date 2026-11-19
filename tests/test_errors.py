from kubescope_sdk.errors import first_line


def test_first_line_skips_blank_lines() -> None:
    assert first_line("\n  \n  boom  \nsecond") == "boom"
    assert first_line("") == ""
