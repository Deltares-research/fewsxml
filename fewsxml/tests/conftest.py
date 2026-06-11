from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def ensemble_fixture() -> Path:
    return Path(__file__).resolve().parent / "fixtures" / "timeseries_import_ensemble.xml"
