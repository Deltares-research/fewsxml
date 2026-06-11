# Developer Guide

This guide contains setup and workflow information for contributors and maintainers of `fewsxml`.

## Running Tests

Install the package with its test dependencies, then run pytest from the repository root:

```powershell
python -m pip install -e ".[test]"
python -m pytest
```

The pytest suite lives in `fewsxml/tests`, and fixed XML inputs used by the tests live in `fewsxml/tests/fixtures`. Test output files are written to pytest-managed temporary directories, so no test log or export artifacts are created in the repository.

## Local CI Checks

GitHub Actions runs the same core checks on pushes and pull requests:

```powershell
python -m flake8 .
python -m pytest -q
```

The GitHub Actions test job runs on Python 3.11 and 3.14.

Install development dependencies and enable the pre-commit hooks. This repository configures hooks for both commit time and push time:

```powershell
python -m pip install -e ".[dev]"
python -m pre_commit install
```

You can also run all hooks manually at any time:

```powershell
python -m pre_commit run --all-files
```

## Publishing

Publishing to PyPI is handled by GitHub Actions when a pushed tag starts with `v`, for example `v0.2.1`.

The publish job uses the GitHub Environment named `pypi`. Store the PyPI API token value in that environment as a secret named `PYPI_API_TOKEN`.

Before publishing, update the package version in these places:

1. `setup.py`
   - Update the `version="X.Y.Z"` argument.
2. `fewsxml/__init__.py`
   - Update `__version__ = "X.Y.Z"`.
3. The release tag
   - Use the same version prefixed with `v`, for example `vX.Y.Z`.

Keep all three values consistent. For example, for release `0.2.1`, use `version="0.2.1"`, `__version__ = "0.2.1"`, and tag `v0.2.1`.

Recommended release flow:

```powershell
git checkout main
git pull
git tag vX.Y.Z
git push origin vX.Y.Z
```
