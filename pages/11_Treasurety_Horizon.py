import streamlit as st
import plotly.graph_objects as go
from services import branding
from services.horizon import evaluate_horizon_from_monitor_scenario
from services.horizon.state_vector import from_monitor_scenario
from services.horizon_math import compute_horizon_math

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_nav()

# ── SCENARIO DATA (mirrors Monitor for cross-page consistency) ─────────────────

SCENARIOS = {
    "Stable Agent — Procurement Automation": {
        "system_name":           "ProcureBot AI",
        "domain":                "Supply Chain",
        "agent_type":            "Single agent",
        "description":           "An autonomous procurement agent operating within defined governance parameters. All drift dimensions within acceptable bounds. Continuous monitoring confirms stable execution.",
        "policy_drift":          8,
        "behavioral_drift":      6,
        "trust_drift":           10,
        "ecosystem_drift":       12,
        "intervention_drift":    7,
        "governance_stability":  93,
        "trust_integrity":       91,
        "escalation_trend_pct":  -8,
        "intervention_burden":   6,
        "policy_exception_rate": 4,
        "trend_history": [88, 90, 91, 91, 92, 93, 92, 93, 94, 93, 93, 93],
    },
    "Moderate Drift — Finance Automation": {
        "system_name":           "FinFlow Agent",
        "domain":                "Financial Services",
        "agent_type":            "Multi-agent",
        "description":           "A finance automation agent showing early signs of policy boundary pressure and increasing behavioral variance. Governance review recommended before further expansion.",
        "policy_drift":          42,
        "behavioral_drift":      38,
        "trust_drift":           22,
        "ecosystem_drift":       18,
        "intervention_drift":    35,
        "governance_stability":  64,
        "trust_integrity":       71,
        "escalation_trend_pct":  28,
        "intervention_burden":   31,
        "policy_exception_rate": 22,
        "trend_history": [84, 82, 80, 79, 77, 74, 73, 70, 68, 66, 65, 64],
    },
    "Third-Party Degradation — Orchestration Agent": {
        "system_name":           "IntegrationOrch AI",
        "domain":                "IT & Infrastructure",
        "agent_type":            "Orchestrated agent fleet",
        "description":           "An orchestration agent with significant third-party API and vendor trust deterioration. Internal behavior stable but external trust surface compromised.",
        "policy_drift":          18,
        "behavioral_drift":      24,
        "trust_drift":           68,
        "ecosystem_drift":       76,
        "intervention_drift":    30,
        "governance_stability":  58,
        "trust_integrity":       42,
        "escalation_trend_pct":  45,
        "intervention_burden":   27,
        "policy_exception_rate": 19,
        "trend_history": [85, 84, 82, 79, 74, 70, 66, 63, 61, 59, 58, 58],
    },
    "Escalation Spike — Multi-Agent Pipeline": {
        "system_name":           "PipelineOps Multi-Agent",
        "domain":                "Operations",
        "agent_type":            "Agentic pipeline",
        "description":           "A multi-agent pipeline experiencing rapid growth in human escalation requests and intervention burden. Policy miscalibration causing governance strain.",
        "policy_drift":          58,
        "behavioral_drift":      52,
        "trust_drift":           40,
        "ecosystem_drift":       28,
        "intervention_drift":    84,
        "governance_stability":  44,
        "trust_integrity":       55,
        "escalation_trend_pct":  67,
        "intervention_burden":   72,
        "policy_exception_rate": 48,
        "trend_history": [81, 78, 74, 69, 64, 60, 56, 52, 49, 46, 45, 44],
    },
    "Critical Instability — High-Autonomy Agent": {
        "system_name":           "AutonomousExec AI",
        "domain":                "Financial Services",
        "agent_type":            "Multi-agent",
        "description":           "A high-autonomy execution agent with multiple converging drift signals indicating critical governance degradation. Immediate execution restriction recommended.",
        "policy_drift":          82,
        "behavioral_drift":      78,
        "trust_drift":           74,
        "ecosystem_drift":       71,
        "intervention_drift":    88,
        "governance_stability":  22,
        "trust_integrity":       28,
        "escalation_trend_pct":  112,
        "intervention_burden":   85,
        "policy_exception_rate": 74,
        "trend_history": [76, 71, 65, 59, 53, 46, 41, 36, 32, 28, 24, 22],
    },
}


