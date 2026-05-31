"""
Treasurety Horizon — Stability Engine
Computes the governance stability score and stability label from a state vector.
"""

from .models import (
    GovernanceStateVector,
    StabilityResult,
    DEFAULT_DIMENSION_WEIGHTS,
    DIMENSION_NAMES,
    STABILITY_STABLE,
    STABILITY_WATCH,
    STABILITY_UNSTABLE,
    STABILITY_CRITICAL,
    STABILITY_THRESHOLDS,
)


def compute_stability(
    state: GovernanceStateVector,
    weights: dict = None,
) -> StabilityResult:
    """
    Compute governance stability score and label.

    Stability score = weighted average of all dimension scores (0–100).
    Because weights sum to 1.0 and each dimension is 0–100, the result
    is also in 0–100.

    Labels:
      stable    >= 75
      watch     >= 50
      unstable  >= 30
      critical  <  30

    Args:
        state:   GovernanceStateVector for the current assessment.
        weights: Optional custom dimension weights (must sum to 1.0).

    Returns:
        StabilityResult with score, label, per-dimension breakdown, and weakest dims.
    """
    w = weights or DEFAULT_DIMENSION_WEIGHTS

    # Per-dimension weighted contributions
    dimension_scores = {
        dim: round(getattr(state, dim) * w.get(dim, 0.125), 3)
        for dim in DIMENSION_NAMES
    }

    stability_score = round(sum(dimension_scores.values()), 2)

    # Label (threshold comparison in descending order)
    if stability_score >= STABILITY_THRESHOLDS[STABILITY_STABLE]:
        label = STABILITY_STABLE
    elif stability_score >= STABILITY_THRESHOLDS[STABILITY_WATCH]:
        label = STABILITY_WATCH
    elif stability_score >= STABILITY_THRESHOLDS[STABILITY_UNSTABLE]:
        label = STABILITY_UNSTABLE
    else:
        label = STABILITY_CRITICAL

    # Weakest dimensions: sorted by raw score ascending (most vulnerable first)
    weakest = sorted(DIMENSION_NAMES, key=lambda d: getattr(state, d))

    return StabilityResult(
        stability_score    = stability_score,
        stability_label    = label,
        dimension_scores   = dimension_scores,
        weakest_dimensions = weakest,
    )
