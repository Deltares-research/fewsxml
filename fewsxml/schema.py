from typing import TypedDict, List, Dict
from datetime import datetime

class FXTimeseries(TypedDict):
    locationId: str
    parameterId: str
    qualifierId: str
    timesteps: List[datetime]
    values: List[float]
    flags: List[float]
    timestepsPattern: str
    type: str
    timeStepSize: int
    startDateTime: datetime
    endDateTime: datetime
    missVal: str
    stationName: str
    units: str
    creationDateTime: datetime

class FXData(TypedDict):
    """
    A dictionary representing a document to be read/written by the library.

    Fields:

    - timeseries (List[FXTimeseries]): A list of FXTimeseries to be written to the driver XML (only needed for write operation)
    - inputFilePath (str): File path of the input XML file (only needed for read operation)
    - outputFilePath (str): File path of the driver XML file (only needed for write operation)
    """
    pi: str
    xsi: str
    version: str
    timeZone: str
    schemaLocation: str
    timestepsPatterns: Dict[str, List[datetime]]
    timeseries: List[FXTimeseries]
    outputFilePath: str
    inputFilePath: str