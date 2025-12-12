from __future__ import annotations
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field
from xml.dom import minidom


# ======================================================
# BASE MODEL (allows unknown attributes)
# ======================================================

class XModel(BaseModel):
    model_config = dict(extra="allow")


# ======================================================
# BASIC DATE/TIME
# ======================================================

class PIDateTime(XModel):
    date: str
    time: str


# ======================================================
# PROPERTIES
# ======================================================

class PIStringProperty(XModel):
    key: str
    value: str


class PIDoubleProperty(XModel):
    key: str
    value: float


class PILongProperty(XModel):
    key: str
    value: int


class PIIntProperty(XModel):
    key: str
    value: int


class PIBooleanProperty(XModel):
    key: str
    value: bool


class PIDateProperty(XModel):
    key: str
    date: str


class PIDateTimeProperty(XModel):
    key: str
    date: str
    time: str


PIProperty = Union[
    PIStringProperty,
    PIDoubleProperty,
    PILongProperty,
    PIIntProperty,
    PIBooleanProperty,
    PIDateProperty,
    PIDateTimeProperty,
]


# ======================================================
# THRESHOLDS
# ======================================================

class PIThresholdBase(XModel):
    id: Optional[str] = None
    name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None
    groupId: Optional[str] = None
    groupName: Optional[str] = None
    value: float


class PIHighLevelThreshold(PIThresholdBase):
    pass


class PILowLevelThreshold(PIThresholdBase):
    pass


class PIThresholds(XModel):
    highLevelThreshold: Optional[List[PIHighLevelThreshold]] = None
    lowLevelThreshold: Optional[List[PILowLevelThreshold]] = None


# ======================================================
# TIMESTEP
# ======================================================

class PITimeStep(XModel):
    unit: Optional[str] = None
    multiplier: Optional[int] = None
    minutes: Optional[int] = None


# ======================================================
# EVENT
# ======================================================

class PIEvent(XModel):
    date: Optional[str] = None
    time: Optional[str] = None

    startDate: Optional[str] = None
    startTime: Optional[str] = None
    endDate: Optional[str] = None
    endTime: Optional[str] = None

    value: Optional[Union[float, str]] = None
    minValue: Optional[float] = None
    maxValue: Optional[float] = None

    flag: Optional[int] = None

    # unknown fs:* attributes accepted automatically (via extra="allow")


# ======================================================
# HEADER
# ======================================================

class PIHeader(XModel):
    type: str

    moduleInstanceId: Optional[str] = None
    locationId: str
    parameterId: str

    qualifierId: Optional[List[str]] = None

    ensembleId: Optional[str] = None
    ensembleMemberIndex: Optional[int] = None

    timeStep: Optional[PITimeStep] = None

    startDate: PIDateTime
    endDate: PIDateTime
    forecastDate: Optional[PIDateTime] = None

    missVal: Optional[str] = None
    stationName: Optional[str] = None

    lat: Optional[float] = None
    lon: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None

    longName: Optional[str] = None
    units: Optional[str] = None

    sourceOrganisation: Optional[str] = None
    sourceSystem: Optional[str] = None

    fileDescription: Optional[str] = None

    creationDate: Optional[str] = None
    creationTime: Optional[str] = None

    thresholds: Optional[PIThresholds] = None


# ======================================================
# SERIES
# ======================================================

class PISeries(XModel):
    header: PIHeader
    properties: Optional[List[PIProperty]] = None
    event: List[PIEvent]


# ======================================================
# ROOT
# ======================================================

class PITimeSeries(XModel):
    version: Optional[str]
    timeZone: float
    series: List[PISeries]




def _set_if_not_none(elem: ET.Element, tag: str, value):
    """Create a subelement <tag>value</tag> if value is not None."""
    if value is not None:
        sub = ET.SubElement(elem, tag)
        sub.text = str(value)


