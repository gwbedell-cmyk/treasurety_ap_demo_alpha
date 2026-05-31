"""
Treasurety Horizon — Corrective Actions Engine
Generates prioritized governance improvement actions based on current state and drift.
"""

from .models import (
    GovernanceStateVector,
    StabilityResult,
    DriftResult,
    CorrectiveAction,
    DIMENSION_NAMES,
    DIMENSION_DISPLAY_NAMES,
)


# ── ACTION TEMPLATES ───────────────────────────────────────────────────────────
# Each dimension has 3 templates ordered by severity: [severe, moderate, mild].
# Severe = dim < 30, moderate = dim < 60, mild = dim >= 60.

_ACTION_TEMPLATES: dict[str, list[tuple[str, str]]] = {
    "authority": [
        ("Reduce delegated authority scope to the minimum required for declared operational purpose.", "HIGH"),
        ("Implement machine-enforced authority limits with runtime boundary checks.", "HIGH"),
        ("Review and document current authority grants; revoke any that exceed declared scope.", "MEDIUM"),
    ],
    "scope": [
        ("Define explicit operational scope boundaries and enforce them at the system level.", "HIGH"),
        ("Review and constrain the system's operational perimeter to declared use cases only.", "MEDIUM"),
        ("Implement scope creep detection to flag deviations from declared operational boundaries.", "MEDIUM"),
    ],
    "observability": [
        ("Increase execution observability — deploy structured action logging covering all consequential decisions.", "HIGH"),
        ("Add real-time dashboards for all high-consequence system actions with human review queues.", "HIGH"),
        ("Implement decision-point tracing to surface reasoning paths for auditors and reviewers.", "MEDIUM"),
    ],
    "intervention_capability": [
        ("Improve intervention response latency — reduce time-to-halt to under 60 seconds across all execution pathways.", "HIGH"),
        ("Test and operationalize the emergency stop procedure end-to-end with a named intervention owner.", "HIGH"),
        ("Assign and train a dedicated intervention owner with clear authority to halt the system.", "MEDIUM"),
    ],
    "accountability": [
        ("Establish named human accountability for all consequential system decisions.", "HIGH"),
        ("Implement a complete and tamper-evident audit trail for all system actions.", "HIGH"),
        ("Document the escalation chain from system alert to human decision-maker with response SLAs.", "MEDIUM"),
    ],
    "reversibility": [
        ("Identify all irreversible action pathways — require pre-action human approval for each.", "HIGH"),
        ("Implement rollback capability for the three highest-consequence action types.", "HIGH"),
        ("Add a reversibility gate before any action above a defined consequence threshold.", "MEDIUM"),
    ],
    "exception_control": [
        ("Define and test exception handling for all known failure modes — system must fail closed, not open.", "MEDIUM"),
        ("Implement graceful degradation — reduce operational scope automatically on unhandled errors.", "MEDIUM"),
        ("Add exception alerting with human-in-loop resolution for unclassified failures.", "LOW"),
    ],
    "drift_monitoring": [
        ("Deploy active governance drift detection with automated alerting on posture change above threshold.", "HIGH"),
        ("Establish a governance review cadence calibrated to the system's observed drift rate.", "MEDIUM"),
        ("Integrate Treasurety Monitor for continuous governance assurance post-deployment.", "MEDIUM"),
    ],
}

# Recommendation generation priority (most governance-critical dimensions first)
_RECOMMENDATION_PRIORITY_ORDER = [
    "authority",
    "observability",
    "intervention_capability",
    "reversibility",
    "accountability",
    "drift_monitoring",
    "scope",
    "exception_control",
]

# Only recommend action for dimensions below this threshold
_ACTION_THRESHOLD = 80.0

# Degradation boost: applied when a dimension is actively getting worse
_DEGRADATION_BOOST = 15.0
_DEGRADATION_BOOST_THRESHOLD = -5.0  # delta below this triggers the boost


def generate_corrective_actions(
    state:     GovernanceStateVector,
    stability: StabilityResult,
    drift:     DriftResult,
    n:         int = 3,
) -> list[CorrectiveAction]:
    """
    Generate the top n prioritized corrective governance actions.

    Priority scoring per dimension:
      urgency = (100 - raw_score) × priority_weight + degradation_boost

    Only dimensions with raw_score < ACTION_THRESHOLD are considered.
    Actions are drawn from dimension-specific templates calibrated to severity.

    Args:
        state:     Current GovernanceStateVector.
        stability: Current StabilityResult (unused directly but available for extension).
        drift:     Current DriftResult (provides degradation signal).
        n:         Number of actions to return (default 3, max 8).

    Returns:
        List of CorrectiveAction objects in priority order.
    """
    scored: list[tuple[str, float, float]] = []  # (dim, raw_score, urgency_score)

    for i, dim in enumerate(_RECOMMENDATION_PRIORITY_ORDER):
        raw = getattr(state, dim)
        if raw >= _ACTION_THRESHOLD:
            continue  # dimension is healthy; no action needed

        # Priority weight biases toward governance-critical dimensions
        priority_weight = 1.0 - (i * 0.04)

        # Degradation boost if dimension is actively getting worse
        delta = drift.dimension_deltas.get(dim, 0.0)
        degradation_boost = _DEGRADATION_BOOST if delta < _DEGRADATION_BOOST_THRESHOLD else 0.0

        urgency = (100.0 - raw) * priority_weight + degradation_boost
        scored.append((dim, raw, urgency))

    # Sort by urgency descending; take top n
    scored.sort(key=lambda x: x[2], reverse=True)
    top = scored[:min(n, len(scored))]

    actions = []
    for rank, (dim, raw, _) in enumerate(top, 1):
        templates = _ACTION_TEMPLATES.get(dim, [])
        if not templates:
            continue

        # Select template severity tier based on raw score
        if raw < 30.0:
            template, impact = templates[0]
        elif raw < 60.0:
            template, impact = templates[min(1, len(templates) - 1)]
        else:
            template, impact = templates[min(2, len(templates) - 1)]

        actions.append(CorrectiveAction(
            priority          = rank,
            dimension         = dim,
            display_dimension = DIMENSION_DISPLAY_NAMES.get(dim, dim),
            action            = template,
            expected_impact   = impact,
        ))

    return actions
