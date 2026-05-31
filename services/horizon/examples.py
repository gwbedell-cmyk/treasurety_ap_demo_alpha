"""
Treasurety Horizon — Example Scenarios

Demonstrates Horizon output for three governance posture profiles:
  1. Healthy system      — stable, inside attractor, improving trajectory
  2. Boundary system     — watch, near boundary, mild degradation
  3. Collapse-risk system — critical, outside attractor, rapid degradation

Run directly:  python -m services.horizon.examples
"""

import json
from . import evaluate_horizon


# ── SCENARIO DEFINITIONS ───────────────────────────────────────────────────────

SCENARIOS = {

    "Healthy System — Procurement Automation": {
        "description": (
            "An autonomous procurement agent operating within defined governance "
            "parameters. All dimensions within healthy bounds. Governance posture "
            "has been improving over the last two assessment cycles."
        ),
        "current": {
            "authority":               88,
            "scope":                   92,
            "observability":           85,
            "intervention_capability": 91,
            "accountability":          82,
            "reversibility":           78,
            "exception_control":       74,
            "drift_monitoring":        68,
        },
        "previous": {
            "authority":               82,
            "scope":                   88,
            "observability":           79,
            "intervention_capability": 85,
            "accountability":          76,
            "reversibility":           72,
            "exception_control":       68,
            "drift_monitoring":        60,
        },
        "older": {
            "authority":               77,
            "scope":                   83,
            "observability":           74,
            "intervention_capability": 80,
            "accountability":          71,
            "reversibility":           66,
            "exception_control":       63,
            "drift_monitoring":        54,
        },
    },

    "Boundary System — Finance Automation": {
        "description": (
            "A finance automation agent showing early signs of policy boundary "
            "pressure and increasing behavioral variance. Governance is drifting "
            "and the system is approaching the outer boundary of its stability zone. "
            "Governance review is recommended before further expansion."
        ),
        "current": {
            "authority":               58,
            "scope":                   64,
            "observability":           49,
            "intervention_capability": 53,
            "accountability":          67,
            "reversibility":           46,
            "exception_control":       60,
            "drift_monitoring":        42,
        },
        "previous": {
            "authority":               65,
            "scope":                   70,
            "observability":           58,
            "intervention_capability": 61,
            "accountability":          72,
            "reversibility":           55,
            "exception_control":       65,
            "drift_monitoring":        50,
        },
        "older": {
            "authority":               70,
            "scope":                   74,
            "observability":           64,
            "intervention_capability": 68,
            "accountability":          75,
            "reversibility":           62,
            "exception_control":       68,
            "drift_monitoring":        57,
        },
    },

    "Collapse-Risk System — High-Autonomy Execution Agent": {
        "description": (
            "A high-autonomy execution agent with multiple converging governance "
            "failures. Authority scope is unconstrained, observability is minimal, "
            "and intervention capability has collapsed. Governance posture is in "
            "rapid degradation across all critical dimensions. Immediate execution "
            "restriction is required."
        ),
        "current": {
            "authority":               22,
            "scope":                   31,
            "observability":           17,
            "intervention_capability": 12,
            "accountability":          38,
            "reversibility":           19,
            "exception_control":       28,
            "drift_monitoring":        14,
        },
        "previous": {
            "authority":               42,
            "scope":                   50,
            "observability":           38,
            "intervention_capability": 34,
            "accountability":          55,
            "reversibility":           40,
            "exception_control":       45,
            "drift_monitoring":        30,
        },
        "older": {
            "authority":               58,
            "scope":                   65,
            "observability":           55,
            "intervention_capability": 52,
            "accountability":          68,
            "reversibility":           58,
            "exception_control":       60,
            "drift_monitoring":        48,
        },
    },
}


# ── RENDERING ─────────────────────────────────────────────────────────────────

def _separator(char: str = "-", width: int = 72) -> str:
    return char * width


def _render_result(name: str, description: str, result) -> None:
    print()
    print(_separator("="))
    print(f"  {name}")
    print(_separator("-"))
    print(f"  {description}")
    print(_separator("-"))

    sv = result.state_vector
    print("\n  GOVERNANCE STATE VECTOR")
    for dim in ["authority", "scope", "observability", "intervention_capability",
                "accountability", "reversibility", "exception_control", "drift_monitoring"]:
        bar_len = int(getattr(sv, dim) / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        print(f"    {dim:<28}  {bar}  {getattr(sv, dim):5.1f}")

    a = result.attractor
    s = result.stability
    d = result.drift
    h = result.trust_horizon

    print(f"\n  ATTRACTOR MEMBERSHIP")
    print(f"    Status:              {a.membership_status}")
    print(f"    Label:               {result.attractor_summary.membership_label}")
    print(f"    Composite score:     {a.composite_score:.1f}")
    print(f"    Distance from center:{a.distance_from_center:.1f}")
    print(f"    Distance from boundary: {a.distance_from_boundary:+.1f}  "
          f"({'inside' if a.distance_from_boundary >= 0 else 'OUTSIDE'} stability zone)")

    print(f"\n  STABILITY")
    print(f"    Score:               {s.stability_score:.1f}")
    print(f"    Label:               {s.stability_label.upper()}")

    print(f"\n  GOVERNANCE DRIFT")
    print(f"    Direction:           {d.drift_direction}")
    print(f"    Velocity:            {d.governance_velocity:+.2f}  (composite pts/cycle)")
    print(f"    Acceleration:        {d.governance_acceleration:+.2f}  (velocity change/cycle)")
    if d.largest_degradation_dimension:
        print(f"    Largest degradation: {d.largest_degradation_dimension}")

    print(f"\n  TRUST HORIZON  [{h.confidence}]")
    print(f"    Estimate:            {h.trust_horizon_months} months")
    print(f"    Label:               {h.horizon_label}")
    print(f"    Primary risk:        {h.primary_risk_factor}")

    print(f"\n  CORRECTIVE ACTIONS")
    for action in result.corrective_actions:
        print(f"    [{action.priority}] {action.display_dimension}  [{action.expected_impact}]")
        print(f"        {action.action}")

    print()


def run_examples() -> None:
    print()
    print("  TREASURETY HORIZON v1 — EXAMPLE SCENARIOS")
    print("  " + _separator())

    results = {}
    for name, spec in SCENARIOS.items():
        result = evaluate_horizon(
            current  = spec["current"],
            previous = spec.get("previous"),
            older    = spec.get("older"),
        )
        results[name] = result
        _render_result(name, spec["description"], result)

    print(_separator("="))
    print("\n  MONITOR INTEGRATION FIELDS (flat metrics)\n")
    for name, r in results.items():
        print(f"  {name[:50]}")
        print(f"    horizon_membership:      {r.horizon_membership}")
        print(f"    horizon_stability:       {r.horizon_stability}")
        print(f"    trust_horizon_months:    {r.trust_horizon_months}")
        print(f"    governance_velocity:     {r.governance_velocity:+.3f}")
        print(f"    governance_acceleration: {r.governance_acceleration:+.3f}")
        print(f"    boundary_distance:       {r.boundary_distance:+.2f}")
        print(f"    top_drift_factor:        {r.top_drift_factor}")
        print()

    print(_separator("="))
    print("\n  JSON SERIALIZATION CHECK\n")
    sample = results[list(results.keys())[0]]
    payload = sample.to_dict()
    print(f"  Artifact keys: {list(payload.keys())}")
    print(f"  JSON serializable: ", end="")
    try:
        json.dumps(payload)
        print("YES")
    except (TypeError, ValueError) as e:
        print(f"FAILED — {e}")
    print()


if __name__ == "__main__":
    run_examples()