def _add_date_time(parent: ET.Element, tag: str, dt):
    """Create something like: <startDate date="YYYY-MM-DD" time="HH:MM:SS" />"""
    if dt:
        elem = ET.SubElement(parent, tag)
        elem.set("date", dt.date)
        elem.set("time", dt.time)


def _add_time_step(parent: ET.Element, ts):
    if ts:
        elem = ET.SubElement(parent, "timeStep")
        if ts.unit is not None:
            elem.set("unit", ts.unit)
        if ts.multiplier is not None:
            elem.set("multiplier", str(ts.multiplier))
        if ts.minutes is not None:
            elem.set("minutes", str(ts.minutes))


def _add_properties(parent: ET.Element, properties):
    if not properties:
        return
    for p in properties:
        tag = "property"
        # Each property becomes:
        # <property key="..." value="...">
        elem = ET.SubElement(parent, tag)
        elem.set("key", p.key)

        # Identify type-specific fields
        if hasattr(p, "value"):
            elem.set("value", str(p.value))
        if hasattr(p, "date"):
            elem.set("date", p.date)
        if hasattr(p, "time"):
            elem.set("time", p.time)


def _add_thresholds(parent: ET.Element, thresholds):
    if not thresholds:
        return

    ts_elem = ET.SubElement(parent, "thresholds")

    def add(th_list, tag):
        if not th_list:
            return
        for th in th_list:
            elem = ET.SubElement(ts_elem, tag)
            for attr in [
                "id", "name", "label", "description", "comment",
                "groupId", "groupName", "value"
            ]:
                val = getattr(th, attr, None)
                if val is not None:
                    elem.set(attr, str(val))

    add(thresholds.highLevelThreshold, "highLevelThreshold")
    add(thresholds.lowLevelThreshold, "lowLevelThreshold")


def _add_event(parent: ET.Element, ev):
    elem = ET.SubElement(parent, "event")

    # date/time
    if ev.date is not None:
        elem.set("date", ev.date)
    if ev.time is not None:
        elem.set("time", ev.time)

    # start / end date + time
    if ev.startDate is not None:
        elem.set("startDate", ev.startDate)
    if ev.startTime is not None:
        elem.set("startTime", ev.startTime)
    if ev.endDate is not None:
        elem.set("endDate", ev.endDate)
    if ev.endTime is not None:
        elem.set("endTime", ev.endTime)

    # value
    if ev.value is not None:
        elem.set("value", str(ev.value))

    # min/max
    if ev.minValue is not None:
        elem.set("minValue", str(ev.minValue))
    if ev.maxValue is not None:
        elem.set("maxValue", str(ev.maxValue))

    # flag
    if ev.flag is not None:
        elem.set("flag", str(ev.flag))

    # unknown attributes (fs:*)
    for k, v in ev.__dict__.items():
        if k.startswith("fs:"):
            elem.set(k, str(v))

