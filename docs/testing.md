# Testing an extension

Test the logic of an extension without the app, and the integration inside it.

## Without the app

`Context` and its services are `Protocol`s, so a test passes a small fake with the members the extension
uses.

```python
from kubescope.sdk import AwsScope


class FakeAws:
    def __init__(self):
        self.answers = {}
        self.asked = []

    def uses_aws(self, context):
        return True

    def scope(self, context):
        return AwsScope("us-east-1", "work", "123456789012")

    def regions(self):
        return ("us-east-1",)

    def run(self, context, command, region=""):
        self.asked.append((context, command, region))
        return self.answers.get(tuple(command[:2]), {})


def test_the_instances_are_read(ctx):
    ctx.aws.answers[("rds", "describe-db-instances")] = {"DBInstances": [...]}
    assert [one.identifier for one in rds.instances(ctx.aws, "ctx")] == ["orders"]
```

Keep a fake `ui` whose `run_action` runs the function at once and calls `on_success` or `on_error`, so a
page can be tested without threads. [kubescope-aws](https://github.com/dcotecnologia/kubescope-aws) has a
complete set in `tests/conftest.py`.

For widgets, set `QT_QPA_PLATFORM=offscreen` and replace `QDialog.exec`, `QMenu.exec` and `QMessageBox.exec`
so that a test that opens a modal dialog fails instead of hanging.

## Keep the extension independent

A test can enforce that the extension imports nothing of KubeScope but the SDK and itself:

```python
import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def test_it_imports_only_the_sdk_and_itself():
    found = []
    for path in SRC.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names = (
                [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else []
            )
            found += [
                n
                for n in names
                if n.split(".")[0] == "kubescope"
                and n.split(".")[:2]
                not in (["kubescope", "sdk"], ["kubescope", "mine"])
            ]
    assert found == []
```

## Inside the app

An integration test can run the extension in the real window with the real services, as
`kubescope-aws/tests/test_in_the_app.py` does: it needs the app as a development dependency
(`kubescope = { path = "../kubescope", editable = true }`) and activates the extension with an
`ExtensionContext` of the app. Only the tests need the app; the extension never does.

## By hand, with hot reload

Tick **Development mode** in **Settings → Extensions** and install your folder: the app runs it in place and
reloads it when a file changes.

## Commands

```bash
make test FILE=tests/test_page.py   # one file
make lint typecheck
```