def _make_previous_scenario(scenario: dict):
    h = scenario.get("trend_history", [])
    if len(h) < 2:
        return None
    prev_stability = sum(h[-4:-1]) / 3 if len(h) >= 4 else h[-2]
    delta = h[-1] - prev_stability
    _SKIP         = {"system_name", "domain", "agent_type", "description", "trend_history"}
    _STABILITY_KS = {"governance_stability", "trust_integrity"}
    prev = {}
    for k, v in scenario.items():
        if k in _SKIP:
            prev[k] = v
        elif k in _STABILITY_KS and isinstance(v, (int, float)):
            prev[k] = max(0.0, min(100.0, v - delta))
        elif isinstance(v, (int, float)):
            prev[k] = max(0.0, min(100.0, v + delta * 0.7))
        else:
            prev[k] = v
    return prev


# ── COLOR HELPERS ─────────────────────────────────────────────────────────────

_MEMBERSHIP_COLORS = {
    "ATTRACTOR_MEMBER":  "#16a34a",
    "NEAR_BOUNDARY":     "#f59e0b",
    "OUTSIDE_ATTRACTOR": "#ea580c",
    "CRITICAL_DRIFT":    "#dc2626",
}
_MEMBERSHIP_SHORT = {
    "ATTRACTOR_MEMBER":  "IN ZONE",
    "NEAR_BOUNDARY":     "NEAR BOUNDARY",
    "OUTSIDE_ATTRACTOR": "OUTSIDE ZONE",
    "CRITICAL_DRIFT":    "CRITICAL DRIFT",
}
_HORIZON_COLORS = {
    "Stable Horizon":  "#16a34a",
    "Watch Horizon":   "#f59e0b",
    "Urgent Horizon":  "#ea580c",
    "Expired Horizon": "#dc2626",
}
_STABILITY_COLORS = {
    "stable":   "#16a34a",
    "watch":    "#f59e0b",
    "unstable": "#ea580c",
    "critical": "#dc2626",
}
_DRIFT_COLORS = {
    "IMPROVING":         "#16a34a",
    "STABLE":            "#06b6d4",
    "DEGRADING":         "#f59e0b",
    "RAPID_DEGRADATION": "#dc2626",
}
_IMPACT_COLORS   = {"HIGH": "#dc2626", "MEDIUM": "#f59e0b", "LOW": "#16a34a"}
_BARRIER_COLORS  = {"CLEAR": "#16a34a", "WARNING": "#f59e0b", "HARD_BARRIER_ACTIVE": "#dc2626"}
_RESONANCE_COLORS = {"LOW": "#16a34a", "ELEVATED": "#f59e0b", "HIGH": "#ea580c", "CRITICAL": "#dc2626"}
_CED_COLORS      = {"LOW": "#16a34a", "WATCH": "#06b6d4", "ELEVATED": "#f59e0b", "CRITICAL": "#dc2626"}
_CONF_COLORS     = {"HIGH": "#16a34a", "MODERATE": "#f59e0b", "LOW": "#dc2626"}
_XI_COLORS       = {"STABLE": "#16a34a", "WATCH": "#06b6d4", "BOUNDARY": "#f59e0b", "CHAOS": "#dc2626"}
_GVM_COLORS      = {"POSITIVE": "#16a34a", "MARGINAL": "#f59e0b", "NEGATIVE": "#dc2626"}


def _instability_color(score: float) -> str:
    if score < 15: return "#16a34a"
    if score < 35: return "#f59e0b"
    if score < 60: return "#ea580c"
    return "#dc2626"


def _metric_card(label: str, value: str, sub: str, color: str, min_height: str = "110px") -> str:
    return (
        f'<div style="background:#0f172a;border:1px solid {color}33;'
        f'border-top:3px solid {color};border-radius:12px;padding:20px;'
        f'text-align:center;min-height:{min_height};">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:10px;">{label}</div>'
        f'<div style="color:{color};font-size:1.8rem;font-weight:800;margin-bottom:6px;">{value}</div>'
        f'<div style="color:#64748b;font-size:0.75rem;">{sub}</div>'
        f'</div>'
    )


