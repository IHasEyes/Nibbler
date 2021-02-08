import numpy as np
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, show
import datetime as dt
from .feed import Feed
from .. import utils
from .. math import greatestDivisor
from ..utils.timeframeconversion import (secondstotimeframe, timeframetoseconds)


_allnames = ["open", "high", "low", "close"]


class Dummy:
    def __init__(self):
        self.x_range = None


class OHLCV(Feed):

    candlestick_chart_width  = 1500
    candlestick_chart_height = 500

    volume_chart_width  = 1500
    volume_chart_height = 250

    candlestick_chart_alpha = 1
    volume_chart_alpha      = 0.5

    time_series_chart   = None
    volume_series_chart = None

    def __init__(self, **kwargs):
        self._tempdata       = None
        self._segments       = None
        self._increment_bars = None
        self._decrement_bars = None
        super(OHLCV, self).__init__(**kwargs)
        self._set_timeframe()

    def _set_timeframe(self):
        (time_gradient, counts)  = np.unique(
            np.gradient(self._data[0, 2:-2]), return_counts=True)

        if not self.is_tick:
            self.smallest_time_delta = int(time_gradient[np.argmax(counts)])
            divisor                  = greatestDivisor(
                self.smallest_time_delta, secondstotimeframe.keys())

            multiplier     = self.smallest_time_delta/divisor
            self.timeframe = "%d%s"%(multiplier, secondstotimeframe[divisor])
        else:
            self.nticks              = self.is_tick
            self.timeframe           = "%d%s"%(self.nticks, "t")
            self.smallest_time_delta = time_gradient.min()

    def _set_data(self):
        self._data = self._tempdata

    def _object_data(self):
        outputString = "OHLCV: %0.3f/%0.3f/%0.3f/%0.3f/%0.3f"
        return outputString%(
            self.current_open, self.current_high,
            self.current_low, self.current_close,
            self.current_volume
        )

    @property
    def open(self):
        return self._live[1]
    @property
    def high(self):
        return self._live[2]
    @property
    def low(self):
        return self._live[3]
    @property
    def close(self):
        return self._live[4]
    @property
    def volume(self):
        return self._live[5]

    @property
    def current_open(self):
        return self.open[-1]
    @property
    def current_high(self):
        return self.high[-1]
    @property
    def current_low(self):
        return self.low[-1]
    @property
    def current_close(self):
        return self.close[-1]
    @property
    def current_volume(self):
        return self.volume[-1]

    def get_ohlcv(self, region=None):
        if region is None:
            return self._live
        else:
            return self._live[:, region]

    def plot_candlesticks(
        self,
        fig             = None,
        title           = None,
        x_range         = None,
        orientation     = np.pi/5,
        grid_line_alpha = 0.3,
        segment_color   = "black",
        increment_color = "green",
        decrement_color = "red",
        bar_width       = 0.6,
        n_bars          = "max",
        tools           = "pan,wheel_zoom,xwheel_zoom,ywheel_zoom,box_zoom,reset,save",
        alpha           = 1
    ):

        if fig is None:

            fig = figure(
                x_axis_type = "datetime",
                tools       = tools,
                plot_width  = self.candlestick_chart_width,
                plot_height = self.candlestick_chart_height,
                title       = title,
                x_range     = x_range
            )
            fig.xaxis.major_label_orientation = orientation
            fig.grid.grid_line_alpha          = grid_line_alpha

        datetime       = utils.timeframeconversion.timestamp_to_datetime(self.datetime)
        datetime_width = np.gradient(self.datetime)*bar_width

        if n_bars == "max":
            _, d_open, d_high, d_low, d_close, _ = self.get_ohlcv()
        else:
            n_bars         = np.clip(n_bars, 2, len(self.open))
            _, d_open, d_high, d_low, d_close, _ = \
                self.get_ohlcv(region=np.s_[-n_bars:])
            datetime       = datetime[-n_bars:]
            datetime_width = datetime_width[-n_bars:]

        incr = d_close > d_open
        decr = d_close < d_open

        self._segments       = fig.segment(
            datetime, d_high, datetime, d_low, color=segment_color)

        self._increment_bars = fig.vbar(
            datetime[incr], datetime_width[incr], d_open[incr], d_close[incr],
            fill_color = increment_color,
            line_color = "black", alpha=self.candlestick_chart_alpha
        )
        self._decrement_bars = fig.vbar(
            datetime[decr], datetime_width[decr], d_open[decr], d_close[decr],
            fill_color = decrement_color, alpha=self.candlestick_chart_alpha,
            line_color = "black"
        )
        return fig

    def plot_volume(
        self,
        fig             = None,
        x_range         = None,
        title           = None,
        orientation     = np.pi/5,
        grid_line_alpha = 0.3,
        segment_color   = "black",
        increment_color = "green",
        decrement_color = "red",
        bar_width       = 0.6,
        n_bars          = "max",
        tools           = "pan,wheel_zoom,xwheel_zoom,ywheel_zoom,box_zoom,reset,save",
        alpha           = 0.5
    ):
        if fig is None:

            fig = figure(
                x_axis_type = "datetime",
                tools       = tools,
                plot_width  = self.volume_chart_width,
                plot_height = self.volume_chart_height,
                title       = title,
                x_range     = x_range,
            )
            fig.xaxis.major_label_orientation = orientation
            fig.grid.grid_line_alpha          = grid_line_alpha

        datetime       = utils.timeframeconversion.timestamp_to_datetime(self.datetime)
        datetime_width = np.gradient(self.datetime)*bar_width

        if n_bars == "max":
            _, d_open, _, _, d_close, d_volume = self.get_ohlcv()
        else:
            n_bars         = np.clip(n_bars, 2, len(self.open))
            _, d_open, _, _, d_close, d_volume = self.get_ohlcv(region=np.s_[-n_bars:])
            datetime       = datetime[-n_bars:]
            datetime_width = datetime_width[-n_bars:]

        incr = d_close > d_open
        decr = d_close < d_open

        self._increment_bars = fig.vbar(
            datetime[incr], datetime_width[incr], 0, d_volume[incr],
            fill_color = increment_color,
            alpha      = self.volume_chart_alpha,
            line_color = "black"
        )

        self._decrement_bars = fig.vbar(
            datetime[decr], datetime_width[decr], 0, d_volume[decr],
            fill_color = decrement_color,
            alpha      = self.volume_chart_alpha,
            line_color = "black"
        )

        return fig

    def __repr__(self):
        if self._counter is None:
            starttime  = dt.datetime.fromtimestamp(self._data[0][0]/1000)
            latesttime = dt.datetime.fromtimestamp(self._data[0][-1]/1000)
            return "<%s timeframe: %s period: %s to %s idle>"%(
                self.__class__.__name__, self.timeframe, starttime, latesttime
            )

        starttime   = dt.datetime.fromtimestamp(self._live[0][0]/1000)
        latesttime  = dt.datetime.fromtimestamp(self._live[0][-1]/1000)
        outpustring = "<%sFeed %s period:%s to %s "%(
            self.__class__.__name__, self._market.name, starttime, latesttime)
        outpustring += self._object_data()
        outpustring += ">"
        return outpustring

    def __iter__(self):
        self.time_series_chart   = None
        self.volume_series_chart = None
        return super().__iter__()


    def plot(self, *args, **kwargs):
        candlestick_chart               = self.plot_candlesticks(*args, **kwargs)
        candlestick_chart.xaxis.visible = False
        kwargs.pop("x_range", None)
        volume_chart                    = self.plot_volume(
            *args, x_range=candlestick_chart.x_range, **kwargs)
        return column(candlestick_chart, volume_chart)