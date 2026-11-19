# Security Policy

## Reporting a vulnerability

Please **do not open a public issue** for a vulnerability. Use
[GitHub private vulnerability reporting](https://github.com/dcotecnologia/kubescope-sdk/security/advisories/new)
for this repository, or write to the maintainers listed in `pyproject.toml`. We acknowledge a report
within a few days, tell you what we found, and credit you in the release notes if you want.

## Supported versions

Only the latest release receives fixes.

## What it is

This package is the contract between KubeScope and its extensions. It contains no code that reaches the
network or a cluster by itself: it describes what the app lends to an extension and checks nothing at run
time. What an extension can do is decided by the app and by the permissions in its manifest; read
[docs/permissions.md](docs/permissions.md) for what is and is not enforced.

## Guarantees this project keeps

- It has no dependencies and imports neither the app nor Qt, so it can be audited in a few minutes.
- A test keeps it that way.
- Every release is a tag built by the release pipeline from the changelog.
