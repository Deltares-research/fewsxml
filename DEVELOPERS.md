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

Install development dependencies and enable the pre-commit hooks. This repository configures hooks for both commit time and push time:

```powershell
python -m pip install -e ".[dev]"
python -m pre_commit install
```

You can also run all hooks manually at any time:

```powershell
python -m pre_commit run --all-files
```
