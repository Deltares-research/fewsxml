import os
from pathlib import Path
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


def test_ensemble_and_missing_timezone_roundtrip(tmp_path):
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
    assert parsed.series[0].event[0].customAttr == "kept"
    exported = tmp_path / "ensemble_no_timezone_export.xml"
    fx.write(parsed, str(exported))
    reparsed = fx.read(str(exported))
    assert reparsed.timeZone is None
    assert reparsed.series[0].header.ensembleId == "main"
    assert reparsed.series[0].header.ensembleMemberIndex == 3
    assert reparsed.series[0].event[0].customAttr == "kept"


def test_namespaced_typed_properties_roundtrip(tmp_path):
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
    props = parsed.series[0].properties
    assert [type(p) for p in props] == [
        PIStringProperty,
        PIDoubleProperty,
        PILongProperty,
        PIIntProperty,
        PIBooleanProperty,
        PIDateProperty,
        PIDateTimeProperty,
    ]
    exported = tmp_path / "properties_export.xml"
    fx.write(parsed, str(exported))
    reparsed = fx.read(str(exported))
    assert [type(p) for p in reparsed.series[0].properties] == [
        PIStringProperty,
        PIDoubleProperty,
        PILongProperty,
        PIIntProperty,
        PIBooleanProperty,
        PIDateProperty,
        PIDateTimeProperty,
    ]
    assert reparsed.series[0].properties[4].value is True


def test_rtc_tools_ensemble_fixture_is_parsed():
    fixture = (
        Path(os.environ["RTC_TOOLS_ROOT"])
        / "tests"
        / "data"
        / "data"
        / "timeseries_import_ensemble.xml"
    )
    parsed = fx.read(str(fixture))
    assert [series.header.ensembleMemberIndex for series in parsed.series] == [0, 1]


if __name__ == "__main__":
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ.setdefault("RTC_TOOLS_ROOT", r"C:\Code\rtc-tools")
        tmp_path = Path(temp_dir)
        test_ensemble_and_missing_timezone_roundtrip(tmp_path)
        test_namespaced_typed_properties_roundtrip(tmp_path)
        test_rtc_tools_ensemble_fixture_is_parsed()
