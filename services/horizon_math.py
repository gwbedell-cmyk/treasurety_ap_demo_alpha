"""
Treasurety Horizon -- Mathematical Stability Layer

Provides heuristic mathematical stability indicators as a supplement to the
core Horizon governance assessment. All outputs are labeled as heuristic
estimates pending longitudinal calibration.

Customer-facing language: Horizon Stability, Trust Horizon, Boundary Condition,
Drift Pressure, Coherence Exhaustion, Resonance Pressure.
Internal convention: TASA, Lyapunov, V_inst are NOT exposed to customers.

Primary entry point:
    from services.horizon_math import compute_horizon_math
    result = compute_horizon_math(state, previous_state=None, base_trust_horizon_months=None)
"""

import math
from dataclasses import dataclass, asdict
from typing import Optional

from services.horizon.models import (
    GovernanceStateVector,
    DIMENSION_NAMES,
    DRIFT_DEGRADING,
    DRIFT_RAPID_DEGRADATION,
)


# -- INSTABILITY P-MATRIX (diagonal) -------------------------------------------
# Weights reflect governance criticality: authority and observability carry
# the highest instability cost.

_P_DIAG = {
    "authority":               1.8,
    "scope":                   1.2,
    "observability":           1.6,
    "intervention_capability": 1.6,
    "accountability":          1.2,
    "reversibility":           1.1,
    "exception_control":       1.0,
    "drift_monitoring":        1.0,
}
_P_MAX = sum(_P_DIAG.values())   # 10.5


# -- BARRIER THRESHOLDS --------------------------------------------------------

_HARD_BARRIER_THRESHOLD = 40.0   # any critical dim below this -> HARD_BARRIER_ACTIVE
_WARNING_THRESHOLD      = 55.0   # any critical dim below this (but >= 40) -> WARNING
_REVERSIBILITY_BARRIER  = 35.0   # reversibility below this -> irreversibility semi-barrier
_BARRIER_DIMS = ["authority", "observability", "intervention_capability"]

BARRIER_CLEAR  = "CLEAR"
BARRIER_WARN   = "WARNING"
BARRIER_HARD   = "HARD_BARRIER_ACTIVE"


# -- RESONANCE R-MATRIX --------------------------------------------------------
# 5-dim q: [observability, intervention_capability, accountability, reversibility, drift_monitoring]
# Symmetric positive-definite; off-diagonal entries capture correlated failure risk.

_RESONANCE_DIMS = [
    "observability",
    "intervention_capability",
    "accountability",
    "reversibility",
    "drift_monitoring",
]

_R = [
    [1.0, 0.4, 0.6, 0.2, 0.3],   # observability
    [0.4, 1.0, 0.5, 0.3, 0.4],   # intervention_capability
    [0.6, 0.5, 1.0, 0.4, 0.3],   # accountability
    [0.2, 0.3, 0.4, 1.0, 0.5],   # reversibility
    [0.3, 0.4, 0.3, 0.5, 1.0],   # drift_monitoring
]
_R_MAX = sum(sum(row) for row in _R)   # 12.8

_RESONANCE_BANDS = [
    (20.0,  "LOW"),
    (45.0,  "ELEVATED"),
    (70.0,  "HIGH"),
    (101.0, "CRITICAL"),
]


# -- CED THRESHOLDS ------------------------------------------------------------

_CED_EPSILON = 1.0
_CED_BANDS = [
    (0.5,  "LOW"),
    (1.0,  "WATCH"),
    (2.0,  "ELEVATED"),
    (1e9,  "CRITICAL"),
]


# -- XI (COHERENCE-CHAOS RATIO) ------------------------------------------------

_XI_EPSILON = 1.0

_XI_BANDS = [
    (0.3,  "STABLE"),
    (0.7,  "WATCH"),
    (1.0,  "BOUNDARY"),
    (1e9,  "CHAOS"),
]


# -- V_TOTAL COMPOSITE WEIGHTS -------------------------------------------------

_V_TOTAL_LAMBDA_R = 0.30   # Rentropy weight
_V_TOTAL_LAMBDA_B = 0.50   # Barrier Proximity weight
_V_TOTAL_NORM     = 1.0 + _V_TOTAL_LAMBDA_R + _V_TOTAL_LAMBDA_B   # 1.80


