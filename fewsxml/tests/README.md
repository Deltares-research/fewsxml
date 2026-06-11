# FEWSXML Tests

This package contains the pytest suite for `fewsxml`.

- `test_timeseries.py` contains the functional read/write and roundtrip tests.
- `fixtures/` contains fixed XML inputs used by tests; no external data checkout is required.
- `utils/` contains shared test helpers such as schema validation.

Run from the repository root:

```powershell
python -m pytest
```
