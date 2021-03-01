import numpy as np

Z_SCORE_TENTHS = np.arange(6.9, step=0.1) - 3.4
Z_SCORE_HUNDREDTHS = np.arange(6.9, step=0.01) - 3.4


def rolling_window(a, window_size):
    shape = (a.shape[0] - window_size + 1, window_size) + a.shape[1:]
    strides = (a.strides[0],) + a.strides
    x = np.ones((window_size - 1, window_size)) * np.nan
    return np.vstack((x, np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)))


def tn_returns(asset, n=5):
    x = rolling_window(asset['forward_returns'], window_size=n+1)
    return x[:, -1]-x[:, 0]


def aggregate(func, feature, window_size=1):
    return func(rolling_window(feature, window_size=window_size), axis=1)


def mean(feature, window_size=1):
    return aggregate(np.mean, feature, window_size)


def std(feature, window_size=1):
    return aggregate(np.std, feature, window_size)


def z_score(feature, window_size=1):
    _std = std(feature, window_size)
    _mean = mean(feature, window_size)
    return (feature - _mean) / _std


def generate_strategies(feature, gt=True, z_score_table=Z_SCORE_TENTHS):
    if gt:
        return np.stack([np.greater(feature, z_score_table[i]) for i in range(len(z_score_table))])
    else:
        return np.stack([np.less(feature, z_score_table[i]) for i in range(len(z_score_table))])


# AUX FUNCTIONS
def sum(feature, window_size=1):
    return aggregate(np.sum, feature, window_size)


def median(feature, window_size=1):
    return aggregate(np.median, feature, window_size)


def average(feature, window_size=1):
    return aggregate(np.average, feature, window_size)


def var(feature, window_size=1):
    return aggregate(np.var, feature, window_size)


def minimum(feature, window_size=1):
    return aggregate(np.minimum, feature, window_size)


def maximum(feature, window_size=1):
    return aggregate(np.maximum, feature, window_size)


def diff(feature, window_size=1):
    return np.diff(feature, n=window_size, prepend=feature[0])
