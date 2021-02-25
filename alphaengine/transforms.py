import numpy as np


def rolling_window(a, window_size):
    shape = (a.shape[0] - window_size + 1, window_size) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    x = np.ones((window_size - 1, window_size)) * np.nan
    return np.vstack((x, np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)))


def aggregate(func, feature, window_size=1):
    return func(rolling_window(feature, window_size=window_size), axis=1)


def sum(feature, window_size=1):
    return aggregate(np.sum, feature, window_size)


def median(feature, window_size=1):
    return aggregate(np.median, feature, window_size)


def average(feature, window_size=1):
    return aggregate(np.average, feature, window_size)


def mean(feature, window_size=1):
    return aggregate(np.mean, feature, window_size)


def std(feature, window_size=1):
    return aggregate(np.std, feature, window_size)


def var(feature, window_size=1):
    return aggregate(np.var, feature, window_size)


def minimum(feature, window_size=1):
    return aggregate(np.minimum, feature, window_size)


def maximum(feature, window_size=1):
    return aggregate(np.maximum, feature, window_size)


def diff(feature, window_size=1):
    return np.diff(feature, n=window_size, prepend=feature[0])


def z_score(feature, window_size=1):
    _std = std(feature, window_size)
    _mean = mean(feature, window_size)
    return (feature - _mean) / _std