import os.path
import sys
import fewsxml as fx
from datetime import datetime
from utils import schema_validator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


def run_example():
    """
    Creates a sample PI-XML time series file.
    """
    # 1. Define the header for the time series
    # For an equidistant series, a timeStep is needed.
    time_step = fx.PITimeStep(unit="hour", multiplier=1)

    header = fx.create_pi_header(
        type="instantaneous",
        location_id="test_location",
        parameter_id="H.test",
        start_date=datetime(2024, 1, 1, 10, 0, 0),
        end_date=datetime(2024, 1, 1, 12, 0, 0),
        timeStep=time_step,
        missVal="-999.9",
        stationName="Test Station",
        units="m",
    )

    # 2. Define the events (data points) for the series
    events = [
        {"date": datetime(2024, 1, 1, 10, 0, 0), "value": 10.1, "flag": 0},
        {"date": datetime(2024, 1, 1, 11, 0, 0), "value": 12.5, "flag": 0},
        {"date": datetime(2024, 1, 1, 12, 0, 0), "value": 11.8, "flag": 0},
    ]

    # 3. Create a PISeries object
    series = fx.create_pi_series(header=header, events=events)

    # 4. Create the root PITimeSeries object
    # This can contain one or more PISeries objects
    pi_timeseries = fx.create_pi_timeseries(series=series, time_zone=1.0)

    # 5. Write the object to an XML file
    output_filename = "sample_output_timeseries.xml"
    fx.write(pi_timeseries, output_filename)

    print(f"Successfully created '{output_filename}'")

    # 6. Validate the created XML file
    is_valid = schema_validator.is_pi_timeseries_valid(output_filename)
    if is_valid:
        print(f"'{output_filename}' is valid.")
    else:
        print(f"'{output_filename}' is NOT valid.")
    return is_valid


if __name__ == "__main__":
    assert run_example()
