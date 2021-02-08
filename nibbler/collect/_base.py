import pandas as pd
import numpy as np
import pathlib as pt
import ccxt
import abc
import time
from datetime import datetime
import logging


class Collector(abc.ABC):

    exchangeDict = {
        "enableRateLimit": True
    }
    limit = 1000
    maxRetries = 10
    symbol = None

    formatString = "%Y-%m-%dT%H:%M:%SZ" 

    _exchange = None
    _timeframeSeconds = None
    _timeframeMilliseconds = None
    _timeDelta = None

    headings = ["datetime", "open", "high", "low", "close", "volume"]

    def __repr__(self):
        return f"<{self._exchange}-{self.symbol}-{self.timeframe}>"

    def __init__(self, timeframe):
        self.timeframe = timeframe
        self.numRetries = 0
        self.scraping = False
        self.exchange
        self.timeFrameseconds
        self.timeframeMilliseconds
        self.timeDelta
    
    def __call__(
        self,
        outputFilename: pt.Path,
        startTime: str = '2013-07-01T00:00:00Z',
        log: bool = True
    ):
        self.outputFilename = pt.Path(outputFilename)
        try:
            dataframeOld = pd.read_csv(outputFilename)
            timestampLast = dataframeOld.datetime.values[-1]*10**(-3)
            timestampFormatted = \
                datetime.fromtimestamp(int(timestampLast)).strftime(self.formatString)
        except:
            if startTime.lower() != "now":
                timestampFormatted = startTime
            else:
                timestampFormatted = datetime.now().strftime(
                    self.formatString
                )
        
        self.startTime = timestampFormatted  
        self.scrapeToCSV()
        dataframeNew = pd.read_csv(outputFilename)

        newDatetime = int(dataframeNew.iloc[-1]["datetime"]*10**(-3))
        newDatetime = datetime.fromtimestamp(newDatetime).strftime(self.formatString)
        newtimestamp = \
            f"""
            datetime: {newDatetime}
            open    : {dataframeNew.iloc[-1]["open"]}
            high    : {dataframeNew.iloc[-1]["high"]}
            low     : {dataframeNew.iloc[-1]["low"]}
            close   : {dataframeNew.iloc[-1]["close"]}
            volume  : {dataframeNew.iloc[-1]["volume"]}
            """
        
        if log:
            logging.info("New Candle\n{newtimestamp}")

    def scrapeToCSV(self):
        if not self.outputFilename.exists():
            dataframe = pd.DataFrame(columns=self.headings)
            dataframe.to_csv(self.outputFilename, index=False, index_label=False)
        self.scrape()
        dataframe = self.constructDateframe()
        dataframe.to_csv(self.outputFilename, index=False, index_label=False)
 
    def scrape(self):
        self.earliestTimestampMilliseconds = self.exchange.milliseconds()
        self.scraping = True
        self.allOHLCV = []
        breakLoop = False
        while True:
            if isinstance(self.startTime, str):
                self.startTime = self.exchange.parse8601(self.startTime)
            self.exchange.load_markets()
            breakLoop = self.scrapeMethod()
            if breakLoop:
                break

    def scrapeMethod(self):
        fetchSince = self.earliestTimestampMilliseconds - self.timeDelta
        ohlcv = self.fetch()
        try:
            if ohlcv[0][0] >= self.earliestTimestampMilliseconds:
                return True
        except ValueError:
            return True
        self.earliestTimestampMilliseconds = ohlcv[0][0]
        self.allOHLCV.extend(ohlcv)
        logging.info(
            len(self.allOHLCV), "candles in total from",
            self.exchange.iso8601(self.allOHLCV[0][0]),
            "to", self.exchange.iso8601(self.allOHLCV[-1][0])
        )
        if fetchSince < int(self.startTime):
            return True
        return False

    def fetch(self):
        assert self.scraping, "command is run within the scrape method"
        self.numRetries = 0
        try:
            self.numRetries += 1
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol, self.timeframe, self.startTime, self.limit
            )
            return ohlcv
        except ValueError:
            if self.numRetries > self.maxRetries:
                raise Exception(
                    "Failed to fetch", self.timeframe, self.symbol,
                    "OHLCV in", self.maxRetries, "attempts"
                )
    
    def constructDateframe(self):
        dataframe = pd.DataFrame(columns=self.headings)
        dataframe = dataframe.assign(
            **dict(zip(dataframe.keys(), np.array(self.allOHLCV).T))
        )
        dataframe = dataframe.sort_values(by=self.headings[0], ascending=True)
        if self.outputFilename is not None:
            originalCSV = pd.read_csv(self.outputFilename)
            dataframe = originalCSV.append(dataframe).drop_duplicates(
                subset=self.headings[0], keep="first", inplace=False
            )
            dataframe = dataframe[self.headings]
        return dataframe

    def loop(self, outputFilename: pt.Path, startTime: str = '2013-07-01T00:00:00Z'):
        while True:
            self(outputFilename, startTime=startTime)
            time.sleep(self.timeFrameseconds)

    @property
    def exchange(self):
        if isinstance(self._exchange, str):
            self._exchange = getattr(ccxt, self._exchange)(self.exchangeDict)
        assert isinstance(self._exchange, ccxt.Exchange)
        return self._exchange

    @property
    def timeFrameseconds(self):
        if self._timeframeSeconds is None:
            self._timeframeSeconds = \
                self.exchange.parse_timeframe(self.timeframe) 
        return self._timeframeSeconds

    @property
    def timeframeMilliseconds(self):
        if self._timeframeMilliseconds is None:
            self._timeframeMilliseconds = \
                self.exchange.parse_timeframe(self.timeframe) 
        return self._timeframeSeconds

    @property
    def timeDelta(self):
        if self._timeDelta is None:
            self._timeDelta = self.limit * self.timeframeMilliseconds
        return self._timeDelta