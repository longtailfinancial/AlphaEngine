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


def confidence_bands(strawbroom, deviations=2):
    mean = np.mean(strawbroom, axis=0)
    std = np.std(strawbroom, axis=0)

    upper = mean + (deviations * std)
    lower = mean - (deviations * std)

    return upper, lower


def alpha(asset, strategy):
    up = asset['forward_returns'][asset['forward_returns'] > 0]
    down = asset['forward_returns'][asset['forward_returns'] < 0]
    bh_alpha = np.sum(up) / np.abs(np.sum(down))

    strat_returns = asset['forward_returns'][strategy]
    up = strat_returns[strat_returns > 0]
    down = strat_returns[strat_returns < 0]
    strat_alpha = np.sum(up) / np.abs(np.sum(down))

    alpha = (strat_alpha / bh_alpha) - 1
    return alpha