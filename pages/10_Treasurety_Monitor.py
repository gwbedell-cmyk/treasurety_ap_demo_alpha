import streamlit as st
import plotly.graph_objects as go
from services import branding
from services.horizon import evaluate_horizon_from_monitor_scenario

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

# ── SCENARIO DATA ─────────────────────────────────────────────────────────────

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

# ── SCORING ENGINE ────────────────────────────────────────────────────────────

DRIFT_WEIGHTS = {
    "policy_drift":       0.28,
    "behavioral_drift":   0.24,
    "trust_drift":        0.22,
    "ecosystem_drift":    0.14,
    "intervention_drift": 0.12,
}

def compute_drift_risk(s):
    return int(
        s["policy_drift"]       * DRIFT_WEIGHTS["policy_drift"] +
        s["behavioral_drift"]   * DRIFT_WEIGHTS["behavioral_drift"] +
        s["trust_drift"]        * DRIFT_WEIGHTS["trust_drift"] +
        s["ecosystem_drift"]    * DRIFT_WEIGHTS["ecosystem_drift"] +
        s["intervention_drift"] * DRIFT_WEIGHTS["intervention_drift"]
    )

def drift_band(score):
    if score < 25:   return "Low",      "#16a34a"
    if score < 50:   return "Moderate", "#f59e0b"
    if score < 75:   return "High",     "#ea580c"
    return                  "Critical", "#dc2626"

def assurance_verdict(drift_risk, stability):
    if drift_risk < 20 and stability >= 85:
        return "HEALTHY",                   "#16a34a", "System operating within governance expectations. Continuous monitoring confirms stable execution."
    if drift_risk < 35 and stability >= 70:
        return "STABLE WITH WATCHPOINTS",   "#0891b2", "Governance stable. Minor drift indicators detected — monitor for trend continuation."
    if drift_risk < 55 and stability >= 50:
        return "ELEVATED RISK",             "#f59e0b", "Meaningful drift detected across one or more dimensions. Governance review recommended."
    if drift_risk < 75 and stability >= 35:
        return "INTERVENTION RECOMMENDED",  "#ea580c", "Significant drift accumulation. Human governance intervention required."
    return         "RESTRICT EXECUTION",    "#dc2626", "Critical governance degradation. Autonomous execution authority should be suspended pending review."

VERDICT_FILL = {
    "HEALTHY":                  "rgba(22,163,74,0.08)",
    "STABLE WITH WATCHPOINTS":  "rgba(8,145,178,0.08)",
    "ELEVATED RISK":            "rgba(245,158,11,0.08)",
    "INTERVENTION RECOMMENDED": "rgba(234,88,12,0.08)",
    "RESTRICT EXECUTION":       "rgba(220,38,38,0.08)",
}

