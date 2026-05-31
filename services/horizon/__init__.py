"""
Treasurety Horizon v1 — Governance Stability and Trust Horizon Engine

A premium capability extension to Treasurety Monitor. Horizon extends Monitor
by introducing governance-state vector analysis, attractor membership
determination, drift detection, and Trust Horizon estimation.

Primary entry point:
    from services.horizon import evaluate_horizon
    result = evaluate_horizon(current={...})

Monitor integration:
    The HorizonResult exposes flat metric fields (horizon_membership,
    horizon_stability, trust_horizon_months, governance_velocity,
    governance_acceleration, boundary_distance, top_drift_factor)
    that integrate directly with existing Monitor metric pipelines.

Adapter for existing Monitor scenarios:
    from services.horizon import evaluate_horizon_from_monitor_scenario
    result = evaluate_horizon_from_monitor_scenario(scenario_dict)

Internal note: TASA (Trusted Autonomous System Attractor) is the internal
mathematical framework. All customer-facing language uses "Governance
Stability Zone", "Attractor Membership", "Trust Horizon", and "Governance Drift".
"""

from datetime import datetime, timezone

from .models import (
    GovernanceStateVector,
    HorizonResult,
    AttractorSummary,
    TrustHorizonSummary,
    GovernanceTrajectorySummary,
    ATTRACTOR_STATUS_LABELS,
    DIMENSION_DISPLAY_NAMES,
    DRIFT_IMPROVING,
    DRIFT_STABLE,
    DRIFT_DEGRADING,
    DRIFT_RAPID_DEGRADATION,
    ATTRACTOR_OUTER_BOUNDARY,
)
from .state_vector import build_state_vector, from_monitor_scenario
from .attractor import analyze_attractor
from .stability import compute_stability
from .drift import compute_drift
from .trust_horizon import compute_trust_horizon
from .recommendations import generate_corrective_actions


_HORIZON_VERSION = "1.0"

_TREND_LABELS = {
    DRIFT_IMPROVING:         "Governance posture is improving",
    DRIFT_STABLE:            "Governance posture is stable",
    DRIFT_DEGRADING:         "Governance posture is degrading",
    DRIFT_RAPID_DEGRADATION: "Rapid governance degradation in progress",
}


def evaluate_horizon(
    current:  dict,
    previous: dict = None,
    older:    dict = None,
    weights:  dict = None,
) -> HorizonResult:
    """
    Primary entry point for Treasurety Horizon evaluation.

    Args:
        current:  Governance state as dimension dict (0–100 per dimension).
                  Keys: authority, scope, observability, intervention_capability,
                        accountability, reversibility, exception_control, drift_monitoring.
        previous: Previous assessment state dict (enables drift/velocity calculation).
        older:    Assessment before previous (enables acceleration calculation).
        weights:  Optional custom dimension weights (must sum to 1.0).

    Returns:
        HorizonResult containing all Horizon metrics, sub-results, dashboard
        summaries, and flat Monitor integration fields.
    """
    current_sv  = build_state_vector(current)
    previous_sv = build_state_vector(previous) if previous else None
    older_sv    = build_state_vector(older)    if older    else None

    return _run_evaluation(current_sv, previous_sv, older_sv, weights)


def evaluate_horizon_from_monitor_scenario(
    scenario:          dict,
    previous_scenario: dict = None,
    older_scenario:    dict = None,
    weights:           dict = None,
) -> HorizonResult:
    """
    Evaluate Horizon from a Monitor scenario dict without data-model changes.

    Uses the Monitor adapter in state_vector.from_monitor_scenario() to map
    existing Monitor drift/stability signals to Horizon dimensions.

    Args:
        scenario:          Current Monitor scenario dict.
        previous_scenario: Previous Monitor scenario dict (for drift).
        older_scenario:    Older Monitor scenario dict (for acceleration).
        weights:           Optional custom dimension weights.

    Returns:
        HorizonResult.
    """
    current_sv  = from_monitor_scenario(scenario)
    previous_sv = from_monitor_scenario(previous_scenario) if previous_scenario else None
    older_sv    = from_monitor_scenario(older_scenario)    if older_scenario    else None

    return _run_evaluation(current_sv, previous_sv, older_sv, weights)


def _run_evaluation(
    current_sv:  GovernanceStateVector,
    previous_sv: GovernanceStateVector,
    older_sv:    GovernanceStateVector,
    weights:     dict,
) -> HorizonResult:
    """Internal evaluation pipeline shared by all entry points."""
    attractor    = analyze_attractor(current_sv, weights)
    stability    = compute_stability(current_sv, weights)
    drift        = compute_drift(current_sv, previous_sv, older_sv, weights)
    trust_hz     = compute_trust_horizon(stability, attractor, drift, current_sv)
    corrections  = generate_corrective_actions(current_sv, stability, drift)

    top_drift_factor = drift.largest_degradation_dimension or "none"

    attractor_summary = AttractorSummary(
        membership_status      = attractor.membership_status,
        membership_label       = ATTRACTOR_STATUS_LABELS.get(
                                     attractor.membership_status, attractor.membership_status),
        distance_from_center   = attractor.distance_from_center,
        distance_from_boundary = attractor.distance_from_boundary,
        boundary_threshold     = int(ATTRACTOR_OUTER_BOUNDARY),
    )

    trust_horizon_summary = TrustHorizonSummary(
        trust_horizon_months = trust_hz.trust_horizon_months,
        horizon_label        = trust_hz.horizon_label,
        confidence           = trust_hz.confidence,
        primary_risk_factor  = trust_hz.primary_risk_factor,
    )

    trajectory_summary = GovernanceTrajectorySummary(
        current_stability       = stability.stability_score,
        stability_label         = stability.stability_label,
        drift_direction         = drift.drift_direction,
        governance_velocity     = drift.governance_velocity,
        governance_acceleration = drift.governance_acceleration,
        top_drift_factor        = DIMENSION_DISPLAY_NAMES.get(top_drift_factor, top_drift_factor),
        trend_label             = _TREND_LABELS.get(drift.drift_direction, drift.drift_direction),
    )

    return HorizonResult(
        # Flat Monitor integration fields
        horizon_membership      = attractor.membership_status,
        horizon_stability       = stability.stability_score,
        trust_horizon_months    = trust_hz.trust_horizon_months,
        governance_velocity     = drift.governance_velocity,
        governance_acceleration = drift.governance_acceleration,
        boundary_distance       = attractor.distance_from_boundary,
        top_drift_factor        = top_drift_factor,

        # Full sub-results
        state_vector       = current_sv,
        attractor          = attractor,
        stability          = stability,
        drift              = drift,
        trust_horizon      = trust_hz,
        corrective_actions = corrections,

        # Dashboard objects
        attractor_summary      = attractor_summary,
        trust_horizon_summary  = trust_horizon_summary,
        trajectory_summary     = trajectory_summary,

        # Metadata
        evaluated_at    = datetime.now(timezone.utc).isoformat(),
        horizon_version = _HORIZON_VERSION,
    )


__all__ = [
    "evaluate_horizon",
    "evaluate_horizon_from_monitor_scenario",
    "HorizonResult",
    "GovernanceStateVector",
]