def _small_metric_card(label: str, value: str, unit: str, color: str) -> str:
    return (
        f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;'
        f'padding:16px;text-align:center;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;margin-bottom:8px;">{label}</div>'
        f'<div style="color:{color};font-size:1.2rem;font-weight:800;">{value}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;margin-top:2px;">{unit}</div>'
        f'</div>'
    )


def _section_divider(label: str) -> str:
    return (
        '<div style="display:flex;align-items:center;gap:16px;margin:32px 0 18px 0;">'
        '<div style="flex:1;height:1px;background:linear-gradient(to right,'
        'rgba(144,211,255,0.3),transparent);"></div>'
        f'<span style="background:rgba(144,211,255,0.08);color:#90d3ff;font-size:0.68rem;'
        f'font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:5px 18px;'
        f'border-radius:999px;border:1px solid rgba(144,211,255,0.2);">{label}</span>'
        '<div style="flex:1;height:1px;background:linear-gradient(to left,'
        'rgba(144,211,255,0.3),transparent);"></div>'
        '</div>'
    )


# ── HEADER ────────────────────────────────────────────────────────────────────

st.image("assets/logo.png", width=240)

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(144,211,255,0.1);color:#90d3ff;font-size:0.72rem;font-weight:700;'
    'letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;'
    'border:1px solid rgba(144,211,255,0.2);">TREASURETY HORIZON</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Governance Dynamics & Trust Horizon Intelligence")
st.caption(
    "Treasurety Horizon analyzes governance trajectory, stability, drift pressure, "
    "and trust sustainability over time. Monitor tells you what is happening now. "
    "Horizon tells you where governance is going."
)

col_title, col_scenario = st.columns([3, 2])
with col_scenario:
    scenario_name = st.selectbox(
        "Active System",
        list(SCENARIOS.keys()),
        help="Select a governance scenario to analyze"
    )

st.markdown("---")

# ── COMPUTE ALL OUTPUTS ───────────────────────────────────────────────────────

s           = SCENARIOS[scenario_name]
horizon     = evaluate_horizon_from_monitor_scenario(s, _make_previous_scenario(s))
_prev_scen  = _make_previous_scenario(s)
_prev_sv    = from_monitor_scenario(_prev_scen) if _prev_scen is not None else None
hm          = compute_horizon_math(
    state                     = horizon.state_vector,
    previous_state            = _prev_sv,
    base_trust_horizon_months = horizon.trust_horizon_months,
    drift_direction           = horizon.drift.drift_direction,
)

m_color = _MEMBERSHIP_COLORS.get(horizon.horizon_membership, "#64748b")
h_color = _HORIZON_COLORS.get(horizon.trust_horizon.horizon_label, "#64748b")
s_color = _STABILITY_COLORS.get(horizon.stability.stability_label, "#64748b")
d_color = _DRIFT_COLORS.get(horizon.drift.drift_direction, "#64748b")

vel      = horizon.governance_velocity
acc      = horizon.governance_acceleration
vel_sign = "+" if vel >= 0 else ""
acc_sign = "+" if acc >= 0 else ""
vel_arrow = "↑" if vel > 0.5 else ("↓" if vel < -0.5 else "→")

th_months  = horizon.trust_horizon_months
th_display = f"{th_months:.1f} mo" if th_months >= 0.1 else "< 0.1 mo"

top_factor = horizon.trajectory_summary.top_drift_factor
if top_factor == "none":
    top_factor = "None detected"

# System badge
st.markdown(
    f'<div style="background:#0a0f1e;border-left:4px solid #90d3ff;padding:14px 18px;'
    f'border-radius:8px;margin-bottom:24px;color:#94a3b8;font-size:0.88rem;">'
    f'<strong style="color:#90d3ff;">{s["system_name"]}</strong>'
    f'&nbsp;&nbsp;&middot;&nbsp;&nbsp;{s["domain"]}&nbsp;&nbsp;&middot;&nbsp;&nbsp;{s["agent_type"]}<br>'
    f'<em>{s["description"]}</em>'
    f'</div>',
    unsafe_allow_html=True
)


