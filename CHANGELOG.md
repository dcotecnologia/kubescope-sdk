# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `ClusterAccess.get_events(context, types)` and the model `ClusterEvent` (`uid`, `type`, `reason`, `namespace`, `kind`, `name`, `message`, `count`, `first_seen`, `last_seen`), the events of the cluster with what an extension needs to follow them over time by @danilogco
- `Ui.add_top_bar_button(owner, button)`, to put a button in the top bar beside the Settings by @danilogco

## [1.2.1] - 2026-11-20

### Fixed

- Document in the manifest page `production`, what an extension keeps when it is installed (`languages` is always kept when it exists), and that `kubescope-extension.toml`, `LICENSE`, `README.md` and `src` are required by @danilogco

## [1.2.0] - 2026-11-20

### Added

- `Context.add_theme(theme_id, document)` and the permission `ui.theme`, so an extension offers color themes

## [1.1.0] - 2026-11-20

### Added

- `ClusterAccess.search_resources(context)`, the names of the main resources of every namespace, and the window command `views`, the lists of the side menu, which an extension that searches the app needs
- The SDK depends on PySide6 (`pyside6>=6.12.0`), which an extension needs to draw anything, so an extension lists only `kubescope-sdk`; the SDK itself still imports no Qt

## [1.0.0] - 2026-11-19

### Added

- The contract between KubeScope and its extensions: `Context`, its services (`ClusterAccess`, `Writes`, `AwsAccess`, `Forwards`, `Ui`, `App`, `Settings`, `Cli`), the permissions and the errors
- The contributions of an extension: a page in the side menu with an optional refresh button, a section of the Settings, a shortcut, a command of the terminal, a panel and a kind of tab
- The events the app tells the extensions about, and the commands of the window an extension can call
- The models of the cluster and helpers: `redact`, `paths`, `timezone`, `ansi`, `programs` and `flatpak`

[Unreleased]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dcotecnologia/kubescope-sdk/releases/tag/v1.0.0
