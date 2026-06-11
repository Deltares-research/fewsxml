from datetime import datetime
from pathlib import Path

import pytest

import fewsxml as fx
from fewsxml import (
    PIBooleanProperty,
    PIDateProperty,
    PIDateTimeProperty,
    PIDoubleProperty,
    PIIntProperty,
    PILongProperty,
    PIStringProperty,
)
from fewsxml.tests.utils import schema_validator


def _sample_pi_timeseries(time_step: fx.PITimeStep) -> fx.PITimeSeries:
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
    events = [
        {"date": datetime(2024, 1, 1, 10, 0, 0), "value": 10.1, "flag": 0},
        {"date": datetime(2024, 1, 1, 11, 0, 0), "value": 12.5, "flag": 0},
        {"date": datetime(2024, 1, 1, 12, 0, 0), "value": 11.8, "flag": 0},
    ]
    series = fx.create_pi_series(header=header, events=events)
    return fx.create_pi_timeseries(series=series, time_zone=1.0)


@pytest.mark.parametrize(
    "time_step",
    [
        pytest.param(fx.PITimeStep(unit="hour", multiplier=1), id="hourly"),
        pytest.param(fx.PITimeStep(unit="second", multiplier=600.0), id="integer-like-float"),
    ],
)
def test_created_timeseries_is_schema_valid(time_step: fx.PITimeStep, tmp_path: Path) -> None:
    output = tmp_path / "sample_output_timeseries.xml"

    fx.write(_sample_pi_timeseries(time_step), str(output))

    assert schema_validator.is_pi_timeseries_valid(str(output))
    if time_step.unit == "second":
        assert 'multiplier="600"' in output.read_text(encoding="utf-8")


def test_imported_timeseries_roundtrip_is_schema_valid(fixtures_dir: Path, tmp_path: Path) -> None:
    parsed_timeseries = fx.read(str(fixtures_dir / "timeseries_import.xml"))
    output = tmp_path / "timeseries_export.xml"

    fx.write(parsed_timeseries, str(output))

    assert schema_validator.is_pi_timeseries_valid(str(output))


def test_qualifier_ids_roundtrip(fixtures_dir: Path, tmp_path: Path) -> None:
    parsed_xml = fx.read(str(fixtures_dir / "timeseries_import_with_qualifier.xml"))
    output = tmp_path / "timeseries_export_with_qualifier.xml"

    fx.write(parsed_xml, str(output))

    assert parsed_xml.series[0].header.qualifierId == ["Minimum"]
    assert parsed_xml.series[1].header.qualifierId == ["Maximum"]

    parsed_xml2 = fx.read(str(output))
    assert parsed_xml2.series[0].header.qualifierId == ["Minimum"]
    assert parsed_xml2.series[1].header.qualifierId == ["Maximum"]


def test_forecast_date_roundtrip(fixtures_dir: Path, tmp_path: Path) -> None:
    parsed_timeseries = fx.read(str(fixtures_dir / "timeseries_import_with_forecast.xml"))
    output = tmp_path / "timeseries_export.xml"

    fx.write(parsed_timeseries, str(output))

    assert schema_validator.is_pi_timeseries_valid(str(output))

    original_forecast_date = parsed_timeseries.series[8].header.forecastDate.date
    original_forecast_time = parsed_timeseries.series[8].header.forecastDate.time
    assert original_forecast_date == "2014-01-01"
    assert original_forecast_time == "00:00:00"

    exported_timeseries = fx.read(str(output))
    exported_forecast_date = exported_timeseries.series[8].header.forecastDate.date
    exported_forecast_time = exported_timeseries.series[8].header.forecastDate.time
    assert exported_forecast_date == "2014-01-01"
    assert exported_forecast_time == "00:00:00"