# ── SECTION 1: HORIZON EXECUTIVE SUMMARY ─────────────────────────────────────

st.markdown(_section_divider("HORIZON EXECUTIVE SUMMARY"), unsafe_allow_html=True)
st.markdown("#### Governance Posture at a Glance")

ex_c1, ex_c2, ex_c3, ex_c4 = st.columns(4)

with ex_c1:
    st.markdown(
        _metric_card(
            "ATTRACTOR MEMBERSHIP",
            _MEMBERSHIP_SHORT.get(horizon.horizon_membership, horizon.horizon_membership),
            f"Stability score: {horizon.horizon_stability:.0f}/100",
            m_color,
        ),
        unsafe_allow_html=True
    )

with ex_c2:
    st.markdown(
        _metric_card(
            "GOVERNANCE STABILITY",
            f"{horizon.horizon_stability:.0f}",
            horizon.stability.stability_label.upper(),
            s_color,
        ),
        unsafe_allow_html=True
    )

with ex_c3:
    st.markdown(
        _metric_card(
            "TRUST HORIZON",
            th_display,
            horizon.trust_horizon.horizon_label,
            h_color,
        ),
        unsafe_allow_html=True
    )

with ex_c4:
    st.markdown(
        _metric_card(
            "GOVERNANCE DRIFT",
            f"{vel_arrow} {vel_sign}{vel:.1f}",
            horizon.drift.drift_direction.replace("_", " "),
            d_color,
        ),
        unsafe_allow_html=True
    )


# ── SECTION 2: GOVERNANCE DYNAMICS ───────────────────────────────────────────

st.markdown(_section_divider("GOVERNANCE DYNAMICS"), unsafe_allow_html=True)
st.markdown("#### Trajectory & Velocity Indicators")

_conf_col = _CONF_COLORS.get(hm.trust_horizon_confidence, "#64748b")
_xi_col   = _XI_COLORS.get(hm.xi_label, "#64748b")
_gvm_col  = _GVM_COLORS.get(hm.gvm_label, "#64748b") if hm.gvm_label else "#64748b"
_gvm_disp = f"{hm.gvm:+.1f}" if hm.gvm is not None else "N/A"
_gvm_lbl  = hm.gvm_label or "No prior state"
_acc_color = "#16a34a" if acc >= 0 else "#f59e0b"

dyn_c1, dyn_c2, dyn_c3, dyn_c4, dyn_c5 = st.columns(5)

dyn_items = [
    ("GOVERNANCE VELOCITY",     f"{vel_sign}{vel:.2f}",  "pts / cycle",           d_color),
    ("GOVERNANCE ACCELERATION", f"{acc_sign}{acc:.2f}",  "velocity change / cycle", _acc_color),
    ("COHERENCE-CHAOS RATIO",   f"ξ {hm.xi:.3f}",  hm.xi_label,             _xi_col),
    ("VELOCITY MARGIN",         _gvm_disp,               _gvm_lbl,                _gvm_col),
    ("DRIFT DIRECTION",
     horizon.drift.drift_direction.replace("_", " "),
     f"Boundary: {'+' if horizon.boundary_distance >= 0 else ''}{horizon.boundary_distance:.1f} pts",
     d_color),
]

for col, (label, value, unit, color) in zip(
    [dyn_c1, dyn_c2, dyn_c3, dyn_c4, dyn_c5], dyn_items
):
    with col:
        st.markdown(_small_metric_card(label, value, unit, color), unsafe_allow_html=True)


# ── SECTION 3: GOVERNANCE STATE ANALYSIS ─────────────────────────────────────

st.markdown(_section_divider("GOVERNANCE STATE ANALYSIS"), unsafe_allow_html=True)
st.markdown("#### Governance State Vector")
st.caption(
    "Eight governance dimensions mapped against the stability zone (inner) and outer boundary. "
    "Higher scores reflect stronger governance posture. All scores 0-100."
)

