from .SavgolFilter import SavitzkyGolayFilter
import numpy as np

class PolyfitSavgolFilter:

    __slots__ = ["filter", "pad", "polyorder"]

    def __init__(self, window_size, deriv=0, polyorder=2):
        assert window_size % 2 != 0
        self.pad = (window_size - 1)//2
        self.polyorder = polyorder
        self.filter = SavitzkyGolayFilter(self.pad, self.pad, deriv, polyorder)

    def __call__(self, input):

        filtered = self.filter(input)

        left = np.ones(self.pad) * input[0]

        x = np.arange(self.pad)
        fit = filtered[-self.pad:]

        p = np.polyfit(x, fit, self.polyorder)

        p = np.poly1d(p)

        right = p(np.arange(self.pad, 2*self.pad))

        ynew = np.concatenate([left, filtered, right])

        return ynew

class CausalSavgolFilter:

    __slots__ = ["filter", "pad", "polyorder"]

    def __init__(self, window_size, deriv=0, polyorder=2):
        assert window_size % 2 != 0
        self.pad = window_size - 1
        self.polyorder = polyorder
        self.filter = SavitzkyGolayFilter(self.pad, 0, deriv, polyorder)

    def __call__(self, input):

        left_pad = np.ones(self.pad) * input[0]

        ynew = np.concatenate([left_pad, input])

        filtered = self.filter(ynew)

        return filtered

class ConstantPaddingSavgolFilter:

    __slots__ = ["filter", "pad", "polyorder"]

    def __init__(self, window_size, deriv=0, polyorder=3):
        assert window_size % 2 != 0
        self.pad = (window_size - 1)//2
        self.polyorder = polyorder
        self.filter = SavitzkyGolayFilter(self.pad, self.pad, deriv, polyorder)

    def __call__(self, input):

        left = np.ones(self.pad) * input[0]

        right = np.ones(self.pad) * input[-1]

        ynew = np.concatenate([left, input, right])

        return self.filter(ynew)