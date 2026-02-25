"""
时序分解工具
"""

import numpy as np


def seasonal_decompose(data: list, period: int = 0) -> dict:
    """Additive seasonal decomposition (trend + seasonal + residual)."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Auto-detect period if not given
    if period <= 0:
        period = _estimate_period(y)
    if period < 2 or period > n // 2:
        period = min(7, n // 3)

    # Trend: centered moving average
    trend = np.full(n, np.nan)
    half = period // 2
    for i in range(half, n - half):
        trend[i] = np.mean(y[i - half:i + half + 1])

    # Fill edges
    valid = ~np.isnan(trend)
    if valid.any():
        first_valid = np.where(valid)[0][0]
        last_valid = np.where(valid)[0][-1]
        trend[:first_valid] = trend[first_valid]
        trend[last_valid + 1:] = trend[last_valid]

    # Seasonal component
    detrended = y - trend
    seasonal = np.zeros(n)
    for i in range(period):
        indices = list(range(i, n, period))
        seasonal_mean = np.nanmean(detrended[indices])
        for idx in indices:
            seasonal[idx] = seasonal_mean

    # Residual
    residual = y - trend - seasonal

    return {
        "tool": "seasonal_decompose",
        "period": period,
        "trend_strength": round(float(
            1 - np.var(residual) / (np.var(y - seasonal) + 1e-10)
        ), 4),
        "seasonal_strength": round(float(
            1 - np.var(residual) / (np.var(y - trend) + 1e-10)
        ), 4),
        "residual_std": round(float(np.nanstd(residual)), 4),
        "trend_direction": "up" if trend[-1] > trend[0] else "down",
    }


def _estimate_period(y: np.ndarray) -> int:
    """Auto-estimate dominant period via ACF peaks."""
    n = len(y)
    if n < 8:
        return 2
    y_c = y - np.mean(y)
    corr = np.correlate(y_c, y_c, mode="full")[n - 1:]
    corr = corr / (corr[0] + 1e-10)

    # Find first peak after lag 1
    for i in range(2, len(corr) - 1):
        if corr[i] > corr[i - 1] and corr[i] > corr[i + 1] and corr[i] > 0.1:
            return i
    return min(7, n // 3)


def difference_transform(data: list, order: int = 1) -> dict:
    """Differencing transform for non-stationary series."""
    y = np.array(data, dtype=float)

    diffed = y.copy()
    for _ in range(order):
        diffed = np.diff(diffed)

    return {
        "tool": "difference_transform",
        "order": order,
        "original_mean": round(float(np.mean(y)), 4),
        "differenced_mean": round(float(np.mean(diffed)), 4),
        "differenced_std": round(float(np.std(diffed)), 4),
        "variance_reduction": round(float(
            1 - np.var(diffed) / (np.var(y) + 1e-10)
        ), 4),
    }


# --- Tool Registry ---
DECOMPOSITION_TOOLS = {
    "seasonal_decompose": {
        "fn": seasonal_decompose,
        "description": "Additive seasonal decomposition into trend, seasonal, residual. Use to understand data structure.",
        "triggers": ["decompose", "seasonal", "trend_seasonal"],
    },
    "difference_transform": {
        "fn": difference_transform,
        "description": "Differencing transform for non-stationary series. Use when stationarity test fails.",
        "triggers": ["difference", "non_stationary", "integrate"],
    },
}