sv = horizon.state_vector
sv_labels = ["Authority", "Scope", "Observability", "Intervention",
             "Accountability", "Reversibility", "Exceptions", "Drift Mon."]
sv_values = [sv.authority, sv.scope, sv.observability, sv.intervention_capability,
             sv.accountability, sv.reversibility, sv.exception_control, sv.drift_monitoring]
sv_cats   = sv_labels + [sv_labels[0]]
sv_vals   = sv_values + [sv_values[0]]
n         = len(sv_labels) + 1

fig_sv = go.Figure()
fig_sv.add_trace(go.Scatterpolar(
    r=[65] * n, theta=sv_cats, fill="toself",
    fillcolor="rgba(22,163,74,0.06)",
    line=dict(color="#16a34a", width=1, dash="dot"),
    name="Stability Zone (65)", hoverinfo="skip",
))
fig_sv.add_trace(go.Scatterpolar(
    r=[50] * n, theta=sv_cats, fill="toself",
    fillcolor="rgba(234,88,12,0.05)",
    line=dict(color="#ea580c", width=1, dash="dot"),
    name="Outer Boundary (50)", hoverinfo="skip",
))
fig_sv.add_trace(go.Scatterpolar(
    r=sv_vals, theta=sv_cats, fill="toself",
    fillcolor="rgba(144,211,255,0.1)",
    line=dict(color="#90d3ff", width=2.5),
    name="Governance State",
))
fig_sv.update_layout(
    polar=dict(
        bgcolor="rgba(10,15,30,0.9)",
        radialaxis=dict(
            visible=True, range=[0, 100],
            tickfont=dict(color="#64748b", size=9),
            gridcolor="rgba(255,255,255,0.07)",
            linecolor="rgba(255,255,255,0.07)",
        ),
        angularaxis=dict(
            tickfont=dict(color="#90d3ff", size=11),
            gridcolor="rgba(255,255,255,0.07)",
            linecolor="rgba(255,255,255,0.07)",
        ),
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=True,
    legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=30, b=30, l=30, r=30),
    height=420,
)
st.plotly_chart(fig_sv, use_container_width=True)

# Dimension detail table
dim_rows = list(zip(
    ["Authority", "Scope", "Observability", "Intervention Capability",
     "Accountability", "Reversibility", "Exception Control", "Drift Monitoring"],
    sv_values
))
dim_html = ""
for dim_name, score in dim_rows:
    bar_color = "#16a34a" if score >= 65 else ("#f59e0b" if score >= 50 else "#dc2626")
    pct = int(score)
    dim_html += (
        f'<div style="display:flex;align-items:center;gap:12px;padding:6px 0;'
        f'border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="color:#94a3b8;font-size:0.82rem;width:180px;flex-shrink:0;">{dim_name}</span>'
        f'<div style="flex:1;background:#1e293b;border-radius:999px;height:5px;">'
        f'<div style="background:{bar_color};width:{pct}%;height:5px;border-radius:999px;"></div></div>'
        f'<span style="color:{bar_color};font-size:0.82rem;font-weight:700;width:36px;text-align:right;">{score:.0f}</span>'
        f'</div>'
    )
st.markdown(
    f'<div style="background:#0a0f1e;border:1px solid rgba(144,211,255,0.1);'
    f'border-radius:12px;padding:20px 24px;margin-top:12px;">'
    f'<div style="color:#64748b;font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
    f'text-transform:uppercase;margin-bottom:12px;">Dimension Detail (0-100, higher = stronger)</div>'
    + dim_html +
    '</div>',
    unsafe_allow_html=True
)


# ── SECTION 4: TRUST HORIZON INTELLIGENCE ────────────────────────────────────

st.markdown(_section_divider("TRUST HORIZON INTELLIGENCE"), unsafe_allow_html=True)
st.markdown("#### Trust Sustainability Analysis")
st.caption("Heuristic estimate of how long current governance conditions can sustain trust. Pending longitudinal calibration.")

th_left, th_right = st.columns([1, 1])

