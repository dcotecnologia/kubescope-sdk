import ast
from pathlib import Path

import kubescope.sdk as sdk

SDK = Path(sdk.__file__).parent


def test_the_sdk_imports_nothing_of_the_app() -> None:
    offenders: list[str] = []
    for path in SDK.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            offenders += [
                f"{path.name}: {module}"
                for module in modules
                if module.split(".")[0] == "PySide6"
                or (
                    module.split(".")[0] == "kubescope"
                    and module.split(".")[:2] != ["kubescope", "sdk"]
                )
            ]

    assert offenders == []


def test_every_name_the_sdk_exports_exists() -> None:
    assert all(hasattr(sdk, name) for name in sdk.__all__)
    assert sdk.API_VERSION == "0"
    assert set(sdk.EVENTS) == {
        sdk.CONTEXT_CHANGED,
        sdk.THEME_CHANGED,
        sdk.LANGUAGE_CHANGED,
        sdk.WRITE_MODE_CHANGED,
        sdk.SHUTDOWN,
        sdk.SETTINGS_SHOWN,
        sdk.NOTIFICATION,
    }


def _names(protocol: type) -> set[str]:
    return {
        name
        for name in {*vars(protocol), *getattr(protocol, "__annotations__", {})}
        if not name.startswith("_")
    }


def test_the_cluster_access_lists_what_an_extension_may_read() -> None:
    assert _names(sdk.ClusterAccess) >= {
        "LOG_WINDOW_BYTES",
        "get_workloads",
        "get_pods",
        "get_pod_logs",
        "get_pod_container_usage",
        "get_usage",
        "get_resources",
        "get_resource_details",
        "get_events",
        "list_contexts",
        "describe_kube",
    }


def test_an_extension_may_add_a_button_to_the_top_bar() -> None:
    assert {"add_top_bar_button", "show_system_notification"} <= _names(sdk.Ui)


def test_a_cluster_event_is_plain_data_with_an_identity() -> None:
    from kubescope.sdk.models import ClusterEvent

    event = ClusterEvent("u1", "Warning", "BackOff", "ns", "Pod", "p", "m", 2, 1.0, 5.0)
    assert (event.uid, event.reason, event.last_seen) == ("u1", "BackOff", 5.0)


def test_the_writes_are_named_and_there_is_no_way_to_run_something_else() -> None:
    names = _names(sdk.Writes)

    assert names == {
        "scale_deployment",
        "restart_deployment",
        "evict_pod",
        "delete_pod",
        "delete_resource",
        "replace_resource",
    }


def test_the_terminal_lends_only_what_it_can_do_without_a_window() -> None:
    assert _names(sdk.Cli) == {"choose_context", "confirm"}


def test_a_page_is_a_permission_and_plain_data() -> None:
    page = sdk.PageContribution("dco.a", "AWS", "RDS", "Instances", lambda: None)

    assert "ui.page" in sdk.PERMISSIONS
    assert (page.section, page.group, page.title) == ("AWS", "RDS", "Instances")
    assert page.visible is None and page.subtitle == "" and page.refresh is None


def test_the_aws_scope_names_where_a_context_signs_in() -> None:
    scope = sdk.AwsScope("us-east-1", "work", "123456789012")

    assert (scope.region, scope.profile, scope.account) == (
        "us-east-1",
        "work",
        "123456789012",
    )
    assert "aws.read" in sdk.PERMISSIONS


def test_a_forward_is_a_permission_of_its_own() -> None:
    assert "forward" in sdk.PERMISSIONS
    assert sdk.Forwards is not None


def test_a_theme_is_a_permission_and_plain_data() -> None:
    theme = sdk.ThemeContribution("dco.a", "midnight", {"name": "Midnight"})

    assert "ui.theme" in sdk.PERMISSIONS
    assert (theme.extension, theme.id, theme.document["name"]) == (
        "dco.a",
        "midnight",
        "Midnight",
    )