def generate_alerts(s):
    alerts = []
    pct = s["escalation_trend_pct"]

    if s["policy_drift"] >= 75:
        alerts.append(("CRITICAL", "Policy boundary violations at critical frequency. Governance enforcement failing."))
    elif s["policy_drift"] >= 55:
        alerts.append(("WARNING", "Policy drift exceeds acceptable threshold. Decision variance increasing."))
    elif s["policy_drift"] >= 35:
        alerts.append(("WATCH", "Policy boundary pressure detected. Monitor for further escalation."))

    if s["behavioral_drift"] >= 75:
        alerts.append(("CRITICAL", "Severe behavioral deviation from established baseline. Execution patterns unrecognized."))
    elif s["behavioral_drift"] >= 55:
        alerts.append(("WARNING", "Behavioral drift exceeds acceptable threshold. Unusual execution sequences detected."))
    elif s["behavioral_drift"] >= 30:
        alerts.append(("WATCH", "Baseline behavioral variance elevated. Early drift signal detected."))

    if s["trust_drift"] >= 65:
        alerts.append(("CRITICAL", "Trust degradation detected in third-party dependency. Trust surface compromised."))
    elif s["trust_drift"] >= 45:
        alerts.append(("WARNING", "Trust signals declining. Anomaly accumulation rate elevated."))
    elif s["trust_drift"] >= 20:
        alerts.append(("WATCH", "Early trust signal degradation. Dependency health monitoring advised."))

    if s["ecosystem_drift"] >= 65:
        alerts.append(("CRITICAL", "Third-party dependency instability at critical level. Vendor trust failing."))
    elif s["ecosystem_drift"] >= 45:
        alerts.append(("WARNING", "Vendor trust deterioration detected. API reliability degrading."))
    elif s["ecosystem_drift"] >= 25:
        alerts.append(("WATCH", "Ecosystem dependency instability emerging. Third-party trust monitoring advised."))

    if s["intervention_drift"] >= 75:
        alerts.append(("CRITICAL", f"Human intervention burden critical. Escalation frequency increased {pct}%. Governance strain at breaking point."))
    elif s["intervention_drift"] >= 50:
        alerts.append(("WARNING", f"Escalation frequency increased {pct}%. Intervention burden unsustainable."))
    elif s["intervention_drift"] >= 30:
        alerts.append(("WATCH", "Human intervention burden increasing. Exception frequency elevated."))

    if s["governance_stability"] < 35:
        alerts.append(("CRITICAL", "Governance stability critically low. Platform integrity at risk."))
    elif s["governance_stability"] < 55:
        alerts.append(("WARNING", "Governance stability declining. System trust degrading over time."))

    if s["policy_exception_rate"] >= 50:
        alerts.append(("CRITICAL", "Policy exception growth indicates governance instability. Exception rate unsustainable."))
    elif s["policy_exception_rate"] >= 30:
        alerts.append(("WARNING", "Policy exception rate elevated. Governance configuration review required."))

    if not alerts:
        alerts.append(("INFO", "All governance signals within acceptable bounds. System operating normally."))

    severity_order = {"CRITICAL": 0, "WARNING": 1, "WATCH": 2, "INFO": 3}
    return sorted(alerts, key=lambda a: severity_order.get(a[0], 4))

def generate_recommendations(s, verdict):
    recs = []
    if s["policy_drift"] >= 55:
        recs.append("Reduce autonomous authority scope — policy boundary pressure indicates over-authorization.")
    if s["behavioral_drift"] >= 50:
        recs.append("Require additional human checkpoints on high-variance execution paths.")
    if s["trust_drift"] >= 50 or s["ecosystem_drift"] >= 50:
        recs.append("Restrict third-party delegation until ecosystem trust is restored.")
    if s["ecosystem_drift"] >= 55:
        recs.append("Enable Treasurety Shield before continued execution — adversarial trust surface active.")
    if s["intervention_drift"] >= 55:
        recs.append("Review autonomous authority grants — escalation burden indicates scope miscalibration.")
    if s["policy_exception_rate"] >= 35:
        recs.append("Audit policy registry — high exception rate indicates governance configuration drift.")
    if verdict in ("ELEVATED RISK", "INTERVENTION RECOMMENDED"):
        recs.append("Re-assess deployment readiness with Treasurety Assess to recalibrate governance parameters.")
    if verdict == "RESTRICT EXECUTION":
        recs.append("Suspend autonomous execution authority pending full governance review.")
        recs.append("Initiate Treasurety Assess re-evaluation before resuming any deployment.")
    if s["governance_stability"] < 60 and s["trust_integrity"] < 65:
        recs.append("Engage Treasurety Govern — tighten runtime policy enforcement and intervention thresholds.")
    if not recs:
        recs.append("Maintain current governance parameters. Schedule next review cycle in 30 days.")
        recs.append("Continue standard Treasurety Monitor cadence. No immediate action required.")
    return recs

def _make_previous_scenario(scenario: dict):
    """
    Derive a synthetic previous-period scenario from trend_history velocity.
    Used to give Horizon a drift velocity signal without separate historical data.
    """
    h = scenario.get("trend_history", [])
    if len(h) < 2:
        return None
    # 3-period average for a stable velocity estimate
    prev_stability = sum(h[-4:-1]) / 3 if len(h) >= 4 else h[-2]
    delta = h[-1] - prev_stability  # positive = currently more stable

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


