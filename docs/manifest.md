# The manifest

Every extension has a `kubescope-extension.toml` at the root of its folder. It is the only thing the app
reads before the person agrees to install the extension, so it is checked strictly: a manifest that does not
fit is refused with a message that says which field is wrong. It is at most 16 KiB.

```toml
id = "kubescope.aws"
name = "AWS"
version = "1.0.0"
api = "0"
entry = "kubescope.aws:activate"
description = "Look at your AWS account from KubeScope."
author = "DCO Tecnologia"
permissions = ["aws.read", "forward", "ui.page", "ui.window"]
commands = ["chat"]          # only with the permission "cli"
production = ["assets"]      # what else stays when it is installed
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
| `production` | no | List of the folders and files at the top of the extension that stay when it is installed, like `assets`. Names only (no `/` inside, no `..`), at most 20. The required ones below, and `languages`, are always kept and need not be listed |

## What an extension must have, and what is installed

Four things are **required** at the top of every extension, and an extension without one of them is refused
when it is installed (from a folder, a zip or GitHub) and when it runs in development mode:

| Required | Why |
| -------- | --- |
| `kubescope-extension.toml` | The manifest |
| `LICENSE` | The person installs code that runs in the app and should know under what terms |
| `README.md` | What the extension does, shown with it |
| `src` | The folder the code runs from; `entry` is looked up in it |

When an extension is installed, **only what the manifest says is for production stays**: the four required
ones, `languages` (its translations, optional: kept when it exists, never required) and the names in
`production`. Everything else at the top of the folder (tests, `docs`, `tools`, the
pipeline, `pyproject.toml`, `CHANGELOG.md`, caches) is left out. Only the top level is looked at: inside a
folder that stays, nothing is removed. An extension that keeps anything else, like images in `assets`, must
list it:

```toml
production = ["assets"]
```

The sha256 the person sees in the install dialog is of everything that was downloaded, not only of what
stays. An extension that runs from its own folder (development mode) is never pruned. When the app opens, an
extension installed earlier is pruned by the same rule, so add `production` before you release a version
that needs more than the required ones.

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

The app imports `entry` from the `src` folder of the extension, which is required. The module must be inside
that folder: a name that resolves to another loaded package is refused.

## Recommended extensions

The app can recommend an extension: it shows a card with an **Install** button in **Settings →
Extensions**. What it downloads is pinned by tag and by the sha256 of that tag, so the person gets exactly
what was checked, never what the tag points at later. To be recommended, ask the maintainers of KubeScope.
