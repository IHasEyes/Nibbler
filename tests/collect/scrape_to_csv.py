from nibbler import collect
import pathlib as pt
import unittest


class ScrapeToCSV(unittest.TestCase):

    cwd       = pt.Path(__file__).parent
    exchange  = "binance"
    pair_a    = "BTC"
    pair_b    = "USDT"
    collector = collect.binance.BTCUSDT

    def collect(self, timeframe):
        filename = "%s_%s_%s.csv"%(self.pair_a, self.pair_b, timeframe)
        outputFile = self.cwd/filename
        collector = self.collector(timeframe)
        collector.run(outputFile)
        self.assertTrue(outputFile)

    def test_1m(self):
        timeframe = "1m"
        self.collect(timeframe)

    def test_5m(self):
        timeframe = "5m"
        self.collect(timeframe)

    def test_15m(self):
        timeframe = "15m"
        self.collect(timeframe)

    def test_1h(self):
        timeframe = "1h"
        self.collect(timeframe)

    def test_4h(self):
        timeframe = "4h"
        self.collect(timeframe)

    def test_1d(self):
        timeframe = "1d"
        self.collect(timeframe)

    def test_1w(self):
        timeframe = "1w"
        self.collect(timeframe)

if __name__ == "__main__":
    unittest.main()
