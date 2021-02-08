import numpy as np
from nibbler import collect
import pathlib as pt
import multiprocessing as mp


def processMarket(market: str, timeframes:str, mainFolder: pt.Path):
    coin = [name for name in market.split("USDT") if all(
        ["USDT" not in name, len(name)>0]
    )][-1]

    mainFolder = mainFolder/coin

    if not mainFolder.exists():
        mainFolder.mkdir()
    
    for timeframe in timeframes:
        filename = "%s_%s"%(market, timeframe)
        collector = getattr(collect.binance, market)(timeframe)
        collector(mainFolder/filename)


def processMarketList(markets):
    for market in markets:
        if not market.startswith("_"):
            if "USDT" in market:
                processMarket(market, timeframes, usdtFolder)


def chunk(iterable, nchunks):
    iterable = list(iterable)
    itemPersplit = np.ceil(len(iterable)/nchunks)

    outputList = [[]]

    counter = 0
    for item in iterable:

        if counter < itemPersplit:
            outputList[-1].append(item)
        else:
            outputList.append([])
            counter = 0

        counter += 1

    return outputList


if __name__ == "__main__":
    
    nprocesses = 8

    timeframes = [
        "1m", "1w", "3d", "1d", "12h", "8h", "6h", "4h", "2h", "1h",
        "30m", "15m", "5m", "3m", "1m"
    ] 

    markets = list(collect.binance.__dict__.keys())
    markets = [ market for market in markets if "USDT" in market ]

    cwd = pt.Path(__file__).parent
    usdtFolder = cwd/"USDT"

    if not usdtFolder.exists():
        usdtFolder.mkdir()

    chunked = chunk(markets, nprocesses)

    pass
