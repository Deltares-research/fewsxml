# fewsxml

A library to read and write XML files to interact with Delft-FEWS.

## Installation
```commandline
pip install fewsxml
```

## Overview

`fewsxml` provides two data structures:
* FXTimeseries
* FXData

To read and write data from/to XML files with the FEWS PI standard, one needs to be familiar with these two data structures.

### Reading Procedure
Reading data from an XML file consists of two steps: first, create an instance of `FXData`, and second, call the function `read_xml`. Here is an example:
```python
import fewsxml as fx

data = fx.FXData({
    "inputFilePath": "timeseries_export.xml"
})
data_in_xml = fx.read_xml(data)
```
The `FXData` structure contains many fields, but for reading data, only the `inputFilePath` field needs to be filled. As a result of a successful read operation, the `FXData` instance is populated with relevant information. Most importantly, `FXData` contains a list of `FXTimeseries`, called `timeseries`, where each element represents one timeseries. For example, a list of timeseries with the `parameterId` of `paramId1` can be retrieved by:
```python
tss = [timeserie for timeserie in data["timeseries"] if timeserie["parameterId"] == "paramId1"]
```

### Writing Procedure
The function `write_xml` is used for writing an XML file with the FEWS PI standard. Similar to the reading procedure, an instance of `FXData` must be created. However, the required fields in this case are `timeseries` and `outputFilePath`. The `outputFilePath` should indicate the location where the XML file will be created. The `timeseries` field is a list of `FXTimeseries` instances, where each instance represents a timeseries to be written into the XML file. The required fields in each `FXTimeseries` instance are:
* `locationId`: The location ID of the timeseries.
* `parameterId`: The parameter ID of the timeseries.
* `timesteps`: A list of `datetime` objects, where each element represents a timestep in the timeseries.
* `values`: A list of values for each timestep in the timeseries.
* `timeStepSize`: The constant interval between consecutive sample times in `timesteps`.
* `startDateTime`: The start date and time of the timeseries.
* `endDateTime`: The end date and time of the timeseries.
* `flags` (optional): A list of flags for each element of the timeseries.

Here is an example of how to write a timeseries:
```python
import os.path
import fewsxml as fx
from datetime import datetime, timedelta

def _create_datetime_list(sDateTime, hDuration, sInterval):
    total_duration_seconds = hDuration * 3600
    num_steps = total_duration_seconds // sInterval
    # Create the list of datetimes
    datetime_list = [sDateTime + timedelta(seconds=i * sInterval) for i in range(int(num_steps) + 1)]
    return datetime_list

sDateTime = datetime(2025, 4, 10, 14, 0, 0)  # Start datetime
hDuration = 2  # Duration in hours
sInterval = 600  # Interval in seconds (e.g., 600 seconds = 10 minutes)

datetime_list = _create_datetime_list(sDateTime, hDuration, sInterval)

timeseries1 = fx.FXTimeseries({
    "locationId": "testLoc1",
    "parameterId": "paramId1",
    "timesteps": datetime_list,
    "values": [0] * len(datetime_list),
    "timeStepSize": sInterval,
    "startDateTime": datetime_list[0],
    "endDateTime": datetime_list[-1]
})
timeseries2 = fx.FXTimeseries({
    "locationId": "testLoc2",
    "parameterId": "paramId2",
    "timesteps": datetime_list,
    "values": [1.1] * len(datetime_list),
    "timeStepSize": sInterval,
    "startDateTime": datetime_list[0],
    "endDateTime": datetime_list[-1]
})

data = fx.FXData({
    "timeseries": [timeseries1, timeseries2],
    "outputFilePath": os.path.join("timeseries_export.xml")
})
fx.write_xml(data)
```
