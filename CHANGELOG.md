# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dcotecnologia/kubescope-sdk/releases/tag/v1.0.0
