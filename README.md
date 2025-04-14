# fewsxml

A library to read and write XML files to interact with Delft-FEWS.

`fewsxml` provides two data structure as follows:
* FXTimeseries
* FXData

To read and write data from/to XML files with the FEWS PI standard, 
one needs to get familiar with the above two data structures.

## Reading procedure
Reading data from an XML file consists of two steps: first, an instance 
of FXData must be created and, second, the function `read_xml` should be 
called. Here is an example:
```python
import fewsxml as fx

data: fx.FXData = {
    "inputFilePath": "timeseries_export.xml"
}
data_in_xml = fx.read_xml(data)
```
The data structure of FXData contains of many fields, but for reading data, 
only the field of `inputFilePath` is necessary to be filled. As a result of 
a successful read operation, the instance of FXData is populated with relevant 
information. Most importantly, `FXData` contains a list of `FXTimeseries`, 
called `timeseries`, in which each element belongs to one timeseries. As an 
example, a list of timeseries that the `parameterId` of `paramId1` can be retrieved 
by:
```python
tss = [timeserie for timeserie in data['timeseries'] if timeserie["parameterId"] == "paramId1"]
```

## Writing procedure
The function `write_xml` is used for writing an XML file with the FEWS PI 
standard. Similar to the reading procedure, an instance of FXData must be 
created. However, the required fields in this case are `timeseries` and 
`outputFilePath`. The value of `outputFilePath` should indicate the location 
of creation of the XML file. The field of `timeseries` is a list of `FXTimeseries` 
instances, where each instance is a timeseries in which we are interested to 
write its data into the XML file. The required fields in each instance of 
`FXTimeseries` are:
* `locationId`: The location ID of the timeseries.
* `parameterId`: The parameter ID of the timeseries.
* `timesteps`: A list of `datetime`s, in which each element of this timeseries belongs to.
* `values`: A list of values for each element of the timeseries.
* `timeStepSize`: The constant interval between consequtive sample times in `timesteps`
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


timeseries1: fx.FXTimeseries = {
    "locationId": "testLoc1",
    "parameterId": "paramId1",
    "timesteps": datetime_list,
    "values": [0] * len(datetime_list),
    "timeStepSize": sInterval,
    "startDateTime": datetime_list[0],
    "endDateTime": datetime_list[-1]
}
timeseries2: fx.FXTimeseries = {
    "locationId": "testLoc2",
    "parameterId": "paramId2",
    "timesteps": datetime_list,
    "values": [1.1] * len(datetime_list),
    "timeStepSize": sInterval,
    "startDateTime": datetime_list[0],
    "endDateTime": datetime_list[-1]
}

data: fx.FXData = {
    "timeseries": [timeseries1, timeseries2],
    "outputFilePath": os.path.join("timeseries_export.xml")
}
fx.write_xml(data)
```