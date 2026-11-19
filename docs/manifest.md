# The manifest

Every extension has a `kubescope-extension.toml` at the root of its folder. It is the only thing the app
reads before the person agrees to install the extension, so it is checked strictly: a manifest that does not
fit is refused with a message that says which field is wrong. It is at most 16 KiB.

```toml
id = "kubescope.aws"
name = "AWS"
version = "1.0.1"
api = "0"
entry = "kubescope.aws:activate"
description = "Look at your AWS account from KubeScope."
author = "DCO Tecnologia"
permissions = ["aws.read", "forward", "ui.page", "ui.window"]
commands = ["chat"]          # only with the permission "cli"
```

| Field | Required | Rule |
| ----- | -------- | ---- |
| `id` | yes | Lowercase `author.name`, with letters, digits, `_` and `-`, and at least one dot. It is the identity of the extension: its settings, its data folder and its commands are named by it |
| `name` | yes | Text shown on the card, at most 300 characters |
| `version` | yes | `MAJOR.MINOR.PATCH`, each up to six digits |
| `api` | yes | The API of the SDK it was written for. It must be the one the app offers (`"0"` today) |
| `entry` | yes | `package.module:function`, the function the app calls with the context |
| `description` | no | Text shown on the card, at most 300 characters |
| `author` | no | Text shown on the card |
| `permissions` | no | List of the permissions it needs. An unknown one is refused. See [permissions.md](permissions.md) |
| `commands` | no | Up to eight different names (`chat`, `ask-me`) of the commands it adds to `kubescope`. Needs `cli`. The app knows them without running the extension |

## The identity

- **The id is forever.** Settings (`ctx.settings`) and the data folder (`ctx.data_directory`) are kept by id.
  Changing it makes the extension a different one.
- **Commands** registered with `ctx.register_command` are named `<id>.<name>`.
- Two installed extensions can never have the same id.

## Versions and updates

An update whose content differs from the installed one asks the person again. The content hash is the
sha256 of the files of the folder that has the manifest, the same for a folder, a zip and a GitHub archive.
Bump `version` on every release: the card shows it, and a pin by tag (see below) names it.

## Where the code is looked up

The app imports `entry` from the folder of the extension, or from its `src` folder when it has one. The
module must be inside that folder: a name that resolves to another loaded package is refused.

## Recommended extensions

The app can recommend an extension: it shows a card with an **Install** button in **Settings →
Extensions**. What it downloads is pinned by tag and by the sha256 of that tag, so the person gets exactly
what was checked, never what the tag points at later. To be recommended, ask the maintainers of KubeScope.
