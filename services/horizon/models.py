"""
Treasurety Horizon — Data Models
All dataclasses, enums, and constants for the Horizon engine.

Internal note: "attractor" language refers to TASA (Trusted Autonomous System Attractor).
Customer-facing language uses "Governance Stability Zone" and "Attractor Membership."
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


# ── DIMENSION CONSTANTS ────────────────────────────────────────────────────────

DIMENSION_NAMES = [
    "authority",
    "scope",
    "observability",
    "intervention_capability",
    "accountability",
    "reversibility",
    "exception_control",
    "drift_monitoring",
]

# Weights must sum to 1.0
DEFAULT_DIMENSION_WEIGHTS = {
    "authority":               0.20,
    "scope":                   0.10,
    "observability":           0.18,
    "intervention_capability": 0.18,
    "accountability":          0.14,
    "reversibility":           0.12,
    "exception_control":       0.05,
    "drift_monitoring":        0.03,
}

# Dimensions where low scores carry the highest governance risk
CRITICAL_DIMENSIONS = ["authority", "observability", "intervention_capability"]

# Customer-facing display labels
DIMENSION_DISPLAY_NAMES = {
    "authority":               "Authority Boundary",
    "scope":                   "Operational Scope",
    "observability":           "System Observability",
    "intervention_capability": "Intervention Capability",
    "accountability":          "Accountability Controls",
    "reversibility":           "Action Reversibility",
    "exception_control":       "Exception Handling",
    "drift_monitoring":        "Drift Monitoring",
}


# ── ATTRACTOR STATUS CONSTANTS ─────────────────────────────────────────────────
# Internal: TASA membership zones. Customer-facing: Attractor Membership.

ATTRACTOR_MEMBER    = "ATTRACTOR_MEMBER"    # Inside governance stability zone
NEAR_BOUNDARY       = "NEAR_BOUNDARY"       # Approaching governance boundary
OUTSIDE_ATTRACTOR   = "OUTSIDE_ATTRACTOR"   # Outside governance stability zone
CRITICAL_DRIFT      = "CRITICAL_DRIFT"      # Critical governance drift detected

ATTRACTOR_STATUS_LABELS = {
    ATTRACTOR_MEMBER:  "Within Governance Stability Zone",
    NEAR_BOUNDARY:     "Approaching Governance Boundary",
    OUTSIDE_ATTRACTOR: "Outside Governance Stability Zone",
    CRITICAL_DRIFT:    "Critical Governance Drift Detected",
}

# Composite score thresholds (TASA boundary definitions)
ATTRACTOR_INNER_BOUNDARY = 65.0   # Composite >= 65 → inside attractor
ATTRACTOR_OUTER_BOUNDARY = 50.0   # Composite >= 50 → near boundary
ATTRACTOR_CENTER_TARGET  = 80.0   # Ideal composite score
CRITICAL_COMPOSITE_FLOOR = 30.0   # Composite < 30 → critical drift
CRITICAL_DIM_FLOOR       = 20.0   # Any critical dim < 20 → critical drift
OUTSIDE_CRITICAL_DIM     = 35.0   # Any critical dim < 35 → outside attractor
BOUNDARY_CRITICAL_DIM    = 50.0   # Any critical dim < 50 → near boundary


# ── STABILITY LABEL CONSTANTS ──────────────────────────────────────────────────

STABILITY_STABLE   = "stable"
STABILITY_WATCH    = "watch"
STABILITY_UNSTABLE = "unstable"
STABILITY_CRITICAL = "critical"

STABILITY_THRESHOLDS = {
    STABILITY_STABLE:   75.0,
    STABILITY_WATCH:    50.0,
    STABILITY_UNSTABLE: 30.0,
}


# ── DRIFT DIRECTION CONSTANTS ──────────────────────────────────────────────────

DRIFT_IMPROVING          = "IMPROVING"
DRIFT_STABLE             = "STABLE"
DRIFT_DEGRADING          = "DEGRADING"
DRIFT_RAPID_DEGRADATION  = "RAPID_DEGRADATION"

DRIFT_VELOCITY_IMPROVING_THRESHOLD   =  3.0   # composite points per cycle
DRIFT_VELOCITY_DEGRADING_THRESHOLD   = -3.0
DRIFT_ACCELERATION_CRITICAL_THRESHOLD = -5.0  # velocity worsening by > 5 pts/cycle


# ── TRUST HORIZON LABEL CONSTANTS ─────────────────────────────────────────────

HORIZON_STABLE  = "Stable Horizon"
HORIZON_WATCH   = "Watch Horizon"
HORIZON_URGENT  = "Urgent Horizon"
HORIZON_EXPIRED = "Expired Horizon"

HORIZON_STABLE_MONTHS  = 9.0
HORIZON_WATCH_MONTHS   = 4.0
HORIZON_URGENT_MONTHS  = 1.0

HORIZON_CONFIDENCE = "Heuristic estimate"


# ── DATA CLASSES ───────────────────────────────────────────────────────────────

@dataclass
class GovernanceStateVector:
    """
    Eight-dimensional governance state vector. All values normalized 0–100.
    Higher = stronger governance posture in that dimension.
    """
    authority:               float  # Degree to which authority scope is bounded
    scope:                   float  # Clarity and enforcement of operational boundaries
    observability:           float  # Ability to observe all system actions
    intervention_capability: float  # Speed and reliability of human intervention
    accountability:          float  # Audit completeness and responsibility attribution
    reversibility:           float  # Ability to undo or roll back system actions
    exception_control:       float  # Quality of exception handling and graceful degradation
    drift_monitoring:        float  # Active monitoring of governance posture changes

    def composite(self, weights: dict = None) -> float:
        w = weights or DEFAULT_DIMENSION_WEIGHTS
        return sum(getattr(self, dim) * w.get(dim, 0.125) for dim in DIMENSION_NAMES)

    def as_dict(self) -> dict:
        return {dim: getattr(self, dim) for dim in DIMENSION_NAMES}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AttractorResult:
    """
    TASA membership analysis result.
    Customer-facing: Attractor Membership / Governance Stability Zone.
    """
    membership_status:      str    # ATTRACTOR_MEMBER / NEAR_BOUNDARY / OUTSIDE_ATTRACTOR / CRITICAL_DRIFT
    distance_from_center:   float  # 0–100; 0 = ideal, 100 = worst possible
    distance_from_boundary: float  # positive = inside zone, negative = outside zone
    composite_score:        float  # weighted composite of all dimensions

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StabilityResult:
    """Governance stability scoring result."""
    stability_score:      float       # 0–100 weighted composite
    stability_label:      str         # stable / watch / unstable / critical
    dimension_scores:     dict        # weighted contribution per dimension
    weakest_dimensions:   list        # dimension names sorted ascending by raw score (weakest first)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DriftResult:
    """Governance drift analysis result."""
    governance_velocity:            float          # composite change per cycle (positive = improving)
    governance_acceleration:        float          # change in velocity (positive = improving faster)
    drift_direction:                str            # IMPROVING / STABLE / DEGRADING / RAPID_DEGRADATION
    dimension_deltas:               dict           # per-dimension score change
    largest_degradation_dimension:  Optional[str]  # dimension with largest negative delta

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrustHorizonResult:
    """
    Trust Horizon estimation.
    All estimates are heuristic and MUST be presented as such.
    """
    trust_horizon_months: float  # estimated months of governance stability
    horizon_label:        str    # Stable / Watch / Urgent / Expired Horizon
    confidence:           str    # always HORIZON_CONFIDENCE = "Heuristic estimate"
    primary_risk_factor:  str    # human-readable description of primary risk
    horizon_factors:      dict   # breakdown of calculation inputs

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CorrectiveAction:
    """A prioritized corrective governance action."""
    priority:           int   # 1 = highest
    dimension:          str   # internal dimension name
    display_dimension:  str   # customer-facing display name
    action:             str   # specific actionable recommendation
    expected_impact:    str   # HIGH / MEDIUM / LOW

    def to_dict(self) -> dict:
        return asdict(self)


# ── DASHBOARD SUMMARY OBJECTS ──────────────────────────────────────────────────

@dataclass
class AttractorSummary:
    """Dashboard-ready attractor membership summary."""
    membership_status:      str
    membership_label:       str   # human-readable customer-facing label
    distance_from_center:   float
    distance_from_boundary: float
    boundary_threshold:     int   # composite score defining the outer boundary (50)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrustHorizonSummary:
    """Dashboard-ready Trust Horizon summary."""
    trust_horizon_months: float
    horizon_label:        str
    confidence:           str
    primary_risk_factor:  str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GovernanceTrajectorySummary:
    """Dashboard-ready governance trajectory summary."""
    current_stability:      float
    stability_label:        str
    drift_direction:        str
    governance_velocity:    float
    governance_acceleration: float
    top_drift_factor:       str   # customer-facing display name of most degrading dimension
    trend_label:            str   # human-readable trend sentence

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class HorizonResult:
    """
    Complete Treasurety Horizon evaluation result.

    Flat monitor integration fields are exposed at the top level for direct
    metric extraction by Treasurety Monitor.

    Dashboard summary objects (attractor_summary, trust_horizon_summary,
    trajectory_summary) are JSON-serializable and suitable for UI rendering.
    """
    # ── Monitor integration fields (flat) ─────────────────────────────────────
    horizon_membership:      str    # ATTRACTOR_MEMBER / NEAR_BOUNDARY / etc.
    horizon_stability:       float  # 0–100 stability score
    trust_horizon_months:    float  # estimated months of governance stability
    governance_velocity:     float  # composite drift per cycle
    governance_acceleration: float  # velocity change per cycle
    boundary_distance:       float  # positive = inside zone, negative = outside
    top_drift_factor:        str    # internal name of most degrading dimension

    # ── Full sub-results ───────────────────────────────────────────────────────
    state_vector:       GovernanceStateVector
    attractor:          AttractorResult
    stability:          StabilityResult
    drift:              DriftResult
    trust_horizon:      TrustHorizonResult
    corrective_actions: list  # list[CorrectiveAction]

    # ── Dashboard objects ──────────────────────────────────────────────────────
    attractor_summary:       AttractorSummary
    trust_horizon_summary:   TrustHorizonSummary
    trajectory_summary:      GovernanceTrajectorySummary

    # ── Metadata ───────────────────────────────────────────────────────────────
    evaluated_at:     str   # ISO 8601 UTC
    horizon_version:  str   # "1.0"

    def to_dict(self) -> dict:
        return asdict(self)
