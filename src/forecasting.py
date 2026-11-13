"""Rolling OLS and paired block bootstrap adapted from the original research scripts.

For every origin, only six-session labels already observed at that origin may
enter the last 1,260 training rows. Original numerical routines are preserved.
"""
import numpy as np
import pandas as pd

WINDOW = 1260
HORIZON = 6
RATIO = 'vix3m_vix'
BASELINES = ['historical_mean', 'no_change']


def fit_forecasts(features, factors, origins):
    """Use the last 1,260 labels mature at each origin and fit with an intercept."""
    x = features[factors].to_numpy(dtype=float)
    y = features.actual_return.to_numpy(dtype=float)
    mature = features.target_date.dropna().to_numpy()
    dates = features.date.to_numpy()
    close = features.close.to_numpy(dtype=float)
    actual = features.actual_close.to_numpy(dtype=float)
    models = factors + BASELINES
    predictions = np.empty((len(origins), len(models)))

    for offset, index in enumerate(origins):
        end = mature.searchsorted(dates[index], side='right')
        assert end >= WINDOW and end <= index
        assert mature[end - 1] <= dates[index]
        assert end == index - HORIZON + 1
        train = slice(end - WINDOW, end)
        training_x, training_y = x[train], y[train]
        x_mean, y_mean = training_x.mean(axis=0), training_y.mean()
        centered_x = training_x - x_mean
        sum_squares = np.square(centered_x).sum(axis=0)
        assert (sum_squares > 0).all()
        slopes = (centered_x * (training_y - y_mean)[:, None]).sum(axis=0) / sum_squares
        returns = y_mean + (x[index] - x_mean) * slopes
        predictions[offset] = close[index] * (1 + np.r_[returns, y_mean, 0.0])

    assert np.isfinite(predictions).all()
    return pd.DataFrame(predictions, index=pd.DatetimeIndex(dates[origins], name='origin_date'), columns=models)

def error_percent(predictions, features):
    actual = features.set_index('date').actual_close.loc[predictions.index]
    return predictions.sub(actual, axis=0).abs().div(actual, axis=0) * 100

def ranking(losses, factors):
    table = losses[factors].mean().rename_axis('factor').reset_index(name='MAPE_pct')
    return table.sort_values(['MAPE_pct', 'factor']).reset_index(drop=True)

def bootstrap_difference(later, model, reference):
    """A conditional, paired uncertainty check for a fixed later-period comparison."""
    difference = (later[model] - later[reference]).to_numpy()
    length = 20
    n = len(difference)
    rng = np.random.default_rng(20261110)
    starts = rng.integers(0, n, (3000, (n + length - 1) // length))
    blocks = (starts[:, :, None] + np.arange(length)) % n
    draws = difference[blocks.reshape(3000, -1)[:, :n]].mean(axis=1)
    low, high = np.quantile(draws, [0.025, 0.975])
    return {'model': model, 'reference': reference, 'difference_pp': float(difference.mean()),
            'ci95_low_pp': float(low), 'ci95_high_pp': float(high)}

def fit_pairs(features, factors, origins):
    columns = [RATIO, *factors]
    values = features[columns].to_numpy(dtype=float)
    dates = features.date.to_numpy()
    returns = features.actual_return.to_numpy(dtype=float)
    target_dates = features.target_date.dropna().to_numpy()
    assert np.isfinite(values[:origins[-1] + 1]).all()
    predicted = np.empty((len(origins), len(factors)))
    largest_condition = 0.0
    for row, origin in enumerate(origins):
        end = target_dates.searchsorted(dates[origin], side='right')
        assert end >= WINDOW and end == origin - HORIZON + 1
        training = values[end - WINDOW:end]
        mean = training.mean(axis=0)
        scale = training.std(axis=0)
        assert np.all(scale > 0)
        normalised = (training - mean) / scale
        today = (values[origin] - mean) / scale
        design = np.column_stack((np.ones(WINDOW), normalised[:, 0], np.zeros(WINDOW)))
        y = returns[end - WINDOW:end]
        for col in range(1, len(columns)):
            design[:, 2] = normalised[:, col]
            coefs, _, rank, singular = np.linalg.lstsq(design, y, rcond=None)
            assert rank == 3
            largest_condition = max(largest_condition, float(singular[0] / singular[-1]))
            predicted_return = coefs @ [1, today[0], today[col]]
            predicted[row, col - 1] = features.close.iloc[origin] * (1 + predicted_return)
    assert np.isfinite(predicted).all() and np.all(predicted > 0)
    return pd.DataFrame(predicted, index=pd.DatetimeIndex(dates[origins], name='origin_date'), columns=factors), largest_condition

def bootstrap(losses, base):
    differences = losses.sub(base, axis=0).to_numpy()
    measured = differences.mean(axis=0)
    n = len(differences)
    block, draws = 20, 3000
    rng = np.random.default_rng(20261110)
    starts = rng.integers(0, n, (draws, (n + block - 1) // block))
    indices = ((starts[:, :, None] + np.arange(block)) % n).reshape(draws, -1)[:, :n]
    weights = np.stack([np.bincount(draw, minlength=n) / n for draw in indices])
    means = weights @ differences
    centred = means - measured
    observed = max(0, float(-measured.min()))
    null_max = np.maximum(0, (-centred).max(axis=1))
    half_width = float(np.quantile(np.abs(centred).max(axis=1), .95))
    bounds = np.quantile(means, [.025, .975], axis=0)
    results = pd.DataFrame({'difference_pp': measured, 'CI95_low_pp': bounds[0], 'CI95_high_pp': bounds[1],
                            'simultaneous95_low_pp': measured - half_width, 'simultaneous95_high_pp': measured + half_width}, index=losses.columns)
    p_value = float((1 + (null_max >= observed).sum()) / (draws + 1))
    return results, p_value
