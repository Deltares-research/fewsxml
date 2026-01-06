import os.path
import sys

import fewsxml as fx
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils import schema_validator

def run_example():
    parsed_timeseries = fx.read("timeseries_import.xml")

    fx.write(parsed_timeseries, "timeseries_export.xml")

    is_valid = schema_validator.is_pi_timeseries_valid("timeseries_export.xml")
    if is_valid:
        print(f"Cycle of read and write is valid.")
    else:
        print(f"Cycle of read and write is NOT valid.")
    return is_valid

if __name__ == "__main__":
    assert run_example()