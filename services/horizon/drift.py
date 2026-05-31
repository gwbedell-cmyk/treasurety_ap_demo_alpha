"""
Treasurety Horizon — Drift Engine
Compares current governance state to prior states to compute velocity,
acceleration, and drift direction.
"""

from typing import Optional

from .models import (
    GovernanceStateVector,
    DriftResult,
    DEFAULT_DIMENSION_WEIGHTS,
    DIMENSION_NAMES,
    DRIFT_IMPROVING,
    DRIFT_STABLE,
    DRIFT_DEGRADING,
    DRIFT_RAPID_DEGRADATION,
    DRIFT_VELOCITY_IMPROVING_THRESHOLD,
    DRIFT_VELOCITY_DEGRADING_THRESHOLD,
    DRIFT_ACCELERATION_CRITICAL_THRESHOLD,
)


def compute_drift(
    current:  GovernanceStateVector,
    previous: Optional[GovernanceStateVector],
    older:    Optional[GovernanceStateVector] = None,
    weights:  dict = None,
) -> DriftResult:
    """
    Compute governance drift between the current and prior assessment states.

    Governance velocity: weighted composite change from previous → current cycle.
      Positive = governance improving. Negative = governance degrading.

    Governance acceleration: change in velocity from (older→previous) → (previous→current).
      Negative acceleration = degradation is worsening over time.

    Drift direction (priority order):
      RAPID_DEGRADATION: velocity < -3 AND acceleration < -5
      DEGRADING:         velocity < -3
      IMPROVING:         velocity >  3
      STABLE:            -3 <= velocity <= 3

    Args:
        current:  Current GovernanceStateVector.
        previous: Previous assessment state (required for velocity).
        older:    Assessment before previous (required for acceleration).
        weights:  Optional custom dimension weights.

    Returns:
        DriftResult. If previous is None, returns a neutral (STABLE, zero) result.
    """
    w = weights or DEFAULT_DIMENSION_WEIGHTS

    if previous is None:
        return DriftResult(
            governance_velocity           = 0.0,
            governance_acceleration       = 0.0,
            drift_direction               = DRIFT_STABLE,
            dimension_deltas              = {dim: 0.0 for dim in DIMENSION_NAMES},
            largest_degradation_dimension = None,
        )

    # Per-dimension deltas (positive = dimension improved)
    deltas = {
        dim: round(getattr(current, dim) - getattr(previous, dim), 2)
        for dim in DIMENSION_NAMES
    }

    # Weighted governance velocity
    velocity = round(sum(deltas[dim] * w.get(dim, 0.125) for dim in DIMENSION_NAMES), 3)

    # Governance acceleration (requires an older state)
    acceleration = 0.0
    if older is not None:
        prev_deltas = {
            dim: getattr(previous, dim) - getattr(older, dim)
            for dim in DIMENSION_NAMES
        }
        prev_velocity = sum(prev_deltas[dim] * w.get(dim, 0.125) for dim in DIMENSION_NAMES)
        acceleration = round(velocity - prev_velocity, 3)

    # Drift direction — priority order: most severe wins
    if (velocity < DRIFT_VELOCITY_DEGRADING_THRESHOLD and
            acceleration < DRIFT_ACCELERATION_CRITICAL_THRESHOLD):
        direction = DRIFT_RAPID_DEGRADATION
    elif velocity < DRIFT_VELOCITY_DEGRADING_THRESHOLD:
        direction = DRIFT_DEGRADING
    elif velocity > DRIFT_VELOCITY_IMPROVING_THRESHOLD:
        direction = DRIFT_IMPROVING
    else:
        direction = DRIFT_STABLE

    # Identify the dimension with the largest negative delta
    degrading = {dim: d for dim, d in deltas.items() if d < 0}
    largest_degradation = (
        min(degrading, key=degrading.get) if degrading else None
    )

    return DriftResult(
        governance_velocity           = velocity,
        governance_acceleration       = acceleration,
        drift_direction               = direction,
        dimension_deltas              = deltas,
        largest_degradation_dimension = largest_degradation,
    )
