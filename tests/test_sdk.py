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
        sdk.SHUTDOWN,
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
        "describe_kube",
    }


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
