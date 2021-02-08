import datetime as _dt
import numpy as _np


secondstotimeframe = {
    1000*60        : "m",
    1000*60*60     : "h",
    1000*60*60*24  : "d",
    1000*60*60*24*7: "w"
}


timeframetoseconds = {
    "m": 1000*60,
    "h": 1000*60*60,
    "d": 1000*60*60*24,
    "w": 1000*60*60*24*7
}


def timestamp_to_datetime(datetime):

    if not isinstance(datetime[0], _dt.datetime):
        datetime = [
            _dt.datetime.fromtimestamp(int(date)/1000)
            for date in datetime
        ]

    return _np.array(datetime)