# -- TRUST HORIZON CONFIDENCE THRESHOLD ----------------------------------------

_HIGH_CONFIDENCE_MAX_V_TOTAL = 10.0   # v_total must be below this for HIGH confidence


# -- OUTPUT DATACLASS ----------------------------------------------------------

@dataclass
class HorizonMathResult:
    """
    Mathematical stability layer output for Treasurety Horizon.
    All values are heuristic indicators.
    """
    # Instability
    instability_score:  float   # 0-100; lower = stronger governance posture
    instability_vector: dict    # per-dimension z[i] = 1 - score/100

    # Boundary Condition
    barrier_status:          str    # CLEAR / WARNING / HARD_BARRIER_ACTIVE
    active_barriers:         list   # list[str] of active barrier descriptions
    barrier_proximity_score: float  # 0-100 continuous pre-barrier signal (Phi_B)

    # Resonance Pressure
    resonance_score: float   # 0-100
    resonance_label: str     # LOW / ELEVATED / HIGH / CRITICAL

    # Coherence Exhaustion Index
    ced:               float   # raw CED value
    ced_label:         str     # LOW / WATCH / ELEVATED / CRITICAL
    governance_capacity: float  # weighted composite of state vector (0-100)
    governance_stress:   float  # instability score (mirrors instability_score)

    # Rentropy -- governance failure entropy (Doc 1)
    rentropy_score: float   # 0-100; high = failure spread uniformly, hard to prioritize

    # Coherence-Chaos Ratio xi (Doc 3)
    xi:       float   # instability/(capacity+eps); xi<1 attractor, xi>1 chaos dominant
    xi_label: str     # STABLE / WATCH / BOUNDARY / CHAOS

    # V_total composite functional (Docs 1 & 2)
    v_total_score: float   # 0-100 weighted composite: V_inst + Rentropy + Phi_B

    # Drift instability (None when no historical state provided)
    instability_velocity:     Optional[float]
    instability_acceleration: Optional[float]

    # Governance Velocity Margin (Doc 2; None when no historical state provided)
    gvm:       Optional[float]   # governance_capacity - |instability_velocity|
    gvm_label: Optional[str]     # POSITIVE / MARGINAL / NEGATIVE

    # Adjusted Trust Horizon
    adjusted_trust_horizon_months: float
    trust_horizon_confidence:      str      # LOW / MODERATE / HIGH
    trust_horizon_adjustments:     list     # list[str] of applied adjustments

    def to_dict(self) -> dict:
        return asdict(self)


# -- PUBLIC ENTRY POINT --------------------------------------------------------

def compute_horizon_math(
    state:                     GovernanceStateVector,
    previous_state:            GovernanceStateVector = None,
    older_state:               GovernanceStateVector = None,
    base_trust_horizon_months: float = None,
    drift_direction:           str   = None,
) -> HorizonMathResult:
    """
    Compute the mathematical stability layer for a Horizon assessment.

    Args:
        state:                     Current GovernanceStateVector.
        previous_state:            Previous state (enables instability velocity).
        older_state:               Older state (enables instability acceleration).
        base_trust_horizon_months: Trust Horizon from the base Horizon engine.
        drift_direction:           Drift direction string (IMPROVING/STABLE/DEGRADING/RAPID_DEGRADATION).

    Returns:
        HorizonMathResult with all mathematical stability indicators.
    """
    z                   = _instability_vector(state)
    i_score             = _instability_score(z)
    barrier_status, active_barriers = _check_barriers(state)
    barrier_prox        = _barrier_proximity(state)
    resonance_score, resonance_label = _resonance(z)
    rentropy            = _rentropy(z, i_score)
    governance_capacity = state.composite()
    ced_raw, ced_label  = _ced(i_score, governance_capacity)
    xi_val, xi_label    = _xi(i_score, governance_capacity)
    v_total             = _v_total(i_score, rentropy, barrier_prox)

    vel = acc = None
    gvm_val = gvm_label_str = None
    if previous_state is not None:
        prev_z    = _instability_vector(previous_state)
        prev_inst = _instability_score(prev_z)
        vel = round(i_score - prev_inst, 3)
        gvm_val, gvm_label_str = _gvm(governance_capacity, vel)
        if older_state is not None:
            older_z    = _instability_vector(older_state)
            older_inst = _instability_score(older_z)
            acc = round(vel - (prev_inst - older_inst), 3)

    adjusted, confidence, adjustments = _adjust_trust_horizon(
        base_trust_horizon_months,
        barrier_status,
        ced_label,
        resonance_label,
        v_total,
        drift_direction,
    )

    return HorizonMathResult(
        instability_score              = round(i_score, 2),
        instability_vector             = {k: round(v, 4) for k, v in z.items()},
        barrier_status                 = barrier_status,
        active_barriers                = active_barriers,
        barrier_proximity_score        = round(barrier_prox, 2),
        resonance_score                = round(resonance_score, 2),
        resonance_label                = resonance_label,
        ced                            = round(ced_raw, 4),
        ced_label                      = ced_label,
        governance_capacity            = round(governance_capacity, 2),
        governance_stress              = round(i_score, 2),
        rentropy_score                 = round(rentropy, 2),
        xi                             = xi_val,
        xi_label                       = xi_label,
        v_total_score                  = round(v_total, 2),
        instability_velocity           = vel,
        instability_acceleration       = acc,
        gvm                            = gvm_val,
        gvm_label                      = gvm_label_str,
        adjusted_trust_horizon_months  = adjusted,
        trust_horizon_confidence       = confidence,
        trust_horizon_adjustments      = adjustments,
    )


