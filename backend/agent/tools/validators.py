"""
验证工具
"""

import numpy as np


def prediction_range_check(data: list, predictions: list) -> dict:
    """Check if predictions fall within reasonable statistical bounds."""
    y = np.array(data, dtype=float)
    preds = np.array(predictions, dtype=float)
    mean_val = float(np.mean(y))
    std_val = float(np.std(y))

    lower = mean_val - 3 * std_val
    upper = mean_val + 3 * std_val

    violations = []
    for i, p in enumerate(preds):
        if p < lower or p > upper:
            violations.append({"index": i, "value": round(float(p), 4),
                               "bound": "lower" if p < lower else "upper"})

    return {
        "tool": "prediction_range_check",
        "bounds": [round(lower, 4), round(upper, 4)],
        "violation_count": len(violations),
        "violations": violations[:10],
        "pass": len(violations) == 0,
    }


def trend_consistency_check(data: list, predictions: list) -> dict:
    """Check if predictions maintain the historical trend direction."""
    y = np.array(data, dtype=float)
    preds = np.array(predictions, dtype=float)

    # Historical trend
    x_hist = np.arange(len(y))
    hist_slope = float(np.polyfit(x_hist, y, 1)[0])

    # Prediction trend
    x_pred = np.arange(len(preds))
    pred_slope = float(np.polyfit(x_pred, preds, 1)[0]) if len(preds) > 1 else 0

    # Continuity: gap between last historical and first prediction
    gap = abs(float(preds[0] - y[-1]))
    gap_ratio = gap / (float(np.std(y)) + 1e-10)

    consistent = (hist_slope * pred_slope >= 0) or abs(hist_slope) < 1e-6

    return {
        "tool": "trend_consistency_check",
        "hist_slope": round(hist_slope, 6),
        "pred_slope": round(pred_slope, 6),
        "consistent": consistent,
        "continuity_gap": round(gap, 4),
        "gap_ratio": round(gap_ratio, 4),
        "smooth_transition": gap_ratio < 1.0,
    }


def confidence_scoring(data: list, predictions: list) -> dict:
    """Compute confidence score based on multiple validation checks."""
    y = np.array(data, dtype=float)
    preds = np.array(predictions, dtype=float)
    score = 1.0

    # Penalize range violations
    std_val = float(np.std(y))
    mean_val = float(np.mean(y))
    for p in preds:
        if abs(p - mean_val) > 3 * std_val:
            score *= 0.85

    # Penalize trend inconsistency
    hist_slope = float(np.polyfit(np.arange(len(y)), y, 1)[0])
    if len(preds) > 1:
        pred_slope = float(np.polyfit(np.arange(len(preds)), preds, 1)[0])
        if hist_slope * pred_slope < 0 and abs(hist_slope) > 1e-4:
            score *= 0.8

    # Penalize large gap
    gap = abs(float(preds[0] - y[-1])) / (std_val + 1e-10)
    if gap > 2.0:
        score *= 0.75

    score = max(0.1, min(1.0, score))

    return {
        "tool": "confidence_scoring",
        "confidence": round(score, 3),
        "level": "high" if score > 0.7 else "medium" if score > 0.4 else "low",
    }


# --- Tool Registry ---
VALIDATOR_TOOLS = {
    "prediction_range_check": {
        "fn": prediction_range_check,
        "description": "Check predictions against 3-sigma statistical bounds.",
        "triggers": ["range", "bounds", "validate"],
    },
    "trend_consistency_check": {
        "fn": trend_consistency_check,
        "description": "Verify predictions maintain historical trend direction.",
        "triggers": ["trend_check", "consistency"],
    },
    "confidence_scoring": {
        "fn": confidence_scoring,
        "description": "Compute overall confidence score for predictions.",
        "triggers": ["confidence", "score"],
    },
}