with th_left:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=min(th_months, 24.0),
        number=dict(suffix=" mo", font=dict(size=42, color=h_color)),
        gauge=dict(
            axis=dict(range=[0, 24], tickfont=dict(color="#64748b", size=9)),
            bar=dict(color=h_color, thickness=0.35),
            bgcolor="rgba(10,15,30,1)",
            borderwidth=0,
            steps=[
                dict(range=[0,  1],  color="rgba(220,38,38,0.25)"),
                dict(range=[1,  4],  color="rgba(234,88,12,0.2)"),
                dict(range=[4,  9],  color="rgba(245,158,11,0.18)"),
                dict(range=[9, 24],  color="rgba(22,163,74,0.15)"),
            ],
            threshold=dict(line=dict(color="#16a34a", width=2), thickness=0.75, value=9),
        ),
        title=dict(
            text=horizon.trust_horizon.horizon_label,
            font=dict(color="#94a3b8", size=14),
        ),
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        height=300,
        margin=dict(t=60, b=10, l=40, r=40),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with th_right:
    _adj_display = f"{hm.adjusted_trust_horizon_months:.1f} mo"
    th_detail_items = [
        ("Trust Horizon (Base)",       th_display,              h_color),
        ("Trust Horizon (Adjusted)",   _adj_display,            _conf_col),
        ("Confidence",                 hm.trust_horizon_confidence, _conf_col),
        ("Boundary Distance",
         f"{'+' if horizon.boundary_distance >= 0 else ''}{horizon.boundary_distance:.1f} pts",
         m_color),
        ("Primary Drift Factor",       top_factor,              "#90d3ff"),
        ("Drift Direction",
         horizon.drift.drift_direction.replace("_", " "),
         d_color),
    ]
    detail_html = ""
    for label, val, color in th_detail_items:
        detail_html += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
            f'<span style="color:#64748b;font-size:0.83rem;">{label}</span>'
            f'<span style="color:{color};font-size:0.83rem;font-weight:700;">{val}</span>'
            f'</div>'
        )
    st.markdown(
        '<div style="background:#0a0f1e;border:1px solid rgba(144,211,255,0.1);'
        'border-radius:12px;padding:20px 24px;margin-bottom:12px;">'
        '<div style="color:#64748b;font-size:0.72rem;font-weight:700;letter-spacing:0.1em;'
        'text-transform:uppercase;margin-bottom:10px;">Trust Horizon Detail</div>'
        + detail_html +
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div style="background:#0a0f1e;border:1px solid rgba(144,211,255,0.1);'
        f'border-radius:10px;padding:14px 16px;">'
        f'<div style="color:#90d3ff;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;'
        f'margin-bottom:5px;">PRIMARY RISK FACTOR</div>'
        f'<div style="color:#cbd5e1;font-size:0.85rem;line-height:1.5;">'
        f'{horizon.trust_horizon.primary_risk_factor}</div>'
        f'<div style="color:#334155;font-size:0.7rem;margin-top:6px;font-style:italic;">'
        f'Heuristic estimate &middot; {horizon.trust_horizon.confidence}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Adjustments applied
    _non_default = [a for a in hm.trust_horizon_adjustments
                    if a != "No adjustments applied -- base estimate preserved"]
    if _non_default:
        st.markdown(
            '<p style="color:#64748b;font-size:0.78rem;margin:14px 0 6px 0;font-weight:600;">'
            'Adjustments Applied</p>',
            unsafe_allow_html=True
        )
        for adj in _non_default:
            st.markdown(
                f'<div style="background:#0a0a18;border-left:2px solid rgba(144,211,255,0.3);'
                f'padding:7px 14px;border-radius:4px;margin-bottom:4px;">'
                f'<span style="color:#90d3ff;font-size:0.8rem;">{adj}</span>'
                f'</div>',
                unsafe_allow_html=True
            )


# ── SECTION 5: MATHEMATICAL STABILITY LAYER ──────────────────────────────────

st.markdown(_section_divider("MATHEMATICAL STABILITY LAYER"), unsafe_allow_html=True)
st.markdown("#### Stability Intelligence")
st.caption(
    "Quantitative stability indicators computed from the governance state vector. "
    "All values are heuristic estimates pending longitudinal calibration."
)

_inst_col = _instability_color(hm.instability_score)
_bar_col  = _BARRIER_COLORS.get(hm.barrier_status, "#64748b")
_res_col  = _RESONANCE_COLORS.get(hm.resonance_label, "#64748b")
_ced_col  = _CED_COLORS.get(hm.ced_label, "#64748b")
_vtot_col = _instability_color(hm.v_total_score)
_rent_col = _instability_color(hm.rentropy_score)
_bar_prox_col = _instability_color(hm.barrier_proximity_score)

_barrier_display = hm.barrier_status.replace("_", " ")
_barrier_detail  = (
    f"{len(hm.active_barriers)} active {'barrier' if len(hm.active_barriers) == 1 else 'barriers'}"
    if hm.active_barriers else "All boundaries nominal"
)

# Row 1: primary stability metrics
ms_c1, ms_c2, ms_c3, ms_c4 = st.columns(4)

with ms_c1:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_inst_col}33;'
        f'border-top:3px solid {_inst_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">INSTABILITY SCORE</div>'
        f'<div style="color:{_inst_col};font-size:2.2rem;font-weight:800;margin-bottom:4px;">{hm.instability_score:.0f}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">/ 100 &nbsp;&middot;&nbsp; posture risk</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">Lower is stronger</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with ms_c2:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_bar_col}33;'
        f'border-top:3px solid {_bar_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">BOUNDARY CONDITION</div>'
        f'<div style="color:{_bar_col};font-size:0.9rem;font-weight:800;margin-bottom:4px;">{_barrier_display}</div>'
        f'<div style="color:#64748b;font-size:0.7rem;line-height:1.5;">{_barrier_detail}</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">Proximity: {hm.barrier_proximity_score:.0f}/100</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with ms_c3:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_res_col}33;'
        f'border-top:3px solid {_res_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">RESONANCE PRESSURE</div>'
        f'<div style="color:{_res_col};font-size:1.5rem;font-weight:800;margin-bottom:4px;">{hm.resonance_label}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">{hm.resonance_score:.0f} / 100</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">Correlated failure risk</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with ms_c4:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_ced_col}33;'
        f'border-top:3px solid {_ced_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">COHERENCE EXHAUSTION</div>'
        f'<div style="color:{_ced_col};font-size:1.5rem;font-weight:800;margin-bottom:4px;">{hm.ced_label}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">Index: {hm.ced:.3f}</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">Stress vs. capacity</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# Row 2: advanced indicators
