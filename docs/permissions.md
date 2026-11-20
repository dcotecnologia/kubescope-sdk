# Permissions and security

An extension is **Python that runs inside the app**, with the same rights as the app. The permissions in its
manifest catch mistakes and tell the person what it does; they are **not a sandbox**. Install only extensions
you trust, and read what the dialog shows.

## The permissions

| Permission | The person sees | What it unlocks |
| ---------- | --------------- | --------------- |
| `cluster.read` | read your clusters | `ctx.cluster` |
| `cluster.write` | change your clusters, in the write mode | `ctx.writes` |
| `aws.read` | read your AWS account (RDS, EC2, EKS, Systems Manager) | `ctx.aws` |
| `forward` | start a port forward to a database, in the write mode | `ctx.forwards` |
| `subprocess` | run programs of this computer | none in the SDK: the person is told |
| `ui.window` | use the window: messages, tasks, shortcuts | `ctx.ui`, `ctx.add_shortcut` |
| `ui.page` | add a page to the side menu | `ctx.add_page` |
| `ui.settings` | add a section to the Settings | `ctx.add_settings_section` |
| `ui.theme` | add color themes | `ctx.add_theme` |
| `ui.dock` | add a panel to the window | `ctx.add_dock` |
| `ui.tab` | add a kind of tab | `ctx.add_tab_kind` |
| `cli` | add a command to kubescope | `ctx.add_cli_command`, `ctx.cli` |

Ask for the least you need. A manifest with a permission it does not use makes a person read more for
nothing, and an extension that calls a service it did not ask for fails with `PermissionDenied`.

## What is enforced

- **The install dialog.** Nothing of an extension runs before the person confirms a dialog that shows where
  it came from, its version, its permissions and the sha256 of its content. An update with other content
  asks again.
- **The write mode.** Writes and forwards raise `WriteModeOff` while it is off.
- **A list of AWS reads.** `ctx.aws.run` refuses any command that is not a read of an allowed service and any
  option that moves the request to another account, region or server.
- **A strict copy.** What is installed is limited in size and number of files, refuses links and names that
  leave its folder, and leaves out `.git`, virtual environments and caches.
- **Isolation of failures.** An extension that fails to load, or in a handler, is logged and taken back; it
  never stops the app or the others.
- **Its own state.** Settings and data folders are kept by id.

## What is not

- An extension can import any module and read any file the app can. A permission does not stop `open()`.
- `subprocess` is a declaration, not a barrier.
- The keys of an AWS account never reach the extension through `ctx.aws`, but code running in the app is
  in the same process as the app.

## For authors

- Do not log what `redact` would scrub, and use it before you log a command line or an answer.
- Never write secrets to `ctx.settings` (they are in a plain JSON file) or to `ctx.data_directory`.
- Make slow calls with `ctx.ui.run_action`, and handle `ClusterError`: it is the normal failure.
- Say in your README why you ask for each permission.