def test_ensemble_and_missing_timezone_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "ensemble_no_timezone.xml"
    source.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<pi:TimeSeries xmlns:pi="http://www.wldelft.nl/fews/PI" version="1.2">
  <pi:series>
    <pi:header>
      <pi:type>instantaneous</pi:type>
      <pi:locationId>Reservoir</pi:locationId>
      <pi:parameterId>QI</pi:parameterId>
      <pi:qualifierId>TEST</pi:qualifierId>
      <pi:ensembleId>main</pi:ensembleId>
      <pi:ensembleMemberIndex>3</pi:ensembleMemberIndex>
      <pi:timeStep unit="nonequidistant" />
      <pi:startDate date="2024-01-01" time="00:00:00" />
      <pi:endDate date="2024-01-01" time="01:00:00" />
      <pi:forecastDate date="2024-01-01" time="00:00:00" />
      <pi:missVal>-999.0</pi:missVal>
      <pi:units>m3/s</pi:units>
    </pi:header>
    <pi:event date="2024-01-01" time="00:00:00" value="1.0" flag="0" customAttr="kept" />
    <pi:event date="2024-01-01" time="01:00:00" value="NaN" flag="2" />
  </pi:series>
</pi:TimeSeries>
""",
        encoding="utf-8",
    )

    parsed = fx.read(str(source))

    assert parsed.timeZone is None
    assert parsed.series[0].header.ensembleId == "main"
    assert parsed.series[0].header.ensembleMemberIndex == 3
    assert parsed.series[0].header.timeStep.unit == "nonequidistant"
    assert getattr(parsed.series[0].event[0], "customAttr") == "kept"

    exported = tmp_path / "ensemble_no_timezone_export.xml"
    fx.write(parsed, str(exported))
    reparsed = fx.read(str(exported))
    assert reparsed.timeZone is None
    assert reparsed.series[0].header.ensembleId == "main"
    assert reparsed.series[0].header.ensembleMemberIndex == 3
    assert getattr(reparsed.series[0].event[0], "customAttr") == "kept"


def test_namespaced_typed_properties_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "properties.xml"
    source.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<pi:TimeSeries xmlns:pi="http://www.wldelft.nl/fews/PI" version="1.2">
  <pi:timeZone>0.0</pi:timeZone>
  <pi:series>
    <pi:header>
      <pi:type>instantaneous</pi:type>
      <pi:locationId>L</pi:locationId>
      <pi:parameterId>P</pi:parameterId>
      <pi:timeStep unit="second" multiplier="3600" />
      <pi:startDate date="2024-01-01" time="00:00:00" />
      <pi:endDate date="2024-01-01" time="00:00:00" />
    </pi:header>
    <pi:properties>
      <pi:string key="s" value="abc" />
      <pi:double key="d" value="1.5" />
      <pi:long key="l" value="123456" />
      <pi:int key="i" value="7" />
      <pi:boolean key="b" value="true" />
      <pi:date key="date" value="2024-01-02" />
      <pi:dateTime key="dt" date="2024-01-02" time="03:04:05" />
    </pi:properties>
    <pi:event date="2024-01-01" time="00:00:00" value="1.0" />
  </pi:series>
</pi:TimeSeries>
""",
        encoding="utf-8",
    )

    parsed = fx.read(str(source))
    expected_property_types = [
        PIStringProperty,
        PIDoubleProperty,
        PILongProperty,
        PIIntProperty,
        PIBooleanProperty,
        PIDateProperty,
        PIDateTimeProperty,
    ]
    assert [type(prop) for prop in parsed.series[0].properties] == expected_property_types

    exported = tmp_path / "properties_export.xml"
    fx.write(parsed, str(exported))
    reparsed = fx.read(str(exported))
    assert [type(prop) for prop in reparsed.series[0].properties] == expected_property_types
    assert reparsed.series[0].properties[4].value is True


def test_ensemble_fixture_is_parsed(ensemble_fixture: Path) -> None:
    parsed = fx.read(str(ensemble_fixture))

    assert [series.header.ensembleMemberIndex for series in parsed.series] == [0, 1]
