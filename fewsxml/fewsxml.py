from .schema import FXData, FXTimeseries
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
from datetime import datetime
import numpy as np
import importlib.resources as pkg_resources
import fewsxml


def read_xml(fxdata: FXData):
    # Loading configs
    configs = {}
    with pkg_resources.files(fewsxml).joinpath("config.xml").open("rb") as f:
        tree = ET.parse(f)
    root = tree.getroot()
    configs["reader_req"] = [elem.text for elem in root.findall("reader_req")]
    # loading the input file
    tree = ET.parse(fxdata["inputFilePath"])
    root = tree.getroot()
    if "ns" not in fxdata.keys():
        fxdata["ns"] = 'http://www.wldelft.nl/fews/PI'
    namespace = {'ns': fxdata["ns"]}
    # Extract general information
    fxdata["timeZone"] = root.find('ns:timeZone', namespace).text
    # Iterate through each series
    fxdata["timeseries"] = []
    for series in root.findall('ns:series', namespace):
        fxtimeseries: FXTimeseries = {}
        header = series.find('ns:header', namespace)
        # Get all properties under header
        properties = {elem.tag.split('}', 1)[-1]: elem.attrib if elem.attrib else elem.text for elem in header}
        if not all([req_property in properties.keys() for req_property in configs["reader_req"]]):
            continue    # Skipping the timeseries that do not contain required properties
        for property in properties:
            if property == "timeStep":
                time_step_unit = header.find('ns:timeStep', namespace).attrib['unit']
                if time_step_unit == "second":
                    fxtimeseries["timeStepSize"] = header.find('ns:timeStep', namespace).attrib['multiplier']
            elif property == "startDate":
                start_date = header.find('ns:startDate', namespace).attrib['date']
                start_time = header.find('ns:startDate', namespace).attrib['time']
                fxtimeseries["startDateTime"] = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
            elif property == "endDate":
                end_date = header.find('ns:endDate', namespace).attrib['date']
                end_time = header.find('ns:endDate', namespace).attrib['time']
                fxtimeseries["endDateTime"] = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")
            else:
                fxtimeseries[property] = header.find('ns:' + property, namespace).text
        # Extract event information
        fxtimeseries["timesteps"] = []
        fxtimeseries["values"] = []
        fxtimeseries["flags"] = []
        for event in series.findall('ns:event', namespace):
            event_date = event.attrib['date']
            event_time = event.attrib['time']
            fxtimeseries["timesteps"].append(datetime.strptime(f"{event_date} {event_time}", "%Y-%m-%d %H:%M:%S"))
            try:
                value = float(event.attrib['value'])
            except ValueError:
                value = fxtimeseries["missVal"]
            fxtimeseries["values"].append(value)
            if "flag" in event.attrib.keys():
                fxtimeseries["flags"].append(event.attrib['flag'])
        if not fxtimeseries["flags"]:
            del fxtimeseries["flags"]
        fxdata["timeseries"].append(fxtimeseries)
    return fxdata