ms_r2c1, ms_r2c2, ms_r2c3 = st.columns(3)

with ms_r2c1:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_rent_col}33;'
        f'border-top:3px solid {_rent_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">FAILURE ENTROPY</div>'
        f'<div style="color:{_rent_col};font-size:2.2rem;font-weight:800;margin-bottom:4px;">{hm.rentropy_score:.0f}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">/ 100 &nbsp;&middot;&nbsp; spread index</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">High = failure spread across dimensions</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with ms_r2c2:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_xi_col}33;'
        f'border-top:3px solid {_xi_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">COHERENCE-CHAOS RATIO</div>'
        f'<div style="color:{_xi_col};font-size:1.8rem;font-weight:800;margin-bottom:4px;">&xi; {hm.xi:.3f}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">{hm.xi_label}</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">&lt;1 = attractor &nbsp;&middot;&nbsp; &gt;1 = chaos dominant</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with ms_r2c3:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {_vtot_col}33;'
        f'border-top:3px solid {_vtot_col};border-radius:12px;padding:18px;text-align:center;min-height:120px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:8px;">COMPOSITE STABILITY</div>'
        f'<div style="color:{_vtot_col};font-size:2.2rem;font-weight:800;margin-bottom:4px;">{hm.v_total_score:.0f}</div>'
        f'<div style="color:#64748b;font-size:0.72rem;">/ 100 &nbsp;&middot;&nbsp; V-total index</div>'
        f'<div style="color:#7b8fa1;font-size:0.68rem;margin-top:4px;">Instability + Entropy + Boundary pressure</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# Active boundary conditions
