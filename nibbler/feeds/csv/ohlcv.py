import numpy as np
from .csv import CSV
from .. import ohlcv


class OHLCV(CSV, ohlcv.OHLCV):

    def _set_data(self):

        self._data = np.stack(
            [
                self._dataframe["datetime"],
                self._dataframe["open"],
                self._dataframe["high"],
                self._dataframe["low"],
                self._dataframe["close"],
                self._dataframe["volume"]
            ], axis=0
        )
        del self._dataframe