# -- INTERNAL HELPERS ----------------------------------------------------------

def _instability_vector(state: GovernanceStateVector) -> dict:
    return {dim: max(0.0, min(1.0, 1.0 - getattr(state, dim) / 100.0))
            for dim in DIMENSION_NAMES}


def _instability_score(z: dict) -> float:
    """V_inst = z^T P z, normalized to 0-100."""
    return (sum(_P_DIAG[d] * z[d] ** 2 for d in DIMENSION_NAMES) / _P_MAX) * 100.0


def _check_barriers(state: GovernanceStateVector) -> tuple:
    active = []
    for dim in _BARRIER_DIMS:
        val = getattr(state, dim)
        if val < _HARD_BARRIER_THRESHOLD:
            active.append(
                f"{_display(dim)} below hard-stop threshold ({val:.0f} < {_HARD_BARRIER_THRESHOLD:.0f})"
            )
    if active:
        rev = getattr(state, "reversibility")
        if rev < _REVERSIBILITY_BARRIER:
            active.append(
                f"Action Reversibility critically low ({rev:.0f} < {_REVERSIBILITY_BARRIER:.0f}) -- irreversibility barrier active"
            )
        return BARRIER_HARD, active

    warn = []
    for dim in _BARRIER_DIMS:
        val = getattr(state, dim)
        if val < _WARNING_THRESHOLD:
            warn.append(
                f"{_display(dim)} approaching boundary ({val:.0f} < {_WARNING_THRESHOLD:.0f})"
            )
    rev = getattr(state, "reversibility")
    if rev < _REVERSIBILITY_BARRIER:
        warn.append(
            f"Action Reversibility below safe threshold ({rev:.0f} < {_REVERSIBILITY_BARRIER:.0f}) -- irreversibility risk"
        )
    if warn:
        return BARRIER_WARN, warn

    return BARRIER_CLEAR, []


def _barrier_proximity(state: GovernanceStateVector) -> float:
    """Barrier Proximity Score Phi_B: continuous 0-100 pre-barrier signal."""
    scores = []
    for dim in _BARRIER_DIMS:
        val = getattr(state, dim)
        prox = max(0.0, (55.0 - val) / 15.0 * 100.0)
        scores.append(min(100.0, prox))
    return max(scores) if scores else 0.0


def _resonance(z: dict) -> tuple:
    """rho = q^T R q, normalized to 0-100."""
    q = [z[d] for d in _RESONANCE_DIMS]
    rho = sum(q[i] * sum(_R[i][j] * q[j] for j in range(5)) for i in range(5))
    score = min(100.0, (rho / _R_MAX) * 100.0)
    label = next(lbl for threshold, lbl in _RESONANCE_BANDS if score < threshold)
    return score, label


