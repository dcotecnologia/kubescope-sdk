# Contributing to KubeScope SDK

Thanks for helping. This page gets you from a clone to a pull request. The commit format, the code of
conduct and the standards of the whole project are those of
[KubeScope](https://github.com/dcotecnologia/kubescope):

- [COMMITING.md](https://github.com/dcotecnologia/kubescope/blob/main/COMMITING.md): Conventional Commits, in English.
- [CODE_OF_CONDUCT.md](https://github.com/dcotecnologia/kubescope/blob/main/CODE_OF_CONDUCT.md).
- [AGENTS.md](https://github.com/dcotecnologia/kubescope/blob/main/AGENTS.md): the code standards, for people and AI assistants alike.

## Set up

```bash
git clone https://github.com/dcotecnologia/kubescope-sdk.git
cd kubescope-sdk
make setup          # uv sync and the pre-commit hook
```

The SDK has no dependencies and imports neither the app nor Qt; a test enforces it.

## Workflow

1. Create a branch from `main`. Do not commit to `main` directly.
2. Make one focused change per commit, with its tests.
3. Run the checks below, and add an entry to `CHANGELOG.md` under **[Unreleased]**.
4. Open a pull request that says what changed and why. The pipeline runs the same checks.

## Checks

```bash
make test FILE=tests/test_x.py   # the test file of your change
make lint typecheck
```

Run one test file at a time while you work; the pipeline runs them all.

## Releases

A release is a tag. Bump the version in `pyproject.toml`, move the **[Unreleased]**
entries of `CHANGELOG.md` under the new version, merge, and push the tag `vX.Y.Z`. The release pipeline
checks that the tag, the versions and the changelog agree, lints and tests, and publishes the release with the built package.
