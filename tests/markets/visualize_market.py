import unittest
import pathlib as pt
import nibbler as nb
import bokeh.plotting as bkp
from bokeh.plotting import output_file
from bokeh.io import show, export_png

resource_directory = pt.Path(r"D:\Github\Nibbler\resources\data")
assert resource_directory.exists()

btc_15m = resource_directory/"BTC_USDT_15m.csv"
btc_1h = resource_directory/"BTC_USDT_1h.csv"
btc_4h = resource_directory/"BTC_USDT_4h.csv"

assert all([btc_1h.exists(), btc_4h.exists()])

if __name__ == "__main__":
    market = nb.markets.Spot("BTC", "USDT")
    market.add_ohlcv_feed_from_csv(btc_1h, btc_15m, btc_4h)

    for i, _ in zip(range(1000), market):
        pass

    output_file("./run.html")
    # plot all figures
    fig = market.plot_multi_timeframe_ohlcv()
    show(fig)
    # plot subset of figures
    fig = market.plot_multi_timeframe_ohlcv(time_frames=["1h", "4h"])
    show(fig)
    # export the image as a png
    export_png(fig, filename="test.png")

    len_feeds = [len(feed.open) for feed in market.feeds_ohlcv.values()]
    print(len_feeds)
    pass

