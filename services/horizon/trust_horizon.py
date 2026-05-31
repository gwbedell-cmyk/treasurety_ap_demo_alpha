"""
Treasurety Horizon — Trust Horizon Estimation

Produces a heuristic estimate of how long current governance posture can
reasonably be expected to hold. All outputs MUST be presented to users with
the confidence label "Heuristic estimate".

This module is intentionally heuristic. It is designed to be replaceable
with a Lyapunov-based stability certificate in a future protocol version.
"""

from .models import (
    GovernanceStateVector,
    AttractorResult,
    StabilityResult,
    DriftResult,
    TrustHorizonResult,
    CRITICAL_DIMENSIONS,
    DIMENSION_DISPLAY_NAMES,
    ATTRACTOR_MEMBER,
    NEAR_BOUNDARY,
    OUTSIDE_ATTRACTOR,
    CRITICAL_DRIFT,
    DRIFT_IMPROVING,
    DRIFT_STABLE,
    DRIFT_DEGRADING,
    DRIFT_RAPID_DEGRADATION,
    HORIZON_STABLE,
    HORIZON_WATCH,
    HORIZON_URGENT,
    HORIZON_EXPIRED,
    HORIZON_STABLE_MONTHS,
    HORIZON_WATCH_MONTHS,
    HORIZON_URGENT_MONTHS,
    HORIZON_CONFIDENCE,
)


# ── BASE HORIZON BY STABILITY SCORE ───────────────────────────────────────────

_BASE_MONTHS = {
    # (min_score_inclusive, base_months)
    75.0: 12.0,
    50.0:  6.0,
    30.0:  3.0,
     0.0:  1.0,
}

# ── MULTIPLIERS ───────────────────────────────────────────────────────────────

_DRIFT_MULTIPLIERS = {
    DRIFT_IMPROVING:         1.5,
    DRIFT_STABLE:            1.0,
    DRIFT_DEGRADING:         0.6,
    DRIFT_RAPID_DEGRADATION: 0.3,
}

_MEMBERSHIP_MULTIPLIERS = {
    ATTRACTOR_MEMBER:  1.0,
    NEAR_BOUNDARY:     0.85,
    OUTSIDE_ATTRACTOR: 0.70,
    CRITICAL_DRIFT:    0.40,
}

# ── CRITICAL DIMENSION PENALTY (months subtracted) ────────────────────────────

_CRITICAL_DIM_PENALTY_SEVERE    = 2.0  # dim < 20
_CRITICAL_DIM_PENALTY_MODERATE  = 1.0  # dim < 40


def compute_trust_horizon(
    stability: StabilityResult,
    attractor: AttractorResult,
    drift:     DriftResult,
    state:     GovernanceStateVector,
) -> TrustHorizonResult:
    """
    Estimate Trust Horizon in months.

    Calculation steps:
      1. Base months derived from stability score.
      2. Apply drift direction multiplier.
      3. Subtract penalties for critical dimensions in crisis.
      4. Apply attractor membership multiplier.
      5. Clamp to [0, ∞), round to one decimal place.
      6. Assign label: Stable / Watch / Urgent / Expired Horizon.

    All results carry confidence = "Heuristic estimate".

    Args:
        stability: StabilityResult for current state.
        attractor: AttractorResult for current state.
        drift:     DriftResult for current state.
        state:     GovernanceStateVector for current state.

    Returns:
        TrustHorizonResult.
    """
    factors: dict = {}

    # Step 1: base months from stability score
    base = 1.0
    for threshold, months in sorted(_BASE_MONTHS.items(), reverse=True):
        if stability.stability_score >= threshold:
            base = months
            break
    factors["base_months"] = base

    # Step 2: drift direction multiplier
    drift_mult = _DRIFT_MULTIPLIERS.get(drift.drift_direction, 1.0)
    factors["drift_multiplier"] = drift_mult
    base *= drift_mult

    # Step 3: critical dimension penalties
    penalty = 0.0
    for dim in CRITICAL_DIMENSIONS:
        val = getattr(state, dim)
        if val < 20.0:
            penalty += _CRITICAL_DIM_PENALTY_SEVERE
        elif val < 40.0:
            penalty += _CRITICAL_DIM_PENALTY_MODERATE
    factors["critical_dimension_penalty_months"] = -penalty
    base -= penalty

    # Step 4: membership multiplier
    membership_mult = _MEMBERSHIP_MULTIPLIERS.get(attractor.membership_status, 1.0)
    factors["membership_multiplier"] = membership_mult
    base *= membership_mult

    trust_horizon_months = round(max(0.0, base), 1)
    factors["result_months"] = trust_horizon_months

    # Step 5: label
    if trust_horizon_months >= HORIZON_STABLE_MONTHS:
        label = HORIZON_STABLE
    elif trust_horizon_months >= HORIZON_WATCH_MONTHS:
        label = HORIZON_WATCH
    elif trust_horizon_months >= HORIZON_URGENT_MONTHS:
        label = HORIZON_URGENT
    else:
        label = HORIZON_EXPIRED

    primary_risk = _determine_primary_risk(stability, attractor, drift, state)

    return TrustHorizonResult(
        trust_horizon_months = trust_horizon_months,
        horizon_label        = label,
        confidence           = HORIZON_CONFIDENCE,
        primary_risk_factor  = primary_risk,
        horizon_factors      = factors,
    )


def _determine_primary_risk(
    stability: StabilityResult,
    attractor: AttractorResult,
    drift:     DriftResult,
    state:     GovernanceStateVector,
) -> str:
    """Identify the single most material risk driving Trust Horizon reduction."""

    # Rapid degradation in a specific dimension
    if drift.drift_direction == DRIFT_RAPID_DEGRADATION:
        dim = drift.largest_degradation_dimension
        if dim:
            return f"Rapid degradation in {DIMENSION_DISPLAY_NAMES.get(dim, dim)}"
        return "Rapid multi-dimensional governance degradation"

    # Critical drift — find the lowest critical dimension
    if attractor.membership_status == CRITICAL_DRIFT:
        lowest = min(CRITICAL_DIMENSIONS, key=lambda d: getattr(state, d))
        return f"Critical governance failure in {DIMENSION_DISPLAY_NAMES.get(lowest, lowest)}"

    # Active degradation in a specific dimension
    if drift.drift_direction == DRIFT_DEGRADING and drift.largest_degradation_dimension:
        dim = drift.largest_degradation_dimension
        return f"Active degradation in {DIMENSION_DISPLAY_NAMES.get(dim, dim)}"

    # Outside attractor — report weakest dimension
    if attractor.membership_status == OUTSIDE_ATTRACTOR:
        weakest = stability.weakest_dimensions[0] if stability.weakest_dimensions else "unknown"
        return f"Governance posture below stability threshold — weakest: {DIMENSION_DISPLAY_NAMES.get(weakest, weakest)}"

    # Near boundary — report weakest dimension
    if attractor.membership_status == NEAR_BOUNDARY:
        weakest = stability.weakest_dimensions[0] if stability.weakest_dimensions else "unknown"
        return f"Approaching governance boundary — watch {DIMENSION_DISPLAY_NAMES.get(weakest, weakest)}"

    # Stable but with a notable weak dimension
    if stability.weakest_dimensions:
        weakest = stability.weakest_dimensions[0]
        score = getattr(state, weakest)
        if score < 60:
            return f"Governance improvement opportunity in {DIMENSION_DISPLAY_NAMES.get(weakest, weakest)}"

    return "No material risk factors identified — maintain current governance posture"
