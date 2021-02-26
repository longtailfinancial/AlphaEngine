import numpy as np


def monte_carlo(asset, strategy, samples=1000, simulations=1000):
    returns = asset['forward_returns'][strategy]

    if len(returns) == 0:
        return np.zeros((samples, simulations))

    strawbroom = np.stack([np.cumsum(np.random.choice(returns, samples)) for _ in range(simulations)])
    return strawbroom


def performance(asset, strategy):
    return strategy.astype(int) * asset['forward_returns']


# Takes an individual set of returns and returns the cumulative drawdown
def drawdown(equity_curve):
    return equity_curve / np.maximum.accumulate(equity_curve)


# Takes a monte carlo strawbrook and returns the worst drawdown possible
def worst_drawdown(strawbroom):
    return drawdown(np.min(strawbroom, axis=0))


def sharpe(returns):
    return np.mean(returns) / np.std(returns)


def confidence_bands(strawbroom, deviations=2):
    mean = np.mean(strawbroom, axis=0)
    std = np.std(strawbroom, axis=0)

    upper = mean + (deviations * std)
    lower = mean - (deviations * std)

    return upper, lower


def alpha(asset, strategy):
    """Compared buy and hold to the strategy. Positive alpha is good. Negative is bad."""
    up = asset['forward_returns'][asset['forward_returns'] > 0]
    down = asset['forward_returns'][asset['forward_returns'] < 0]
    bh_alpha = np.sum(up) / np.abs(np.sum(down))

    strat_returns = asset['forward_returns'][strategy]
    up = strat_returns[strat_returns > 0]
    down = strat_returns[strat_returns < 0]
    strat_alpha = np.sum(up) / np.abs(np.sum(down))

    _alpha = (strat_alpha / bh_alpha) - 1
    return _alpha


def vectorized_alpha(asset, strategies):
    """Compared buy and hold to the strategy. Positive alpha is good. Negative is bad."""
    up = asset['forward_returns'][asset['forward_returns'] > 0]
    down = asset['forward_returns'][asset['forward_returns'] < 0]
    bh_alpha = np.sum(up) / np.abs(np.sum(down))

    strat_returns = asset['forward_returns'][:, np.newaxis].T * strategies
    up = strat_returns * (strat_returns[:, ] > 0)
    down = strat_returns * (strat_returns[:, ] < 0)
    strat_alpha = np.sum(up, axis=1) / np.abs(np.sum(down, axis=1))

    _alpha = (strat_alpha / bh_alpha) - 1
    return _alpha


def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = (len(data))

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y


def time_in_market(strategy):
    return np.sum(strategy.astype(int)) / len(strategy)


def volatility_efficiency(asset, strategy):
    """Determines how effective the strategy is and how it
    would perform if leveraged to the same risk as buy and hold"""
    perf = performance(asset, strategy)
    strat_perf = np.cumsum(perf)

    buy_hold_perf = np.cumsum(asset['forward_returns'])

    strat_v_bh = strat_perf[-1] / buy_hold_perf[-1]

    return strat_v_bh / time_in_market(strategy)


def vectorized_volatility_efficiency(asset, strategy):
    """Determines how effective the strategy is and how it
    would perform if leveraged to the same risk as buy and hold"""
    perf = performance(asset, strategy)
    strat_perf = np.cumsum(perf, axis=1)

    buy_hold_perf = np.cumsum(asset['forward_returns'])

    strat_v_bh = strat_perf[:, -1] / buy_hold_perf[-1]

    return strat_v_bh / (np.sum(strategy.astype(int), axis=1) / strategy.shape[1])
