# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.10.0] - 2026-11-24

### Added

- `Ui.show_system_notification` takes a `category` (`action`, `pod`, `task`), so the notifications extension can keep the notice and let the person choose which kinds are listed and told, and the `notification` event carries it by @danilogco

## [1.9.0] - 2026-11-24

### Added

- `Writes.run_remove(context, arguments)`, to run the commands that remove an add-on or a Helm release (`aws eks delete-addon`, `helm uninstall`, `az k8s-extension delete`), only in the write mode and only those by @danilogco

## [1.8.0] - 2026-11-24

### Added

- `natural_key(text)`, a sort key that orders what a table cell says as a person would (ages, numbers, versions and text), so that the tables of the extensions sort the way the ones of the app do by @danilogco

## [1.7.0] - 2026-11-24

### Added

- `ClusterAccess.eks_target(context)` and `ClusterAccess.aks_cluster(context)`, the arguments that name the EKS cluster and the name and resource group of the AKS cluster of a context, for the command that updates an add-on by @danilogco

## [1.6.0] - 2026-11-24

### Added

- `ClusterAccess.environment(context)` and `ClusterAccess.helm_chart_name(...)`, and `Writes.run_update(context, arguments)`, so that an extension can show the add-ons and the Helm releases of a cluster and update them, with the write mode and a short list of commands guarding the update by @danilogco

## [1.5.0] - 2026-11-23

### Added

- `ClusterAccess.get_custom_resources(context, group, version, plural, namespace)` and `Writes.patch_custom_resource(...)`, to read and merge-patch the custom resources (CRDs) of a cluster, for an extension about one of them by @danilogco
- `Context.set_pages(key, pages)` and the model `PageSpec`, to give the side menu pages that are known only while the app runs (the custom resources of a cluster) by @danilogco

## [1.4.0] - 2026-11-22

### Added

- The event `SETTINGS_SHOWN` (`shown`), for an extension whose panel fills the pages to give the Settings their place by @danilogco
- `Ui.content_area()`, the area of the window between the top bar and the footer, for a panel that takes the place of the pages by @danilogco
- `Ui.hide_side_menu(owner, hidden)`, to hide the side menu of the window while an extension needs the whole width, such as a focus mode by @danilogco

## [1.3.0] - 2026-11-20

### Added

- `ClusterAccess.get_events(context, types)` and the model `ClusterEvent` (`uid`, `type`, `reason`, `namespace`, `kind`, `name`, `message`, `count`, `first_seen`, `last_seen`), the events of the cluster with what an extension needs to follow them over time by @danilogco
- The event `NOTIFICATION` (`level`, `title`, `message`, `key`, `repeat`), with which the app tells an extension about an error, a warning or an update, to list them by @danilogco
- `ClusterAccess.list_contexts()`, the contexts of the kubeconfig, and `Ui.show_system_notification(title, message, on_click)`, a notification of the operating system whose click brings the app forward by @danilogco
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

[Unreleased]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.10.0...HEAD
[1.10.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.9.0...v1.10.0
[1.9.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.8.0...v1.9.0
[1.8.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.6.0...v1.7.0
[1.6.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.5.0...v1.6.0
[1.5.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/dcotecnologia/kubescope-sdk/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dcotecnologia/kubescope-sdk/releases/tag/v1.0.0
