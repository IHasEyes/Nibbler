from typing import Iterable 
import numpy as np


def greatestDivisor(target: int, iterator: Iterable[int]):
    """
        For a target specified find the largest
        divisor within from iterable 
    """

    _greatestDivisor = 1

    for item in iterator:
        if target%item == 0:
            if item > _greatestDivisor:
                _greatestDivisor = item
    
    return _greatestDivisor


def makeOdd(value: int):
    if value%2==0:
        return value + 1
    return value


def findMaxFromGradients(gradients):
    find = np.logical_and(
        gradients[:-1] > 0,
        gradients[1:] < 0
    )

    maxes = np.flatnonzero(find)

    try:
        len(maxes)
    except ValueError:
        return np.array([maxes, ])
    
    return maxes


def findMinFromGradients(gradients):
    find = np.logical_and(
        gradients[:-1] < 0,
        gradients[1:] > 0
    )

    mins = np.flatnonzero(find)

    try:
        len(mins)
    except ValueError:
        return np.array([mins, ])
    
    return mins