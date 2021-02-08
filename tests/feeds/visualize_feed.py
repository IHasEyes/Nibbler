import unittest
import pathlib as pt
import nibbler as nb
import bokeh.plotting as bkp
from bokeh.plotting import output_file

resource_directory = pt.Path(r"D:\Github\Nibbler\resources\data")
assert resource_directory.exists()

data_file = resource_directory/"BTC_USDT_1h.csv"
assert data_file.exists()

if __name__ == "__main__":
    feed = nb.feeds.csv.OHLCV(data_file)
    feed.initialize()

    for i in range(1000):
        feed.step()

    p = feed.plot(n_bars=100)
    output_file("./run.html")
    bkp.show(p)
    pass