def write_xml(fxdata: FXData):
    # Loading configs
    configs = {}
    with pkg_resources.files(fewsxml).joinpath("config.xml").open("rb") as f:
        tree = ET.parse(f)
    root = tree.getroot()
    configs["writer_req"] = [elem.text for elem in root.findall("writer_req")]
    # Data fixing of overal XML information
    if "pi" not in fxdata.keys():
        fxdata["pi"] = "http://www.wldelft.nl/fews/PI"
    if "xsi" not in fxdata.keys():
        fxdata["xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
    if "version" not in fxdata.keys():
        fxdata["version"] = "1.2"
    if "schemaLocation" not in fxdata.keys():
        fxdata["schemaLocation"] = "http://www.wldelft.nl/fews/PI https://fewsdocs.deltares.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd"
    if "timeZone" not in fxdata.keys():
        fxdata['timeZone'] = "1.0"
    # Data fixing and validity check of individual timeseries
    for timeserie in fxdata["timeseries"]:
        if "missVal" not in timeserie.keys():
            timeserie["missVal"] = "-999"
        if "type" not in timeserie.keys():
            timeserie["type"] = "instantaneous"
        if "units" not in timeserie.keys():
            timeserie["units"] = "unit_unknown"
        if "creationDateTime" not in timeserie.keys():
            timeserie["creationDateTime"] = datetime.now()
        if "stationName" not in timeserie.keys():
            timeserie["stationName"] = timeserie["locationId"]
        l_necessary_keys = configs["writer_req"]
        if not all(item in timeserie.keys() for item in l_necessary_keys):
            raise Exception("The provided timeseries data is incomplete. Note that each individual timeseries should have appropriate values for the following list of keys:\n{}".format(l_necessary_keys))

    # prelude information
    ET.register_namespace("pi", fxdata["pi"])
    ET.register_namespace("xsi", fxdata["xsi"])
    tag_prefix = "pi:"
    root = ET.Element(tag_prefix + "TimeSeries", attrib={
        "xmlns:pi": fxdata["pi"],
        "xmlns:xsi": fxdata["xsi"],
        "xsi:schemaLocation": fxdata["schemaLocation"],
        "version": fxdata["version"]
    })
    ET.SubElement(root, tag_prefix + "timeZone").text = fxdata['timeZone']
    # adding timeseries
    for timeserie in fxdata["timeseries"]:
        series = ET.SubElement(root, tag_prefix + "series")
        header = ET.SubElement(series, tag_prefix + "header")
        ET.SubElement(header, tag_prefix + "type").text = timeserie["type"]
        ET.SubElement(header, tag_prefix + "locationId").text = timeserie["locationId"]
        ET.SubElement(header, tag_prefix + "parameterId").text = timeserie["parameterId"]
        if "qualifierId" in timeserie.keys():
            ET.SubElement(header, tag_prefix + "qualifierId").text = timeserie["qualifierId"]
        ET.SubElement(header, tag_prefix + "timeStep", unit="second", multiplier=str(timeserie["timeStepSize"]))
        ET.SubElement(header, tag_prefix + "startDate", date=timeserie["startDateTime"].strftime("%Y-%m-%d"), time=timeserie["startDateTime"].strftime("%H:%M:%S"))
        ET.SubElement(header, tag_prefix + "endDate", date=timeserie["endDateTime"].strftime("%Y-%m-%d"), time=timeserie["endDateTime"].strftime("%H:%M:%S"))
        ET.SubElement(header, tag_prefix + "missVal").text = timeserie["missVal"]
        ET.SubElement(header, tag_prefix + "stationName").text = timeserie["stationName"]
        ET.SubElement(header, tag_prefix + "units").text = timeserie["units"]
        ET.SubElement(header, tag_prefix + "creationDate").text = timeserie["creationDateTime"].strftime("%Y-%m-%d")
        ET.SubElement(header, tag_prefix + "creationTime").text = timeserie["creationDateTime"].strftime("%H:%M:%S")
        l_manual_handlings = ["type", "locationId", "parameterId", "qualifierId", "timeStepSize", "startDateTime", "endDateTime", "missVal", "stationName", "units", "creationDateTime", "flags", "values", "timesteps"]
        for key in timeserie.keys():
            if key not in l_manual_handlings:
                ET.SubElement(header, key).text = timeserie[key]
        if "flags" in timeserie.keys():
            for t, v, flag in zip(timeserie["timesteps"], timeserie["values"], timeserie["flags"]):
                ET.SubElement(series, tag_prefix + "event", date=t.strftime("%Y-%m-%d"), time=t.strftime("%H:%M:%S"), value=str(v if not np.isnan(v) else timeserie["missVal"]), flag=flag)
        else:
            for t, v in zip(timeserie["timesteps"], timeserie["values"]):
                ET.SubElement(series, tag_prefix + "event", date=t.strftime("%Y-%m-%d"), time=t.strftime("%H:%M:%S"), value=str(v if not np.isnan(v) else timeserie["missVal"]))

    def prettify_xml(element):
        rough_string = ET.tostring(element, encoding="utf-8")
        parsed = minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="    ", encoding="UTF-8")
    if "outputFilePath" not in fxdata.keys():
        raise Exception("outputFilePath is not stored in the given FXData argument.")
    else:
        xml_export_path = os.path.join(fxdata["outputFilePath"])
    with open(xml_export_path, "wb") as f:
        f.write(prettify_xml(root))