# ---------------------------------------------------------------------
def fx_write(pi: "PITimeSeries", filename: str):
    NS = "http://www.wldelft.nl/fews/PI"
    XSI = "http://www.w3.org/2001/XMLSchema-instance"

    ET.register_namespace("", NS)
    ET.register_namespace("xsi", XSI)

    root = ET.Element(
        f"{{{NS}}}TimeSeries",
        {
            "version": pi.version if pi.version else "",
            f"{{{XSI}}}schemaLocation":
                f"{NS} https://fewsdocs.deltares.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd",
        },
    )

    # <timeZone>
    _set_if_not_none(root, "timeZone", pi.timeZone)

    # Each <series>
    for s in pi.series:
        s_elem = ET.SubElement(root, "series")

        # ------------------- HEADER -------------------
        h = s.header
        h_elem = ET.SubElement(s_elem, "header")

        _set_if_not_none(h_elem, "type", h.type)
        _set_if_not_none(h_elem, "moduleInstanceId", h.moduleInstanceId)
        _set_if_not_none(h_elem, "locationId", h.locationId)
        _set_if_not_none(h_elem, "parameterId", h.parameterId)

        # qualifierId is a list
        if h.qualifierId:
            for q in h.qualifierId:
                _set_if_not_none(h_elem, "qualifierId", q)

        _set_if_not_none(h_elem, "ensembleId", h.ensembleId)
        _set_if_not_none(h_elem, "ensembleMemberIndex", h.ensembleMemberIndex)

        # timeStep
        _add_time_step(h_elem, h.timeStep)

        # Dates
        _add_date_time(h_elem, "startDate", h.startDate)
        _add_date_time(h_elem, "endDate", h.endDate)
        if h.forecastDate:
            _add_date_time(h_elem, "forecastDate", h.forecastDate)

        # Simple fields
        for tag in [
            "missVal", "stationName", "lat", "lon", "x", "y", "z",
            "longName", "units", "sourceOrganisation", "sourceSystem",
            "fileDescription", "creationDate", "creationTime"
        ]:
            _set_if_not_none(h_elem, tag, getattr(h, tag))

        # thresholds
        _add_thresholds(h_elem, h.thresholds)

        # ------------------- PROPERTIES -------------------
        _add_properties(s_elem, s.properties)

        # ------------------- EVENTS -------------------
        for ev in s.event:
            _add_event(s_elem, ev)

    # Pretty printing
    xml_bytes = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(indent="  ", encoding="utf-8")

    with open(filename, "wb") as f:
        f.write(pretty)





NS = {"pi": "http://www.wldelft.nl/fews/PI"}

# ----------------------------------------------------------------------
# Helper: read date/time composite element
# ----------------------------------------------------------------------
def _parse_date_time(elem: ET.Element) -> PIDateTime:
    return PIDateTime(
        date=elem.attrib.get("date"),
        time=elem.attrib.get("time")
    )


# ----------------------------------------------------------------------
# Helper: parse typed <properties>
# ----------------------------------------------------------------------
def _parse_property(elem: ET.Element) -> PIProperty:

    tag = elem.tag

    # Simple key/value types
    if tag == "string":
        return PIStringProperty(key=elem.attrib["key"], value=elem.attrib["value"])
    if tag == "double":
        return PIDoubleProperty(key=elem.attrib["key"], value=float(elem.attrib["value"]))
    if tag == "long":
        return PILongProperty(key=elem.attrib["key"], value=int(elem.attrib["value"]))
    if tag == "int":
        return PIIntProperty(key=elem.attrib["key"], value=int(elem.attrib["value"]))
    if tag == "boolean":
        v = elem.attrib["value"].lower() == "true"
        return PIBooleanProperty(key=elem.attrib["key"], value=v)

    # Date property
    if tag == "date":
        return PIDateProperty(key=elem.attrib["key"], date=elem.attrib["value"])

    # Date-time property
    if tag == "dateTime":
        return PIDateTimeProperty(
            key=elem.attrib["key"],
            date=elem.attrib["date"],
            time=elem.attrib["time"]
        )

    raise ValueError(f"Unknown property tag: {tag}")


# ----------------------------------------------------------------------
# Helper: thresholds
# ----------------------------------------------------------------------
def _parse_thresholds(elem: ET.Element) -> PIThresholds:
    highs = []
    lows = []

    for h in elem.findall("pi:highLevelThreshold", namespaces=NS):
        attrs = {k: v for k, v in h.attrib.items() if k != "value"}
        highs.append(PIHighLevelThreshold(value=float(h.attrib["value"]), **attrs))

    for l in elem.findall("pi:lowLevelThreshold", namespaces=NS):
        attrs = {k: v for k, v in l.attrib.items() if k != "value"}
        lows.append(PILowLevelThreshold(value=float(l.attrib["value"]), **attrs))

    return PIThresholds(
        highLevelThreshold=highs or None,
        lowLevelThreshold=lows or None
    )