if hm.active_barriers:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.8rem;margin:16px 0 6px 0;font-weight:600;">'
        'Active Boundary Conditions</p>',
        unsafe_allow_html=True
    )
    for barrier in hm.active_barriers:
        st.markdown(
            f'<div style="background:#1a0a0a;border-left:3px solid #dc2626;'
            f'padding:9px 16px;border-radius:6px;margin-bottom:5px;">'
            f'<span style="color:#fca5a5;font-size:0.83rem;">{barrier}</span>'
            f'</div>',
            unsafe_allow_html=True
        )


# ── SECTION 6: PRIORITY STABILIZATION ACTIONS ────────────────────────────────

if horizon.corrective_actions:
    st.markdown(_section_divider("RECOMMENDED CORRECTIONS"), unsafe_allow_html=True)
    st.markdown("#### Priority Stabilization Actions")
    st.caption(
        "Governance actions ranked by urgency. Address high-impact items first to restore "
        "posture toward the stability zone."
    )
    for action in horizon.corrective_actions:
        ic = _IMPACT_COLORS.get(action.expected_impact, "#64748b")
        st.markdown(
            f'<div style="background:#0a0f1e;border:1px solid rgba(144,211,255,0.1);'
            f'border-left:3px solid #90d3ff;padding:16px 20px;border-radius:8px;margin-bottom:10px;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
            f'<span style="background:rgba(144,211,255,0.1);color:#90d3ff;font-weight:800;'
            f'font-size:0.82rem;width:24px;height:24px;border-radius:50%;display:inline-flex;'
            f'align-items:center;justify-content:center;flex-shrink:0;">{action.priority}</span>'
            f'<span style="color:white;font-weight:700;font-size:0.92rem;">{action.display_dimension}</span>'
            f'<span style="background:{ic}22;color:{ic};font-size:0.68rem;font-weight:700;'
            f'padding:2px 9px;border-radius:999px;border:1px solid {ic}44;">{action.expected_impact}</span>'
            f'</div>'
            f'<div style="color:#94a3b8;font-size:0.86rem;padding-left:34px;line-height:1.5;">'
            f'{action.action}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ── UPCOMING HORIZON CAPABILITIES ────────────────────────────────────────────

st.markdown(_section_divider("UPCOMING CAPABILITIES"), unsafe_allow_html=True)
st.markdown("#### Upcoming Horizon Capabilities")
st.caption("Next-generation governance intelligence features in development.")

upcoming = [
    ("Trajectory Forecasting",
     "Model governance trajectory forward in time based on current velocity and acceleration signals."),
    ("Intervention Simulation",
     "Simulate the effect of governance interventions on Trust Horizon and attractor membership."),
    ("Attractor Engineering",
     "Design target governance postures and generate intervention pathways to reach them."),
    ("Governance Scenario Modeling",
     "Stress-test governance configurations against adversarial, compliance, and operational scenarios."),
]

up_c1, up_c2 = st.columns(2)
for i, (title, desc) in enumerate(upcoming):
    col = up_c1 if i % 2 == 0 else up_c2
    with col:
        st.markdown(
            f'<div style="background:#0a0f1e;border:1px solid rgba(144,211,255,0.08);'
            f'border-radius:12px;padding:18px 20px;margin-bottom:10px;opacity:0.6;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
            f'<span style="color:#90d3ff;font-weight:700;font-size:0.88rem;">{title}</span>'
            f'<span style="background:rgba(144,211,255,0.1);color:#90d3ff;font-size:0.64rem;'
            f'font-weight:700;padding:2px 9px;border-radius:999px;letter-spacing:0.08em;'
            f'text-transform:uppercase;">Coming Soon</span>'
            f'</div>'
            f'<div style="color:#8898a8;font-size:0.82rem;line-height:1.5;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ── FOOTER ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    '<p style="color:#334155;font-size:0.75rem;text-align:center;margin-top:8px;">'
    'Treasurety Horizon &mdash; Governance Dynamics &amp; Trust Horizon Intelligence<br>'
    'All Trust Horizon estimates are heuristic &middot; Pending longitudinal calibration &middot; '
    'Signals feed Treasurety Govern policy engine'
    '</p>',
    unsafe_allow_html=True
)