def _rentropy(z: dict, i_score: float) -> float:
    """
    Rentropy: entropy of governance failure distribution, weighted by instability.
    H_normalized = -sum(p_i * log(p_i + eps)) / log(8); p_i = z_i / (sum_z + eps)
    rentropy_score = H_normalized * i_score
    High rentropy means failure is spread uniformly -- harder to prioritize remediation.
    """
    eps = 1e-9
    z_vals = [z[d] for d in DIMENSION_NAMES]
    z_sum  = sum(z_vals) + eps
    p      = [zi / z_sum for zi in z_vals]
    H      = -sum(pi * math.log(pi + eps) for pi in p) / math.log(8)
    return min(100.0, H * i_score)


def _xi(i_score: float, governance_capacity: float) -> tuple:
    """xi = instability / (capacity + eps); xi<1 attractor basin, xi>1 chaos dominant."""
    xi = i_score / (governance_capacity + _XI_EPSILON)
    label = next(lbl for threshold, lbl in _XI_BANDS if xi < threshold)
    return round(xi, 4), label


def _gvm(governance_capacity: float, instability_velocity: float) -> tuple:
    """GVM = governance_capacity - |instability_velocity|; negative = crisis propagates faster than governance responds."""
    gvm = governance_capacity - abs(instability_velocity)
    if gvm > 10.0:
        label = "POSITIVE"
    elif gvm >= -10.0:
        label = "MARGINAL"
    else:
        label = "NEGATIVE"
    return round(gvm, 3), label


def _v_total(i_score: float, rentropy_score: float, barrier_proximity_score: float) -> float:
    """V_total = (V_inst + lambda_R * Rentropy + lambda_B * Phi_B) / normalization."""
    return min(100.0, (
        i_score
        + _V_TOTAL_LAMBDA_R * rentropy_score
        + _V_TOTAL_LAMBDA_B * barrier_proximity_score
    ) / _V_TOTAL_NORM)


def _ced(stress: float, capacity: float) -> tuple:
    """CED = governance_stress / (governance_capacity + epsilon)."""
    ced = stress / (capacity + _CED_EPSILON)
    label = next(lbl for threshold, lbl in _CED_BANDS if ced < threshold)
    return ced, label


def _adjust_trust_horizon(
    base:            Optional[float],
    barrier_status:  str,
    ced_label:       str,
    resonance_label: str,
    v_total_score:   float,
    drift_direction: Optional[str],
) -> tuple:
    if base is None:
        base = 6.0

    months = base
    adjustments: list[str] = []

    if barrier_status == BARRIER_HARD:
        months = min(months, 1.0)
        adjustments.append("Hard boundary condition active: Trust Horizon capped at 1 month")

    if ced_label == "CRITICAL":
        months -= 4.0
        adjustments.append("Coherence Exhaustion critical: -4 months")

    if resonance_label in ("HIGH", "CRITICAL"):
        months -= 3.0
        adjustments.append(f"Resonance Pressure {resonance_label}: -3 months")

    if drift_direction == DRIFT_RAPID_DEGRADATION:
        months -= 5.0
        adjustments.append("Rapid governance degradation: -5 months")
    elif drift_direction == DRIFT_DEGRADING:
        months -= 2.0
        adjustments.append("Active governance degradation: -2 months")

    if v_total_score < _HIGH_CONFIDENCE_MAX_V_TOTAL and barrier_status == BARRIER_CLEAR:
        months = max(months, base)
        adjustments.append("Low instability with clear boundaries: base estimate preserved")

    months = round(max(0.0, min(24.0, months)), 1)

    if barrier_status == BARRIER_HARD or ced_label == "CRITICAL":
        confidence = "LOW"
    elif (barrier_status == BARRIER_WARN or
          ced_label in ("ELEVATED", "WATCH") or
          resonance_label in ("HIGH", "CRITICAL") or
          v_total_score >= _HIGH_CONFIDENCE_MAX_V_TOTAL):
        confidence = "MODERATE"
    else:
        confidence = "HIGH"

    if not adjustments:
        adjustments.append("No adjustments applied -- base estimate preserved")

    return months, confidence, adjustments


_DISPLAY_NAMES = {
    "authority":               "Authority Boundary",
    "scope":                   "Operational Scope",
    "observability":           "System Observability",
    "intervention_capability": "Intervention Capability",
    "accountability":          "Accountability Controls",
    "reversibility":           "Action Reversibility",
    "exception_control":       "Exception Handling",
    "drift_monitoring":        "Drift Monitoring",
}

def _display(dim: str) -> str:
    return _DISPLAY_NAMES.get(dim, dim)
