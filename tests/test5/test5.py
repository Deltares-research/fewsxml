import os.path
import sys
import fewsxml as fx
from utils import schema_validator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def run_example():
    parsed_timeseries = fx.read("timeseries_import.xml")

    fx.write(parsed_timeseries, "timeseries_export.xml")

    is_valid = schema_validator.is_pi_timeseries_valid("timeseries_export.xml")
    if is_valid:
        print("Cycle of read and write is valid.")
    else:
        print("Cycle of read and write is NOT valid.")
    assert is_valid

    # Making sure the forecast attribute is preserved
    original_forecast_date = parsed_timeseries.series[8].header.forecastDate.date
    assert original_forecast_date is not None
    assert original_forecast_date == "2014-01-01"
    original_forecast_time = parsed_timeseries.series[8].header.forecastDate.time
    assert original_forecast_time is not None
    assert original_forecast_time == "00:00:00"

    exported_timeseries = fx.read("timeseries_export.xml")
    exported_forecast_date = exported_timeseries.series[8].header.forecastDate.date
    assert exported_forecast_date is not None
    assert exported_forecast_date == "2014-01-01"
    exported_forecast_time = exported_timeseries.series[8].header.forecastDate.time
    assert exported_forecast_time is not None
    assert exported_forecast_time == "00:00:00"


if __name__ == "__main__":
    run_example()
