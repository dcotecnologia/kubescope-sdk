import pytest

from kubescope.sdk.errors import ClusterError, first_line


def test_first_line_skips_blank_lines() -> None:
    assert first_line("\n  \n  boom  \nsecond") == "boom"
    assert first_line("") == ""


def test_a_failure_of_the_cluster_is_an_error_with_a_message() -> None:
    with pytest.raises(ClusterError, match="no route"):
        raise ClusterError("no route")
    assert issubclass(ClusterError, RuntimeError)