def recommend_modules(s, verdict):
    modules = []
    if s["ecosystem_drift"] >= 45 or s["trust_drift"] >= 45:
        modules.append(("Treasurety Shield", "Adversarial protection and trust boundary enforcement.", "#dc2626"))
    if verdict in ("ELEVATED RISK", "INTERVENTION RECOMMENDED", "RESTRICT EXECUTION"):
        modules.append(("Treasurety Assess", "Re-run pre-deployment readiness evaluation.", "#8b5cf6"))
    if s["policy_drift"] >= 45 or s["intervention_drift"] >= 45:
        modules.append(("Treasurety Govern", "Tighten runtime policy enforcement and execution controls.", "#3b82f6"))
    return modules


# ── HEADER ────────────────────────────────────────────────────────────────────

st.image("assets/logo.png", width=240)

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(6,182,212,0.15);color:#67e8f9;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(6,182,212,0.3);">TREASURETY MONITOR™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Continuous Drift Detection & Assurance")
st.caption("Autonomous systems change over time. Treasurety Monitor detects drift before trust becomes failure.")

col_title, col_scenario = st.columns([3, 2])
with col_scenario:
    scenario_name = st.selectbox(
        "⚡ Active Monitoring Scenario",
        list(SCENARIOS.keys()),
        help="Select a pre-configured monitoring scenario"
    )

st.markdown("---")

# ── DERIVE ALL OUTPUTS FROM SELECTED SCENARIO ─────────────────────────────────

s = SCENARIOS[scenario_name]
drift_risk = compute_drift_risk(s)
drift_label, drift_color = drift_band(drift_risk)
verdict, verdict_color, verdict_desc = assurance_verdict(drift_risk, s["governance_stability"])
alerts  = generate_alerts(s)
recs    = generate_recommendations(s, verdict)
modules = recommend_modules(s, verdict)
horizon = evaluate_horizon_from_monitor_scenario(s, _make_previous_scenario(s))

st.markdown(
    f'<div style="background:#0f172a;border-left:4px solid #06b6d4;padding:14px 18px;border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">'
    f'<strong style="color:#67e8f9;">{s["system_name"]}</strong>&nbsp;&nbsp;·&nbsp;&nbsp;{s["domain"]}&nbsp;&nbsp;·&nbsp;&nbsp;{s["agent_type"]}<br>'
    f'<em>{s["description"]}</em>'
    f'</div>',
    unsafe_allow_html=True
)


# ── MODULE 1: GOVERNANCE HEALTH OVERVIEW ──────────────────────────────────────

st.markdown("#### Governance Health Overview")

m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

with m1:
    delta_stability = s["governance_stability"] - 80
    st.metric("Governance Stability", str(s["governance_stability"]), delta=f"{delta_stability:+d} vs baseline")
with m2:
    delta_trust = s["trust_integrity"] - 80
    st.metric("Trust Integrity Score", str(s["trust_integrity"]), delta=f"{delta_trust:+d} vs baseline")
with m3:
    st.metric("Composite Drift Risk", f"{drift_risk}/100", delta=drift_label)
with m4:
    pct = s["escalation_trend_pct"]
    sign = "+" if pct > 0 else ""
    st.metric("Escalation Trend", f"{sign}{pct}%", delta="Rising" if pct > 0 else "Declining")
with m5:
    burden = s["intervention_burden"]
    st.metric("Intervention Burden", f"{burden}%", delta="High" if burden > 40 else "Normal")
with m6:
    exc_rate = s["policy_exception_rate"]
    st.metric("Policy Exception Rate", f"{exc_rate}%", delta="Elevated" if exc_rate > 20 else "Normal")

st.markdown("---")


# ── MODULE 2: DRIFT DETECTION ENGINE ──────────────────────────────────────────

st.markdown("#### Drift Detection Engine")

DRIFT_DIMS = [
    ("Policy Drift",       "policy_drift",       "Policy violations, boundary pressure, decision variance"),
    ("Behavioral Drift",   "behavioral_drift",   "Unexpected action patterns, baseline deviation, unusual execution sequences"),
    ("Trust Drift",        "trust_drift",         "Declining trust signals, dependency degradation, anomaly accumulation"),
    ("Ecosystem Drift",    "ecosystem_drift",     "Third-party instability, API reliability degradation, vendor trust"),
    ("Intervention Drift", "intervention_drift",  "Rising human interventions, escalation growth, exception frequency"),
]

