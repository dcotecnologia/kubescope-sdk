from kubescope.sdk.models import RESOURCE_KINDS


def test_the_kinds_are_sorted_and_have_no_repeats() -> None:
    assert tuple(sorted(set(RESOURCE_KINDS))) == RESOURCE_KINDS
    assert "Deployment" in RESOURCE_KINDS and "Pod" in RESOURCE_KINDS
    assert "Node" not in RESOURCE_KINDS  # it is read, but not changed by name