# ----------------------------------------------------------------------
# Helper: parse <event>
# ----------------------------------------------------------------------
def _parse_event(elem: ET.Element) -> PIEvent:
    attrs = dict(elem.attrib)

    # Convert numeric fields where needed
    if "value" in attrs:
        v = attrs["value"]
        try:
            attrs["value"] = float(v)
        except ValueError:
            attrs["value"] = v  # allow NaN or text

    if "minValue" in attrs:
        attrs["minValue"] = float(attrs["minValue"])
    if "maxValue" in attrs:
        attrs["maxValue"] = float(attrs["maxValue"])
    if "flag" in attrs:
        attrs["flag"] = int(attrs["flag"])

    return PIEvent(**attrs)


# ----------------------------------------------------------------------
# Helper: parse <header>
# ----------------------------------------------------------------------
def _parse_header(elem: ET.Element) -> PIHeader:
    type_text = elem.findtext("pi:type", namespaces=NS)
    attribs = {"type": type_text}

    # Required simple text elements:
    locationId = elem.findtext("pi:locationId", namespaces=NS)
    parameterId = elem.findtext("pi:parameterId", namespaces=NS)

    attribs["locationId"] = locationId
    attribs["parameterId"] = parameterId

    # qualifierId list
    qualifiers = [q.text for q in elem.findall("pi:qualifierId", namespaces=NS)]
    if qualifiers:
        attribs["qualifierId"] = qualifiers

    # moduleInstanceId
    if (mi := elem.findtext("pi:moduleInstanceId", namespaces=NS)) is not None:
        attribs["moduleInstanceId"] = mi

    # times
    attribs["startDate"] = _parse_date_time(elem.find("pi:startDate", namespaces=NS))
    attribs["endDate"] = _parse_date_time(elem.find("pi:endDate", namespaces=NS))

    if (fd := elem.find("pi:forecastDate", namespaces=NS)) is not None:
        attribs["forecastDate"] = _parse_date_time(fd)

    # timeStep
    if (ts := elem.find("pi:timeStep", namespaces=NS)) is not None:
        ts_kwargs = {k: int(v) if k in ("multiplier", "minutes") else v
                     for k, v in ts.attrib.items()}
        attribs["timeStep"] = ts_kwargs

    # optional scalar tags
    optional_tags = [
        "missVal", "stationName", "longName", "units", "sourceOrganisation",
        "sourceSystem", "fileDescription", "creationDate", "creationTime",
        "lat", "lon", "x", "y", "z"
    ]

    for tag in optional_tags:
        if elem.find("pi:" + tag, namespaces= NS) is not None:
            txt = elem.findtext("pi:" + tag, namespaces= NS)
            # float conversion for coords
            if tag in ("lat", "lon", "x", "y", "z"):
                attribs[tag] = float(txt)
            else:
                attribs[tag] = txt

    # thresholds
    if (th := elem.find("pi:thresholds", namespaces=NS)) is not None:
        attribs["thresholds"] = _parse_thresholds(th)

    return PIHeader(**attribs)


# ----------------------------------------------------------------------
# Helper: parse <series>
# ----------------------------------------------------------------------
def _parse_series(elem: ET.Element) -> PISeries:
    header = elem.find("pi:header", NS)
    parsed_header = _parse_header(header)

    # properties
    props_container = elem.find("pi:properties", NS)
    props = None
    if props_container is not None:
        props = [_parse_property(p) for p in list(props_container)]

    # events
    events = [_parse_event(e) for e in elem.findall("pi:event", NS)]

    return PISeries(
        header=parsed_header,
        properties=props,
        event=events
    )


# ----------------------------------------------------------------------
# MAIN ENTRY POINT
# ----------------------------------------------------------------------

def fx_read(filepath: str) -> PITimeSeries:
    tree = ET.parse(filepath)
    root = tree.getroot()

    version = root.attrib.get("version")

    tz_elem = root.find("pi:timeZone", NS)
    if tz_elem is None or tz_elem.text is None:
        raise ValueError("Missing <timeZone> element")
    timeZone = float(tz_elem.text)

    series = [_parse_series(s) for s in root.findall("pi:series", NS)]

    return PITimeSeries(
        version=version,
        timeZone=timeZone,
        series=series
    )