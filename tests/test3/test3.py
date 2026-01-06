import os.path

import fewsxml as fx
from datetime import datetime, timedelta


parsed_xml = fx.read("timeseries_import_with_qualifier.xml")
fx.write(parsed_xml, "timeseries_export_with_qualifier.xml")

# Making sure the qualifier IDs are read correctly
assert parsed_xml.series[0].header.qualifierId == ["Minimum"]
assert parsed_xml.series[1].header.qualifierId == ["Maximum"]

# Making sure the qualifier IDs are written correctly
parsed_xml2 = fx.read("timeseries_export_with_qualifier.xml")
assert parsed_xml2.series[0].header.qualifierId == ["Minimum"]
assert parsed_xml2.series[1].header.qualifierId == ["Maximum"]