for dim_name, dim_key, dim_detail in DRIFT_DIMS:
    score = s[dim_key]
    level_label, level_color = drift_band(score)
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:18px 22px;margin-bottom:8px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
        f'<div><span style="color:white;font-weight:600;font-size:0.95rem;">{dim_name}</span>'
        f'<span style="color:#64748b;font-size:0.8rem;margin-left:12px;">{dim_detail}</span></div>'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<span style="color:#94a3b8;font-size:0.9rem;">{score}/100</span>'
        f'<span style="background:{level_color};color:white;font-weight:700;font-size:0.72rem;padding:2px 10px;border-radius:999px;">{level_label}</span>'
        f'</div></div>'
        f'<div style="background:#1e293b;border-radius:999px;height:6px;">'
        f'<div style="background:{level_color};width:{score}%;height:6px;border-radius:999px;"></div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

st.markdown("---")


# ── MODULE 3: HEALTH VISUALIZATION ────────────────────────────────────────────

st.markdown("#### Health Visualization")

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">Drift Dimension Radar</p>',
        unsafe_allow_html=True
    )
    categories = ["Policy", "Behavioral", "Trust", "Ecosystem", "Intervention"]
    values     = [s["policy_drift"], s["behavioral_drift"], s["trust_drift"], s["ecosystem_drift"], s["intervention_drift"]]
    cats_c     = categories + [categories[0]]
    vals_c     = values     + [values[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_c, theta=cats_c,
        fill="toself",
        fillcolor="rgba(6,182,212,0.15)",
        line=dict(color="#06b6d4", width=2),
        name="Drift Risk"
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=[25, 25, 25, 25, 25, 25], theta=cats_c,
        fill="toself",
        fillcolor="rgba(22,163,74,0.06)",
        line=dict(color="#16a34a", width=1, dash="dot"),
        name="Safe Threshold"
    ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(15,23,42,0.8)",
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#64748b", size=9), gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)"),
            angularaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with chart_right:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">Governance Stability Trend (12 monitoring periods)</p>',
        unsafe_allow_html=True
    )
    periods   = list(range(1, 13))
    history   = s["trend_history"]
    fill_rgba = VERDICT_FILL.get(verdict, "rgba(6,182,212,0.06)")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=periods, y=history,
        mode="lines+markers",
        line=dict(color=verdict_color, width=2.5),
        marker=dict(color=verdict_color, size=5),
        fill="tozeroy",
        fillcolor=fill_rgba,
        name="Stability Score"
    ))
    fig_trend.add_hline(
        y=70, line_dash="dot", line_color="#16a34a", line_width=1,
        annotation_text="Safe Zone (70)", annotation_font_color="#16a34a", annotation_font_size=10,
    )
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        xaxis=dict(title="Period", tickfont=dict(color="#64748b"), gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(title="Stability Score", tickfont=dict(color="#64748b"), gridcolor="rgba(255,255,255,0.04)", range=[0, 100]),
        legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")


# ── MODULE 4: ALERT ENGINE ────────────────────────────────────────────────────

st.markdown("#### Active Alerts")

ALERT_STYLES = {
    "INFO":     ("#1e3a5f", "#93c5fd"),
    "WATCH":    ("#1c2d1c", "#86efac"),
    "WARNING":  ("#3d2a00", "#fcd34d"),
    "CRITICAL": ("#3b0a0a", "#fca5a5"),
}

for severity, message in alerts:
    bg, fg = ALERT_STYLES.get(severity, ALERT_STYLES["INFO"])
    st.markdown(
        f'<div style="background:{bg};border-left:3px solid {fg};border-radius:8px;padding:12px 16px;margin-bottom:6px;">'
        f'<span style="color:{fg};font-weight:700;font-size:0.75rem;letter-spacing:0.07em;">{severity}</span>'
        f'<span style="color:#94a3b8;font-size:0.88rem;margin-left:10px;">{message}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("---")


# ── MODULE 5: CONTINUOUS ASSURANCE VERDICT ────────────────────────────────────

st.markdown("#### Continuous Assurance Verdict")

st.markdown(
    f'<div style="background:{verdict_color};border-radius:16px;padding:28px 32px;margin-bottom:24px;text-align:center;">'
    f'<div style="color:rgba(255,255,255,0.7);font-size:0.8rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">CONTINUOUS ASSURANCE DECISION</div>'
    f'<div style="color:white;font-size:2.4rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">{verdict}</div>'
    f'<div style="color:rgba(255,255,255,0.85);font-size:1rem;">{s["system_name"]} — Drift Risk: {drift_risk}/100 ({drift_label})</div>'
    f'<div style="color:rgba(255,255,255,0.7);font-size:0.88rem;margin-top:6px;">{verdict_desc}</div>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ── MODULE 6: RECOMMENDATION ENGINE ──────────────────────────────────────────

st.markdown("#### Governance Recommendations")

for i, rec in enumerate(recs):
    st.markdown(
        f'<div style="background:#0f172a;border-left:3px solid #06b6d4;padding:12px 16px;border-radius:8px;margin-bottom:8px;">'
        f'<span style="color:#06b6d4;font-weight:700;font-size:0.85rem;margin-right:12px;">{i+1:02d}</span>'
        f'<span style="color:#cbd5e1;font-size:0.9rem;">{rec}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("---")


# ── MODULE 7: EXECUTIVE ASSURANCE SUMMARY ─────────────────────────────────────

st.markdown("#### Executive Assurance Summary")

critical_count = sum(1 for a in alerts if a[0] == "CRITICAL")
warning_count  = sum(1 for a in alerts if a[0] == "WARNING")
watch_count    = sum(1 for a in alerts if a[0] == "WATCH")
trend_sign     = "+" if s["escalation_trend_pct"] > 0 else ""
trend_str      = f"{trend_sign}{s['escalation_trend_pct']}%"

summary_rows = [
    ("Monitored System",      s["system_name"]),
    ("Domain",                f'{s["domain"]} · {s["agent_type"]}'),
    ("Assurance Verdict",     verdict),
    ("Governance Stability",  f'{s["governance_stability"]} / 100'),
    ("Trust Integrity",       f'{s["trust_integrity"]} / 100'),
    ("Composite Drift Risk",  f'{drift_risk} / 100  ({drift_label})'),
    ("Escalation Trend",      trend_str),
    ("Intervention Burden",   f'{s["intervention_burden"]}%'),
    ("Policy Exception Rate", f'{s["policy_exception_rate"]}%'),
    ("Active Alerts",         f'{critical_count} Critical · {warning_count} Warning · {watch_count} Watch'),
]

rows_html = "".join(
    f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
    f'<span style="color:#64748b;font-size:0.85rem;">{label}</span>'
    f'<span style="color:#e2e8f0;font-size:0.85rem;font-weight:600;">{value}</span>'
    f'</div>'
    for label, value in summary_rows
)

exec_left, exec_right = st.columns([3, 2])

with exec_left:
    st.markdown(
        '<div style="background:#0f172a;border:1px solid rgba(6,182,212,0.2);border-radius:14px;padding:24px 28px;">'
        '<h4 style="color:white;margin:0 0 16px 0;">System Health Report</h4>'
        + rows_html +
        '</div>',
        unsafe_allow_html=True
    )

with exec_right:
    if modules:
        module_cards = "".join(
            f'<div style="background:#0a0f1e;border:1px solid {mc};border-radius:10px;padding:12px 14px;margin-bottom:8px;">'
            f'<div style="color:{mc};font-weight:700;font-size:0.85rem;">{mn}</div>'
            f'<div style="color:#64748b;font-size:0.78rem;margin-top:3px;">{md}</div>'
            f'</div>'
            for mn, md, mc in modules
        )
        st.markdown(
            '<div style="background:#0f172a;border:1px solid #1e293b;border-radius:14px;padding:24px 28px;margin-bottom:12px;">'
            '<h4 style="color:white;margin:0 0 14px 0;">Recommended Modules</h4>'
            + module_cards +
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div style="background:#0a0f1e;border:1px solid rgba(6,182,212,0.2);border-radius:10px;padding:16px 18px;">'
        '<div style="color:#67e8f9;font-size:0.8rem;font-weight:700;margin-bottom:6px;">MONITORING CADENCE</div>'
        '<div style="color:#64748b;font-size:0.8rem;line-height:1.7;">'
        'Continuous real-time signal ingestion<br>'
        'Drift assessment: every execution cycle<br>'
        'Assurance report: every governance period<br>'
        'Executive summary: on-demand or scheduled'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ── MODULE 8: TREASURETY HORIZON ──────────────────────────────────────────────

_HZ_MEMBERSHIP_COLORS = {
    "ATTRACTOR_MEMBER":  "#16a34a",
    "NEAR_BOUNDARY":     "#f59e0b",
    "OUTSIDE_ATTRACTOR": "#ea580c",
    "CRITICAL_DRIFT":    "#dc2626",
}
_HZ_MEMBERSHIP_SHORT = {
    "ATTRACTOR_MEMBER":  "IN ZONE",
    "NEAR_BOUNDARY":     "NEAR BOUNDARY",
    "OUTSIDE_ATTRACTOR": "OUTSIDE ZONE",
    "CRITICAL_DRIFT":    "CRITICAL DRIFT",
}
_HZ_HORIZON_COLORS = {
    "Stable Horizon":  "#16a34a",
    "Watch Horizon":   "#f59e0b",
    "Urgent Horizon":  "#ea580c",
    "Expired Horizon": "#dc2626",
}
_HZ_STABILITY_COLORS = {
    "stable":   "#16a34a",
    "watch":    "#f59e0b",
    "unstable": "#ea580c",
    "critical": "#dc2626",
}
_HZ_DRIFT_COLORS = {
    "IMPROVING":         "#16a34a",
    "STABLE":            "#06b6d4",
    "DEGRADING":         "#f59e0b",
    "RAPID_DEGRADATION": "#dc2626",
}
_HZ_IMPACT_COLORS = {"HIGH": "#dc2626", "MEDIUM": "#f59e0b", "LOW": "#16a34a"}

m_color = _HZ_MEMBERSHIP_COLORS.get(horizon.horizon_membership, "#64748b")
h_color = _HZ_HORIZON_COLORS.get(horizon.trust_horizon.horizon_label, "#64748b")
s_color = _HZ_STABILITY_COLORS.get(horizon.stability.stability_label, "#64748b")
d_color = _HZ_DRIFT_COLORS.get(horizon.drift.drift_direction, "#64748b")

vel       = horizon.governance_velocity
acc       = horizon.governance_acceleration
vel_sign  = "+" if vel >= 0 else ""
acc_sign  = "+" if acc >= 0 else ""
vel_arrow = "↑" if vel > 0.5 else ("↓" if vel < -0.5 else "→")

th_months  = horizon.trust_horizon_months
th_display = f"{th_months:.1f} mo" if th_months >= 0.1 else "< 0.1 mo"

top_factor = horizon.trajectory_summary.top_drift_factor
if top_factor == "none":
    top_factor = "None detected"

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div style="display:flex;align-items:center;gap:16px;margin:8px 0 20px 0;">'
    '<div style="flex:1;height:1px;background:linear-gradient(to right,'
    'rgba(139,92,246,0.5),transparent);"></div>'
    '<span style="background:rgba(139,92,246,0.15);color:#c4b5fd;font-size:0.72rem;'
    'font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:5px 16px;'
    'border-radius:999px;border:1px solid rgba(139,92,246,0.35);">TREASURETY HORIZON</span>'
    '<div style="flex:1;height:1px;background:linear-gradient(to left,'
    'rgba(139,92,246,0.5),transparent);"></div>'
    '</div>',
    unsafe_allow_html=True
)
st.markdown("#### Governance Stability Analysis & Trust Horizon")
st.caption(
    "Horizon maps the system’s governance posture against its stability zone and estimates "
    "how long current trust conditions can hold. All Trust Horizon estimates are heuristic."
)

# ── STATUS CARDS ───────────────────────────────────────────────────────────────

hz_c1, hz_c2, hz_c3, hz_c4 = st.columns(4)

with hz_c1:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {m_color}33;border-top:3px solid {m_color};'
        f'border-radius:12px;padding:20px;text-align:center;min-height:110px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:10px;">ATTRACTOR MEMBERSHIP</div>'
        f'<div style="color:{m_color};font-size:1.05rem;font-weight:800;margin-bottom:6px;">'
        f'{_HZ_MEMBERSHIP_SHORT.get(horizon.horizon_membership, horizon.horizon_membership)}</div>'
        f'<div style="color:#64748b;font-size:0.75rem;">Stability score: {horizon.horizon_stability:.0f}/100</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with hz_c2:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {s_color}33;border-top:3px solid {s_color};'
        f'border-radius:12px;padding:20px;text-align:center;min-height:110px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:10px;">GOVERNANCE STABILITY</div>'
        f'<div style="color:{s_color};font-size:2rem;font-weight:800;margin-bottom:6px;">'
        f'{horizon.horizon_stability:.0f}</div>'
        f'<div style="color:#64748b;font-size:0.75rem;">{horizon.stability.stability_label.upper()}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with hz_c3:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {h_color}33;border-top:3px solid {h_color};'
        f'border-radius:12px;padding:20px;text-align:center;min-height:110px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:10px;">TRUST HORIZON</div>'
        f'<div style="color:{h_color};font-size:2rem;font-weight:800;margin-bottom:6px;">{th_display}</div>'
        f'<div style="color:#64748b;font-size:0.75rem;">{horizon.trust_horizon.horizon_label}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with hz_c4:
    st.markdown(
        f'<div style="background:#0f172a;border:1px solid {d_color}33;border-top:3px solid {d_color};'
        f'border-radius:12px;padding:20px;text-align:center;min-height:110px;">'
        f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:10px;">GOVERNANCE DRIFT</div>'
        f'<div style="color:{d_color};font-size:1.6rem;font-weight:800;margin-bottom:6px;">'
        f'{vel_arrow} {vel_sign}{vel:.1f}</div>'
        f'<div style="color:#64748b;font-size:0.75rem;">'
        f'{horizon.drift.drift_direction.replace("_", " ")}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── CHARTS ─────────────────────────────────────────────────────────────────────

sv = horizon.state_vector
hz_chart_l, hz_chart_r = st.columns(2)

with hz_chart_l:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">'
        'Governance State Vector (0–100, higher = stronger posture)</p>',
        unsafe_allow_html=True
    )
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
        fillcolor="rgba(139,92,246,0.15)",
        line=dict(color="#8b5cf6", width=2),
        name="Governance State",
    ))
    fig_sv.update_layout(
        polar=dict(
            bgcolor="rgba(15,23,42,0.8)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(color="#64748b", size=9),
                gridcolor="rgba(255,255,255,0.07)",
                linecolor="rgba(255,255,255,0.07)",
            ),
            angularaxis=dict(
                tickfont=dict(color="#94a3b8", size=10),
                gridcolor="rgba(255,255,255,0.07)",
                linecolor="rgba(255,255,255,0.07)",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_sv, use_container_width=True)

with hz_chart_r:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">'
        'Trust Horizon — Heuristic Estimate</p>',
        unsafe_allow_html=True
    )
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=min(th_months, 24.0),
        number=dict(suffix=" mo", font=dict(size=36, color=h_color)),
        gauge=dict(
            axis=dict(range=[0, 24], tickfont=dict(color="#64748b", size=9)),
            bar=dict(color=h_color, thickness=0.35),
            bgcolor="rgba(15,23,42,1)",
            borderwidth=0,
            steps=[
                dict(range=[0,  1],  color="rgba(220,38,38,0.25)"),
                dict(range=[1,  4],  color="rgba(234,88,12,0.2)"),
                dict(range=[4,  9],  color="rgba(245,158,11,0.18)"),
                dict(range=[9, 24],  color="rgba(22,163,74,0.15)"),
            ],
            threshold=dict(
                line=dict(color="#16a34a", width=2),
                thickness=0.75, value=9,
            ),
        ),
        title=dict(text=horizon.trust_horizon.horizon_label,
                   font=dict(color="#94a3b8", size=13)),
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8"),
        height=280,
        margin=dict(t=60, b=10, l=40, r=40),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.markdown(
        f'<div style="background:#0a0f1e;border:1px solid rgba(139,92,246,0.2);'
        f'border-radius:10px;padding:14px 16px;">'
        f'<div style="color:#a78bfa;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;'
        f'margin-bottom:5px;">PRIMARY RISK FACTOR</div>'
        f'<div style="color:#cbd5e1;font-size:0.85rem;line-height:1.4;">'
        f'{horizon.trust_horizon.primary_risk_factor}</div>'
        f'<div style="color:#334155;font-size:0.7rem;margin-top:6px;font-style:italic;">'
        f'{horizon.trust_horizon.confidence}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── GOVERNANCE TRAJECTORY ──────────────────────────────────────────────────────

st.markdown(
    '<p style="color:#94a3b8;font-size:0.85rem;margin:20px 0 8px 0;font-weight:600;">'
    'Governance Trajectory</p>',
    unsafe_allow_html=True
)

traj_c1, traj_c2, traj_c3, traj_c4 = st.columns(4)

traj_items = [
    ("Velocity",         f"{vel_sign}{vel:.2f}",  "composite pts / cycle",      d_color),
    ("Acceleration",     f"{acc_sign}{acc:.2f}",  "velocity change / cycle",
     "#16a34a" if acc >= 0 else "#f59e0b"),
    ("Boundary Distance",
     f"{'+' if horizon.boundary_distance >= 0 else ''}{horizon.boundary_distance:.1f}",
     "pts from stability boundary",               m_color),
    ("Top Drift Factor", top_factor,              "most degraded dimension",     "#8b5cf6"),
]

for col, (label, value, unit, color) in zip(
    [traj_c1, traj_c2, traj_c3, traj_c4], traj_items
):
    with col:
        st.markdown(
            f'<div style="background:#0f172a;border:1px solid #1e293b;border-radius:10px;'
            f'padding:16px;text-align:center;">'
            f'<div style="color:#64748b;font-size:0.68rem;font-weight:700;letter-spacing:0.08em;'
            f'text-transform:uppercase;margin-bottom:8px;">{label}</div>'
            f'<div style="color:{color};font-size:1.2rem;font-weight:800;">{value}</div>'
            f'<div style="color:#64748b;font-size:0.72rem;margin-top:2px;">{unit}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ── CORRECTIVE ACTIONS ─────────────────────────────────────────────────────────

if horizon.corrective_actions:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin:20px 0 8px 0;font-weight:600;">'
        'Horizon Corrective Actions</p>',
        unsafe_allow_html=True
    )
    for action in horizon.corrective_actions:
        ic = _HZ_IMPACT_COLORS.get(action.expected_impact, "#64748b")
        st.markdown(
            f'<div style="background:#0f172a;border-left:3px solid #8b5cf6;'
            f'padding:14px 18px;border-radius:8px;margin-bottom:8px;">'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:5px;">'
            f'<span style="background:rgba(139,92,246,0.2);color:#a78bfa;font-weight:800;'
            f'font-size:0.82rem;width:22px;height:22px;border-radius:50%;display:inline-flex;'
            f'align-items:center;justify-content:center;flex-shrink:0;">{action.priority}</span>'
            f'<span style="color:white;font-weight:600;font-size:0.9rem;">'
            f'{action.display_dimension}</span>'
            f'<span style="background:{ic}22;color:{ic};font-size:0.68rem;font-weight:700;'
            f'padding:2px 8px;border-radius:999px;border:1px solid {ic}44;">'
            f'{action.expected_impact}</span>'
            f'</div>'
            f'<div style="color:#94a3b8;font-size:0.85rem;padding-left:32px;">'
            f'{action.action}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("---")

st.markdown(
    '<p style="color:#334155;font-size:0.75rem;text-align:center;margin-top:8px;">'
    'Treasurety Monitor™ — Continuous Drift Detection &amp; Assurance'
    '&nbsp;&nbsp;·&nbsp;&nbsp;'
    'Treasurety Horizon — Governance Stability &amp; Trust Horizon<br>'
    'Partner-ready · White-label capable · Signals feed Treasurety Govern policy engine'
    '</p>',
    unsafe_allow_html=True
)
