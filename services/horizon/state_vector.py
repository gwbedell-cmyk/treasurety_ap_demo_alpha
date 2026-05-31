"""
Treasurety Horizon — Governance State Vector
Normalizes raw governance signal inputs into a GovernanceStateVector.
"""

from .models import GovernanceStateVector, DIMENSION_NAMES


def build_state_vector(raw: dict) -> GovernanceStateVector:
    """
    Build and validate a GovernanceStateVector from a raw input dict.

    Each key should match a dimension name (see DIMENSION_NAMES).
    Values are expected 0–100 (higher = stronger governance posture).
    Missing dimensions default to 50 (neutral). Out-of-range values are clamped.

    Args:
        raw: Dict with any subset of DIMENSION_NAMES as keys, values 0–100.

    Returns:
        GovernanceStateVector with all 8 dimensions populated.
    """
    def clamp(v: float) -> float:
        return max(0.0, min(100.0, float(v)))

    return GovernanceStateVector(
        authority               = clamp(raw.get("authority",               50)),
        scope                   = clamp(raw.get("scope",                   50)),
        observability           = clamp(raw.get("observability",           50)),
        intervention_capability = clamp(raw.get("intervention_capability", 50)),
        accountability          = clamp(raw.get("accountability",          50)),
        reversibility           = clamp(raw.get("reversibility",           50)),
        exception_control       = clamp(raw.get("exception_control",       50)),
        drift_monitoring        = clamp(raw.get("drift_monitoring",        50)),
    )


def from_monitor_scenario(scenario: dict) -> GovernanceStateVector:
    """
    Derive a GovernanceStateVector from a Monitor scenario dict.

    Maps Monitor's existing drift/stability signals to Horizon dimensions.
    This adapter allows Horizon to run against existing Monitor scenario data
    without requiring Monitor data-model changes.

    Mapping rationale:
      authority               ← inverse of policy_drift (high drift = low authority control)
      scope                   ← inverse of behavioral_drift
      observability           ← governance_stability (directly correlated)
      intervention_capability ← inverse of intervention_drift
      accountability          ← trust_integrity
      reversibility           ← inverse of ecosystem_drift (external entanglement reduces reversibility)
      exception_control       ← inverse of policy_exception_rate
      drift_monitoring        ← inverse of escalation_trend_pct (high escalations = poor drift detection)
    """
    def inv(val: float, scale: float = 100.0) -> float:
        """Convert a drift/risk value (0=good, 100=bad) to a posture score (0=bad, 100=good)."""
        return max(0.0, min(100.0, scale - float(val)))

    return GovernanceStateVector(
        authority               = inv(scenario.get("policy_drift",          50)),
        scope                   = inv(scenario.get("behavioral_drift",       50)),
        observability           = float(scenario.get("governance_stability", 50)),
        intervention_capability = inv(scenario.get("intervention_drift",     50)),
        accountability          = float(scenario.get("trust_integrity",      50)),
        reversibility           = inv(scenario.get("ecosystem_drift",        50)),
        exception_control       = inv(scenario.get("policy_exception_rate",  50)),
        drift_monitoring        = inv(min(scenario.get("escalation_trend_pct", 50), 100)),
    )
