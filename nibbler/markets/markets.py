import abc
from typing import Iterable
from collections import defaultdict, OrderedDict
import pathlib as pt
from bokeh.layouts import column
from collections import OrderedDict, defaultdict
from uuid import uuid1
from typing import List

from ..utils import timeframeconversion
from ..feeds import Feed, csv, OHLCV


class Market(abc.ABC):

    kind      = None
    maker_fee = None
    taker_fee = None

    def __init__(
            self, pair1:str, pair2:str,
            slippage=None, maker_fee=None, taker_fee=None
        ):

        if maker_fee is not None:
            self.maker_fee = maker_fee

        if taker_fee is not None:
            self.taker_fee = taker_fee

        self.pair1               = pair1
        self.pair2               = pair2
        self.name                = "%s%s"%(self.pair1, self.pair2)
        self.exchange            = None
        self.smallest_time_delta = 0
        self.master_key          = None
        self.feeds               = {}
        self.feeds_ohlcv         = {}
        self.orders              = defaultdict(OrderedDict)
        self.stops               = defaultdict(OrderedDict)
        self._children           = []
        self._master             = None

        if slippage is None:
            # the slippage takes in qunatity and the current amarket
            # and returns the amount which is filled.
            self._slippage = lambda quantity, market: quantity

    def set_slippage_function(self, slippage_function):
        self._slippage = slippage_function

    def fill_amount(self, quantity):
        return self._slippage(quantity, self)

    def add_ohlcv_feed_from_csv(self, *paths: Iterable[pt.Path]):
        for path in paths:
            self.add_feeds(csv.OHLCV(path))

    def set_master(self, master_market: "Market"):
        assert isinstance(master_market, Market), "input must be a Market object"
        self.master_feed.set_master(master_market.master_feed)
        master_market.set_child(self)

    def del_master(self):
        self.master_feed.del_master()

    def set_child(self, child: "Market"):
        assert isinstance(child, Market)
        if child not in self._children:
            self._children.append(child)

    def del_child(self, child: "Market"):
        if child in self._children:
            child.del_master()

    def del_children(self):
        for child in self._children:
            self.del_child(child)

    def set_exchange(self, exchange):
        self.exchange = exchange

    def add_feeds(self, *feeds: Feed):
        for feed in feeds:
            feed_key = f"{feed.__class__.__name__}_{feed.timeframe}"

            if len(self.feeds) == 0:
                self.smallest_time_delta = feed.smallest_time_delta
                self.master_key          = feed_key
            elif feed.smallest_time_delta <=self.master_feed.smallest_time_delta:
                self.smallest_time_delta = feed.smallest_time_delta
                self.master_key          = feed_key
            self.feeds[feed_key] = feed

            if feed.__class__.__name__ == "OHLCV":
                self.feeds_ohlcv[feed.timeframe] = feed

    def add_stops(self, *stops: "Stop"):
        for stop in stops:
            stop_dictionary = self.stops[stop.trader]
            stop_id         = len(stop_dictionary)
            while stop_id in stop_dictionary.keys():
                stop_id += 1
            stop_dictionary[stop_id] = stop
            stop.id = stop_id

    def initialize(self):
        return iter(self)

    def step(self):
        return next(self)

    def __iter__(self):
        for key, feed in self.feeds.items():
            if key != self.master_key:
                feed.set_master(self.master_feed)
            self.master_feed.initialize()

        # get the master ohlcv_key
        ohlc_feeds = list(self.feeds_ohlcv.values())
        ohlc_feeds.sort(key=lambda  x: x.smallest_time_delta)
        self.master_ohlcv_key = ohlc_feeds[0].timeframe

        return self

    def __next__(self):
        self.master_feed.step()
        [child.step() for child in self._children]
        # process each of the orders
        for order_dict in self.orders.values():
            order_dict_keys = list(order_dict.keys())
            for key in order_dict_keys:
                order_dict[key].process()
        # process each of the stops
        for stop_dict in self.stops.values():
            stop_dict_keys = list(stop_dict.keys())
            for key in stop_dict_keys:
                stop_dict[key].process()
        return self

    def __getitem__(self, key):
        if key in self.feeds.keys():
            return self.feeds[key]
        elif key in self.feeds_ohlcv.keys():
            return self.feeds_ohlcv[key]

    def __len__(self):
        return len(self.master_feed)

    @property
    def master_feed(self) -> Feed:
        return self.feeds[self.master_key]

    @property
    def master_feed_ohlcv(self) -> OHLCV:
        return self.feeds_ohlcv[self.master_ohlcv_key]

    @property
    def start_datetime(self):
        return self.master_feed.start_datetime

    @property
    def all_feed_names(self):
        return [name for name in self.feeds.keys()]

    @property
    def all_feed_ohlcv_names(self):
        return [name for name in self.feeds_ohlcv.keys()]

    @property
    def current_datetime(self):
        return self.master_feed.current_datetime

    @property
    def current_open(self):
        return self.master_feed_ohlcv.current_open

    @property
    def current_high(self):
        return self.master_feed_ohlcv.current_high

    @property
    def current_low(self):
        return self.master_feed_ohlcv.current_low

    @property
    def current_close(self):
        return self.master_feed_ohlcv.current_close

    @property
    def current_volume(self):
        return self.master_feed_ohlcv.current_volume

    def __repr__(self):
        return f"<{self.name} {self.kind}Market feeds={self.all_feed_names}>"

    def plot(self, fig=None, **kwargs):

        if any([fig is None, not isinstance(fig, Iterable)]):
            for feed in self.feeds.values():
                feed.plot(fig=fig, **kwargs)
            return fig

        for feed, f in zip(self.feeds_ohlcv.values(), fig):
            output = feed.plot(fig=f, **kwargs)
        return output

    def plot_order(self, fig=None, **kwargs):
        for order in self.orders.values():
            output = order.plot(fig=fig, **kwargs)
        return output

    def plot_stops(self, fig=None, **kwargs):
        for stop_dict in self.stops.values():
            for stop in stop_dict.values():
                output = stop.plot(fig=fig, **kwargs)
        return output

    def plot_multi_timeframe_ohlcv(self, time_frames="all", **kwargs):
        figures = []
        plotted_first_figure = False
        feeds = list(self.feeds_ohlcv.values())
        feeds.sort(key=lambda x: x.smallest_time_delta)
        for _, feed in enumerate(feeds):
            do_plot = False

            if time_frames == "all":
                do_plot = True
            else:
                if isinstance(time_frames, str):
                    if time_frames in feed.timeframe:
                        return feed.plot()
                elif any(
                    [(time_frame in feed.timeframe) for time_frame in time_frames]):
                    do_plot = True
            if do_plot:
                if not plotted_first_figure:
                    fig       = feed.plot()
                    first_fig = fig
                    plotted_first_figure = True
                else:
                    fig = feed.plot(x_range=first_fig.children[0].x_range)
                figures.append(fig)

        assert len(figures) > 0, "specified time frames do not exist"
        return column(figures)
# ---------------------------------------------------------------------------- #
class Spot(Market):
    kind      = "spot"
    maker_fee = 0.001
    taker_fee = 0.001
# ---------------------------------------------------------------------------- #
class Futures(Market):
    kin       = "futures"
    maker_fee = 0.0002
    taker_fee = 0.0004

    def __init__(
        self, *args, funding_rate=None, max_leverage=75, **kwargs):
        '''
            futures markets funding rates have yet to be implemented
        '''
        assert args[0] != "USDT", "Cannot trade USDT with USDT"
        assert args[1] == "USDT", "Futures only support USDT pair"
        super(Futures, self).__init__(*args, **kwargs)
        self.max_leverage = max_leverage
        self.positions    = OrderedDict()

    def __next__(self):
        super().__next__()
        for key in list(self.positions.keys()):
            self.positions[key].process()
