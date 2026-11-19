# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/) once the API is stable (`API_VERSION` 1);
until then, any release may change the API.

## [Unreleased]

### Added

- The tests check the coverage, which stays at 100% as in KubeScope, and the pipeline publishes the badge
- The guides of the SDK in `docs/`: getting started, the manifest, the context, the contributions, the permissions and testing
- A pipeline that lints, type-checks and tests on every pull request, and a release pipeline for the tags `v*`

## [0.1.0] - 2026-11-19

### Added

- The contract between KubeScope and its extensions: `Context`, its services (`ClusterAccess`, `Writes`, `AwsAccess`, `Forwards`, `Ui`, `App`, `Settings`, `Cli`), the permissions and the errors
- The contributions of an extension: a page in the side menu with an optional refresh button, a section of the Settings, a shortcut, a command of the terminal, a panel and a kind of tab
- The events the app tells the extensions about, and the commands of the window an extension can call
- The models of the cluster and helpers: `redact`, `paths`, `timezone`, `ansi`, `programs` and `flatpak`

[Unreleased]: https://github.com/dcotecnologia/kubescope-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dcotecnologia/kubescope-sdk/releases/tag/v0.1.0
