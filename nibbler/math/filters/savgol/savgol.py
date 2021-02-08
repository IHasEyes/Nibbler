from savgol import SavitzkyGolayFilter, CausalSavgolFilter
import numpy as np
from scipy import signal, interpolate
from time import time

input_array = np.arange(0,1000)

# filt = SavitzkyGolayFilter(9, 1, 0, 3)
causal_filt = CausalSavgolFilter(11)

N = 10000

# inbuilt

start = time()
for i in range(N):
    signal.savgol_filter(input_array, 11, 3)
end = time()

print(end - start)

# cpp

start = time()

for i in range(N):

    # left = np.ones(9)*input_array[0]
    # right = np.ones(1)*input_array[-1]

    # ynew = np.concatenate([left, input_array, right])

    # filt(ynew)
    causal_filt(input_array)

end = time()

print(end - start)
