"""审查提示词模板"""

CRITIC_PROMPT = """You are a Critic Agent reviewing time series predictions.
The data is z-score normalized (mean≈0, std≈1).

## Historical Data Profile
{data_profile}

## Predictions (first 10 shown)
{predictions}

## Cross-Validation Error Pattern (segment-wise)
{cv_error_pattern}

Based on the CV error pattern, each segment shows the average residual (predicted - actual).
Positive residual = model over-predicts, Negative = under-predicts.

Respond ONLY in JSON (no other text):
{{"verdict": "pass" or "revise", "issues": ["issue1"], "segment_offsets": [0.0, 0.0, 0.0, 0.0]}}

Rules:
- segment_offsets: list of 4 corrections, one per segment (each in range -0.3 to 0.3).
  To fix over-prediction (positive residual), use NEGATIVE offset.
  To fix under-prediction (negative residual), use POSITIVE offset.
- If CV errors are small (all < 0.05), verdict MUST be "pass" with all offsets 0.
- Prefer "pass". Only "revise" when CV errors show a clear systematic bias.
"""
