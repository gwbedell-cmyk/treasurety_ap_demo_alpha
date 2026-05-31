"""
Treasurety Horizon — Attractor Membership Analysis

Determines whether a system is inside, near, or outside its governance
stability zone (internally: TASA — Trusted Autonomous System Attractor).

Customer-facing terminology: "Attractor Membership", "Governance Stability Zone".
Internal terminology: TASA, attractor center, attractor boundary.
"""

from .models import (
    GovernanceStateVector,
    AttractorResult,
    DEFAULT_DIMENSION_WEIGHTS,
    CRITICAL_DIMENSIONS,
    ATTRACTOR_MEMBER,
    NEAR_BOUNDARY,
    OUTSIDE_ATTRACTOR,
    CRITICAL_DRIFT,
    ATTRACTOR_INNER_BOUNDARY,
    ATTRACTOR_OUTER_BOUNDARY,
    CRITICAL_COMPOSITE_FLOOR,
    CRITICAL_DIM_FLOOR,
    OUTSIDE_CRITICAL_DIM,
    BOUNDARY_CRITICAL_DIM,
)


def analyze_attractor(
    state: GovernanceStateVector,
    weights: dict = None,
) -> AttractorResult:
    """
    Determine TASA membership status and distances.

    Membership logic (priority order — most severe wins):

    CRITICAL_DRIFT:    composite < 30  OR  any critical dim < 20
    OUTSIDE_ATTRACTOR: composite < 50  OR  any critical dim < 35
    NEAR_BOUNDARY:     composite < 65  OR  any critical dim < 50
    ATTRACTOR_MEMBER:  composite >= 65 AND all critical dims >= 50

    Args:
        state:   GovernanceStateVector for the current assessment.
        weights: Optional custom dimension weights (must sum to 1.0).

    Returns:
        AttractorResult with membership status and distance metrics.
    """
    w = weights or DEFAULT_DIMENSION_WEIGHTS
    composite = state.composite(w)

    # Distance from ideal center (0 = perfect, 100 = worst possible)
    distance_from_center = round(100.0 - composite, 2)

    # Signed distance from outer boundary
    # positive = inside zone, negative = outside zone
    distance_from_boundary = round(composite - ATTRACTOR_OUTER_BOUNDARY, 2)

    # Minimum value among critical governance dimensions
    min_critical = min(getattr(state, d) for d in CRITICAL_DIMENSIONS)

    # Membership determination — most severe condition wins
    if composite < CRITICAL_COMPOSITE_FLOOR or min_critical < CRITICAL_DIM_FLOOR:
        membership = CRITICAL_DRIFT
    elif composite < ATTRACTOR_OUTER_BOUNDARY or min_critical < OUTSIDE_CRITICAL_DIM:
        membership = OUTSIDE_ATTRACTOR
    elif composite < ATTRACTOR_INNER_BOUNDARY or min_critical < BOUNDARY_CRITICAL_DIM:
        membership = NEAR_BOUNDARY
    else:
        membership = ATTRACTOR_MEMBER

    return AttractorResult(
        membership_status      = membership,
        distance_from_center   = distance_from_center,
        distance_from_boundary = distance_from_boundary,
        composite_score        = round(composite, 2),
    )
