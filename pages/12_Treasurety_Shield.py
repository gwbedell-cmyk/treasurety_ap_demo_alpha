import streamlit as st
import plotly.graph_objects as go
import math
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_nav()

# ── SCENARIO DATA ─────────────────────────────────────────────────────────────

SCENARIOS = {
    "Stable Ecosystem — Trusted Partner Network": {
        "ecosystem_name": "Enterprise Integration Platform",
        "domain":         "IT & Infrastructure",
        "agent_type":     "Multi-agent with trusted partners",
        "description":    "A mature enterprise integration ecosystem with established partner trust profiles and well-governed external dependencies. All third-party relationships are within approved trust boundaries.",
        "external_agent_risk":  8,
        "api_dependency_risk": 12,
        "delegation_risk":      6,
        "partner_risk":        10,
        "compositional_risk":   9,
        "third_party_trust_score":      92,
        "external_dependency_risk_kpi": 11,
        "delegated_authority_exposure":  8,
        "partner_stability_index":      94,
        "api_reliability_score":        96,
        "trust_zones": {
            "internal":   ["Finance Agent", "Procurement Bot", "Audit Agent"],
            "trusted":    ["SAP ERP API", "Salesforce CRM", "Stripe Payments"],
            "monitored":  ["Vendor Portal", "Partner API"],
            "restricted": [],
        },
        "trend_history": [91, 92, 93, 92, 93, 93, 94, 93, 94, 93, 92, 92],
    },
    "Third-Party Degradation — Vendor Instability": {
        "ecosystem_name": "Supply Chain Automation Platform",
        "domain":         "Supply Chain",
        "agent_type":     "Orchestrated agent fleet",
        "description":    "A supply chain automation platform experiencing significant vendor API instability and deteriorating third-party trust signals. Internal execution remains stable but ecosystem exposure is elevated.",
        "external_agent_risk": 22,
        "api_dependency_risk": 68,
        "delegation_risk":     28,
        "partner_risk":        72,
        "compositional_risk":  45,
        "third_party_trust_score":      44,
        "external_dependency_risk_kpi": 68,
        "delegated_authority_exposure": 32,
        "partner_stability_index":      38,
        "api_reliability_score":        41,
        "trust_zones": {
            "internal":   ["Supply Agent", "Procurement Bot"],
            "trusted":    ["Core ERP API"],
            "monitored":  ["Logistics API", "Vendor Portal", "Freight Partner"],
            "restricted": ["Legacy Supplier API", "External Fulfillment"],
        },
        "trend_history": [88, 86, 83, 79, 74, 68, 62, 57, 52, 48, 45, 44],
    },
    "Delegation Overreach — Authority Boundary Breach": {
        "ecosystem_name": "Financial Workflow Orchestrator",
        "domain":         "Financial Services",
        "agent_type":     "Agentic pipeline",
        "description":    "An autonomous financial workflow agent attempting to delegate authority beyond its approved boundary. Permission amplification detected across the execution chain. Scope expansion in progress.",
        "external_agent_risk": 74,
        "api_dependency_risk": 38,
        "delegation_risk":     88,
        "partner_risk":        42,
        "compositional_risk":  62,
        "third_party_trust_score":      38,
        "external_dependency_risk_kpi": 58,
        "delegated_authority_exposure": 84,
        "partner_stability_index":      55,
        "api_reliability_score":        72,
        "trust_zones": {
            "internal":   ["Finance Agent"],
            "trusted":    ["Payment API"],
            "monitored":  ["Sub-Agent A", "Sub-Agent B"],
            "restricted": ["External Exec Agent", "Unapproved API", "Scope-Amplified Chain"],
        },
        "trend_history": [82, 80, 78, 74, 70, 64, 58, 52, 46, 42, 40, 38],
    },
    "Multi-Agent Ecosystem Risk — Compositional Fragility": {
        "ecosystem_name": "Autonomous Operations Fleet",
        "domain":         "Operations",
        "agent_type":     "Multi-agent pipeline",
        "description":    "A complex multi-agent autonomous operations fleet with significant compositional chain fragility. Single-point failure risks across cascading dependency chains. Systemic ecosystem instability emerging.",
        "external_agent_risk": 52,
        "api_dependency_risk": 58,
        "delegation_risk":     48,
        "partner_risk":        55,
        "compositional_risk":  84,
        "third_party_trust_score":      41,
        "external_dependency_risk_kpi": 62,
        "delegated_authority_exposure": 48,
        "partner_stability_index":      46,
        "api_reliability_score":        53,
        "trust_zones": {
            "internal":   ["Ops Agent A", "Ops Agent B"],
            "trusted":    ["Core API"],
            "monitored":  ["External Agent X", "Partner API", "Vendor Service"],
            "restricted": ["Chain Node 4", "Chain Node 5", "Chain Node 6"],
        },
        "trend_history": [78, 74, 70, 66, 62, 58, 54, 50, 47, 44, 42, 41],
    },
    "Critical Ecosystem Failure — External Trust Collapse": {
        "ecosystem_name": "Enterprise AI Execution Platform",
        "domain":         "Financial Services",
        "agent_type":     "Multi-agent with external delegation",
        "description":    "Critical external trust collapse across multiple dependency chains. Unknown agent provenance, API authentication failures, vendor trust deterioration, and permission amplification converging. Immediate execution restriction required.",
        "external_agent_risk": 88,
        "api_dependency_risk": 82,
        "delegation_risk":     92,
        "partner_risk":        86,
        "compositional_risk":  90,
        "third_party_trust_score":      14,
        "external_dependency_risk_kpi": 88,
        "delegated_authority_exposure": 91,
        "partner_stability_index":      18,
        "api_reliability_score":        22,
        "trust_zones": {
            "internal":   ["Core Agent"],
            "trusted":    [],
            "monitored":  [],
            "restricted": ["External Agent A", "External Agent B", "Unknown API", "Compromised Vendor", "Rogue Sub-Agent", "Unauth Chain"],
        },
        "trend_history": [72, 65, 58, 50, 43, 37, 31, 26, 22, 18, 16, 14],
    },
}

# ── SCORING ENGINE ─────────────────────────────────────────────────────────────

RISK_WEIGHTS = {
    "external_agent_risk": 0.25,
    "api_dependency_risk": 0.20,
    "delegation_risk":     0.25,
    "partner_risk":        0.18,
    "compositional_risk":  0.12,
}

def compute_ecosystem_risk(s):
    return int(
        s["external_agent_risk"]  * RISK_WEIGHTS["external_agent_risk"] +
        s["api_dependency_risk"]  * RISK_WEIGHTS["api_dependency_risk"] +
        s["delegation_risk"]      * RISK_WEIGHTS["delegation_risk"] +
        s["partner_risk"]         * RISK_WEIGHTS["partner_risk"] +
        s["compositional_risk"]   * RISK_WEIGHTS["compositional_risk"]
    )

def risk_band(score):
    if score < 25:   return "Low",      "#16a34a"
    if score < 50:   return "Moderate", "#f59e0b"
    if score < 75:   return "High",     "#ea580c"
    return                  "Critical", "#dc2626"

def trust_verdict(composite_risk, trust_score):
    if composite_risk < 20 and trust_score >= 85:
        return "TRUSTED",    "#16a34a", "Ecosystem operating within approved trust boundaries. Third-party governance confirmed."
    if composite_risk < 40 and trust_score >= 65:
        return "WATCH",      "#0891b2", "Minor ecosystem risk signals detected. Third-party dependency monitoring advised."
    if composite_risk < 60 and trust_score >= 40:
        return "RESTRICTED", "#f59e0b", "Ecosystem risk elevated. Restrict third-party delegation pending trust verification."
    if composite_risk < 80 and trust_score >= 20:
        return "ESCALATE",   "#ea580c", "Significant trust boundary threats detected. Human governance intervention required."
    return                   "BLOCK",   "#dc2626", "Critical ecosystem trust failure. Suspend external execution authority pending full review."

VERDICT_FILL = {
    "TRUSTED":    "rgba(22,163,74,0.08)",
    "WATCH":      "rgba(8,145,178,0.08)",
    "RESTRICTED": "rgba(245,158,11,0.08)",
    "ESCALATE":   "rgba(234,88,12,0.08)",
    "BLOCK":      "rgba(220,38,38,0.08)",
}

ALERT_STYLES = {
    "INFO":     ("#1e3a5f", "#93c5fd"),
    "WATCH":    ("#1c2d1c", "#86efac"),
    "WARNING":  ("#3d2a00", "#fcd34d"),
    "CRITICAL": ("#3b0a0a", "#fca5a5"),
}

def generate_alerts(s):
    alerts = []
    if s["external_agent_risk"] >= 75:
        alerts.append(("CRITICAL", "Unknown external agent provenance confirmed. Agent trust verification failed — execution authority at risk."))
    elif s["external_agent_risk"] >= 55:
        alerts.append(("WARNING", "External agent governance maturity below required threshold. Trust profile degraded."))
    elif s["external_agent_risk"] >= 30:
        alerts.append(("WATCH", "External agent trust signals require monitoring. Provenance verification advised."))

    if s["api_dependency_risk"] >= 75:
        alerts.append(("CRITICAL", "API authentication failures detected across external services. Trust surface compromised."))
    elif s["api_dependency_risk"] >= 55:
        alerts.append(("WARNING", "API reliability below acceptable threshold. External dependency health deteriorating."))
    elif s["api_dependency_risk"] >= 30:
        alerts.append(("WATCH", "API dependency instability emerging. Service reliability monitoring activated."))

    if s["delegation_risk"] >= 75:
        alerts.append(("CRITICAL", "Delegated authority boundary breach confirmed. Permission amplification in progress — immediate intervention required."))
    elif s["delegation_risk"] >= 55:
        alerts.append(("WARNING", "Delegation scope exceeding approved boundary. Authority chain audit required."))
    elif s["delegation_risk"] >= 30:
        alerts.append(("WATCH", "Delegation boundary pressure detected. Authority scope monitoring advised."))

    if s["partner_risk"] >= 75:
        alerts.append(("CRITICAL", "Vendor trust collapse detected. Partner stability index at critical failure level."))
    elif s["partner_risk"] >= 55:
        alerts.append(("WARNING", "Vendor trust signals deteriorating. Partner stability index declining."))
    elif s["partner_risk"] >= 30:
        alerts.append(("WATCH", "Partner trust drift detected. Operational concentration risk elevated."))

    if s["compositional_risk"] >= 75:
        alerts.append(("CRITICAL", "Multi-agent chain fragility at critical level. Cascading failure exposure confirmed across dependency network."))
    elif s["compositional_risk"] >= 55:
        alerts.append(("WARNING", "Compositional dependency chain fragility elevated. Systemic failure risk growing."))
    elif s["compositional_risk"] >= 30:
        alerts.append(("WATCH", "Dependency chain concentration risk emerging. Compositional monitoring advised."))

    if not alerts:
        alerts.append(("INFO", "All ecosystem trust signals within approved boundaries. Third-party governance confirmed."))

    severity_order = {"CRITICAL": 0, "WARNING": 1, "WATCH": 2, "INFO": 3}
    return sorted(alerts, key=lambda a: severity_order.get(a[0], 4))

def generate_recommendations(s, verdict):
    recs = []
    if s["delegation_risk"] >= 55:
        recs.append("Restrict third-party delegation immediately — authority boundary breach detected.")
    if s["external_agent_risk"] >= 55:
        recs.append("Require human approval for all external agent execution until provenance is verified.")
    if s["api_dependency_risk"] >= 55:
        recs.append("Limit API permission scope and audit authentication controls across all external services.")
    if s["partner_risk"] >= 55:
        recs.append("Isolate high-risk partner dependencies — reduce operational concentration exposure.")
    if s["compositional_risk"] >= 55:
        recs.append("Introduce circuit breakers across fragile dependency chains to contain cascading failure risk.")
    if verdict in ("RESTRICTED", "ESCALATE"):
        recs.append("Re-assess deployment readiness with Treasurety Assess before resuming full execution scope.")
    if verdict == "ESCALATE":
        recs.append("Tighten Treasurety Govern runtime policy enforcement — reduce autonomous authority grants.")
    if verdict == "BLOCK":
        recs.append("Suspend all external execution authority pending full ecosystem trust review.")
        recs.append("Initiate Treasurety Assess re-evaluation and Treasurety Govern policy reset before any resumption.")
    if s["external_agent_risk"] >= 40 or s["partner_risk"] >= 40:
        recs.append("Enable Treasurety Monitor — continuous drift detection across third-party trust signals.")
    if not recs:
        recs.append("Maintain current ecosystem governance parameters. Schedule next trust review in 30 days.")
        recs.append("Continue standard Treasurety Shield monitoring cadence. No immediate action required.")
    return recs

def recommend_modules(s, verdict):
    modules = []
    if verdict in ("RESTRICTED", "ESCALATE", "BLOCK"):
        modules.append(("Treasurety Govern", "Tighten runtime policy enforcement and execution authorization controls.", "#3b82f6"))
    if verdict in ("ESCALATE", "BLOCK") or s["external_agent_risk"] >= 55:
        modules.append(("Treasurety Assess", "Re-evaluate deployment readiness given ecosystem trust profile changes.", "#8b5cf6"))
    if s["partner_risk"] >= 45 or s["compositional_risk"] >= 45:
        modules.append(("Treasurety Monitor", "Deploy continuous drift detection across ecosystem trust dimensions.", "#06b6d4"))
    return modules


# ── TRUST BOUNDARY MAP ────────────────────────────────────────────────────────

def build_trust_map(s):
    zones = s["trust_zones"]
    fig   = go.Figure()
    theta = [i * 2 * math.pi / 100 for i in range(101)]

    rings = [
        (0.28, "rgba(59,130,246,0.07)",  "rgba(59,130,246,0.3)"),
        (0.55, "rgba(22,163,74,0.05)",   "rgba(22,163,74,0.25)"),
        (0.78, "rgba(245,158,11,0.04)",  "rgba(245,158,11,0.22)"),
        (1.02, "rgba(220,38,38,0.04)",   "rgba(220,38,38,0.2)"),
    ]
    for r, fill_c, line_c in rings:
        fig.add_trace(go.Scatter(
            x=[r * math.cos(t) for t in theta],
            y=[r * math.sin(t) for t in theta],
            mode="lines", fill="toself",
            fillcolor=fill_c, line=dict(color=line_c, width=1, dash="dot"),
            hoverinfo="skip", showlegend=False,
        ))

    fig.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers+text",
        marker=dict(size=36, color="#0d1f3c", line=dict(color="#3b82f6", width=2.5)),
        text=["CORE"], textposition="middle center",
        textfont=dict(color="#7dd3fc", size=9),
        hovertemplate="<b>Treasurety Runtime</b><br>Governance Core<extra></extra>",
        showlegend=False,
    ))

    zone_params = [
        ("internal",   0.41, "#3b82f6", "#93c5fd", 0.0),
        ("trusted",    0.66, "#16a34a", "#86efac", 0.5),
        ("monitored",  0.88, "#f59e0b", "#fcd34d", 1.0),
        ("restricted", 1.10, "#dc2626", "#fca5a5", 0.3),
    ]
    for zone_key, radius, dot_color, text_color, angle_offset in zone_params:
        nodes = zones.get(zone_key, [])
        if not nodes:
            continue
        n = len(nodes)
        for i, name in enumerate(nodes):
            angle = (2 * math.pi * i / n) + angle_offset
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            tpos = "top center" if y > 0.1 else ("bottom center" if y < -0.1 else "middle right")
            fig.add_trace(go.Scatter(
                x=[0, x], y=[0, y], mode="lines",
                line=dict(color=dot_color, width=0.8, dash="dash"),
                opacity=0.22, hoverinfo="skip", showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode="markers+text",
                marker=dict(size=14, color=dot_color, line=dict(color=text_color, width=1.5)),
                text=[name.replace(" ", "<br>")],
                textposition=tpos,
                textfont=dict(color=text_color, size=8),
                hovertemplate=f"<b>{name}</b><br>Zone: {zone_key.title()}<extra></extra>",
                showlegend=False,
            ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,15,30,0.95)",
        xaxis=dict(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
        height=440, margin=dict(t=20, b=20, l=20, r=20),
    )
    return fig


# ── HEADER ────────────────────────────────────────────────────────────────────

st.image("assets/logo.png", width=240)

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(239,68,68,0.15);color:#fca5a5;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(239,68,68,0.3);">TREASURETY SHIELD™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Third-Party & Ecosystem Governance")
st.caption("Autonomous trust breaks at the ecosystem boundary. Treasurety Shield governs what happens when external systems enter the trust perimeter.")

col_title, col_scenario = st.columns([3, 2])
with col_scenario:
    scenario_name = st.selectbox(
        "⚡ Active Shield Scenario",
        list(SCENARIOS.keys()),
        help="Select a pre-configured ecosystem trust scenario"
    )

st.markdown("---")

# ── DERIVE ALL OUTPUTS ────────────────────────────────────────────────────────

s              = SCENARIOS[scenario_name]
composite_risk = compute_ecosystem_risk(s)
risk_label, risk_color = risk_band(composite_risk)
verdict, verdict_color, verdict_desc = trust_verdict(composite_risk, s["third_party_trust_score"])
alerts  = generate_alerts(s)
recs    = generate_recommendations(s, verdict)
modules = recommend_modules(s, verdict)

st.markdown(
    f'<div style="background:#0f172a;border-left:4px solid #ef4444;padding:14px 18px;border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">'
    f'<strong style="color:#fca5a5;">{s["ecosystem_name"]}</strong>&nbsp;&nbsp;·&nbsp;&nbsp;{s["domain"]}&nbsp;&nbsp;·&nbsp;&nbsp;{s["agent_type"]}<br>'
    f'<em>{s["description"]}</em>'
    f'</div>',
    unsafe_allow_html=True
)


# ── MODULE 1: ECOSYSTEM TRUST DASHBOARD ───────────────────────────────────────

st.markdown("#### Ecosystem Trust Dashboard")

m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

with m1:
    delta_tts = s["third_party_trust_score"] - 80
    st.metric("Third-Party Trust Score", str(s["third_party_trust_score"]), delta=f"{delta_tts:+d} vs baseline")
with m2:
    dep = s["external_dependency_risk_kpi"]
    st.metric("External Dependency Risk", f"{dep}/100", delta="Critical" if dep >= 75 else ("High" if dep >= 50 else ("Moderate" if dep >= 25 else "Low")))
with m3:
    deleg = s["delegated_authority_exposure"]
    st.metric("Delegated Authority Exposure", f"{deleg}%", delta="Elevated" if deleg > 40 else "Normal")
with m4:
    delta_psi = s["partner_stability_index"] - 80
    st.metric("Partner Stability Index", str(s["partner_stability_index"]), delta=f"{delta_psi:+d} vs baseline")
with m5:
    api_rel = s["api_reliability_score"]
    st.metric("API Reliability Score", str(api_rel), delta="Degraded" if api_rel < 60 else ("Nominal" if api_rel < 85 else "Healthy"))
with m6:
    st.metric("Composite Ecosystem Risk", f"{composite_risk}/100", delta=risk_label)

st.markdown("---")


# ── MODULE 2: TRUST BOUNDARY MAP ──────────────────────────────────────────────

st.markdown("#### Trust Boundary Map")

map_col, legend_col = st.columns([3, 1])

with map_col:
    st.plotly_chart(build_trust_map(s), use_container_width=True)

with legend_col:
    st.markdown('<div style="padding-top:32px;"></div>', unsafe_allow_html=True)
    for zone_key, label, dot_color, text_color, desc in [
        ("internal",   "Internal Agents",     "#3b82f6", "#93c5fd", "Governed by Treasurety runtime"),
        ("trusted",    "Trusted External",    "#16a34a", "#86efac", "Approved and verified partners"),
        ("monitored",  "Monitored",           "#f59e0b", "#fcd34d", "Under active trust monitoring"),
        ("restricted", "Restricted / Blocked","#dc2626", "#fca5a5", "Requires human authorization"),
    ]:
        count = len(s["trust_zones"].get(zone_key, []))
        st.markdown(
            f'<div style="background:#0f172a;border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:10px 14px;margin-bottom:6px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0;"></div>'
            f'<span style="color:white;font-size:0.8rem;font-weight:600;">{label}</span>'
            f'<span style="color:#64748b;font-size:0.75rem;margin-left:auto;">{count}</span>'
            f'</div>'
            f'<div style="color:#64748b;font-size:0.75rem;">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("---")


# ── MODULE 3: THIRD-PARTY RISK ENGINE ─────────────────────────────────────────

st.markdown("#### Third-Party Risk Engine")

RISK_DIMS = [
    ("External Agent Trust",       "external_agent_risk",  "Unknown provenance, poor governance maturity, unstable behavioral profile"),
    ("API Dependency Risk",        "api_dependency_risk",  "Service instability, auth weakness, degraded reliability, permission overreach"),
    ("Delegated Authority Risk",   "delegation_risk",       "Agent delegating to external agents, permission amplification, scope expansion"),
    ("Partner Dependency Risk",    "partner_risk",          "Vendor instability, poor trust signals, operational concentration risk"),
    ("Compositional Failure Risk", "compositional_risk",    "Chain dependency fragility, cascading failure exposure, multi-agent systemic instability"),
]

for dim_name, dim_key, dim_detail in RISK_DIMS:
    score = s[dim_key]
    level_label, level_color = risk_band(score)
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


# ── MODULE 4: ECOSYSTEM HEALTH VISUALIZATION ──────────────────────────────────

st.markdown("#### Ecosystem Health Visualization")

chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown(
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">Risk Dimension Radar</p>',
        unsafe_allow_html=True
    )
    categories = ["Ext. Agent", "API Dependency", "Delegation", "Partner", "Compositional"]
    values     = [s["external_agent_risk"], s["api_dependency_risk"], s["delegation_risk"], s["partner_risk"], s["compositional_risk"]]
    cats_c     = categories + [categories[0]]
    vals_c     = values     + [values[0]]

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals_c, theta=cats_c,
        fill="toself",
        fillcolor="rgba(239,68,68,0.12)",
        line=dict(color="#ef4444", width=2),
        name="Ecosystem Risk"
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
        '<p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;font-weight:600;">Third-Party Trust Score Trend (12 monitoring periods)</p>',
        unsafe_allow_html=True
    )
    periods    = list(range(1, 13))
    fill_rgba  = VERDICT_FILL.get(verdict, "rgba(239,68,68,0.06)")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=periods, y=s["trend_history"],
        mode="lines+markers",
        line=dict(color=verdict_color, width=2.5),
        marker=dict(color=verdict_color, size=5),
        fill="tozeroy",
        fillcolor=fill_rgba,
        name="Trust Score"
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
        yaxis=dict(title="Trust Score", tickfont=dict(color="#64748b"), gridcolor="rgba(255,255,255,0.04)", range=[0, 100]),
        legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=20, b=40, l=40, r=20),
        height=320,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")


# ── MODULE 5: ALERT ENGINE ────────────────────────────────────────────────────

st.markdown("#### Ecosystem Alerts")

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


# ── MODULE 6: TRUST GOVERNANCE VERDICT ───────────────────────────────────────

st.markdown("#### Trust Governance Verdict")

st.markdown(
    f'<div style="background:{verdict_color};border-radius:16px;padding:28px 32px;margin-bottom:24px;text-align:center;">'
    f'<div style="color:rgba(255,255,255,0.7);font-size:0.8rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">ECOSYSTEM TRUST DECISION</div>'
    f'<div style="color:white;font-size:2.4rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">{verdict}</div>'
    f'<div style="color:rgba(255,255,255,0.85);font-size:1rem;">{s["ecosystem_name"]} — Composite Risk: {composite_risk}/100 ({risk_label})</div>'
    f'<div style="color:rgba(255,255,255,0.7);font-size:0.88rem;margin-top:6px;">{verdict_desc}</div>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown("---")


# ── MODULE 7: RECOMMENDATION ENGINE ──────────────────────────────────────────

st.markdown("#### Governance Recommendations")

for i, rec in enumerate(recs):
    st.markdown(
        f'<div style="background:#0f172a;border-left:3px solid #ef4444;padding:12px 16px;border-radius:8px;margin-bottom:8px;">'
        f'<span style="color:#ef4444;font-weight:700;font-size:0.85rem;margin-right:12px;">{i+1:02d}</span>'
        f'<span style="color:#cbd5e1;font-size:0.9rem;">{rec}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("---")


# ── MODULE 8: EXECUTIVE TRUST SUMMARY ────────────────────────────────────────

st.markdown("#### Executive Trust Summary")

critical_count = sum(1 for a in alerts if a[0] == "CRITICAL")
warning_count  = sum(1 for a in alerts if a[0] == "WARNING")
watch_count    = sum(1 for a in alerts if a[0] == "WATCH")

summary_rows = [
    ("Ecosystem",                    s["ecosystem_name"]),
    ("Domain",                       f'{s["domain"]} · {s["agent_type"]}'),
    ("Trust Verdict",                verdict),
    ("Third-Party Trust Score",      f'{s["third_party_trust_score"]} / 100'),
    ("API Reliability Score",        f'{s["api_reliability_score"]} / 100'),
    ("Partner Stability Index",      f'{s["partner_stability_index"]} / 100'),
    ("Composite Ecosystem Risk",     f'{composite_risk} / 100  ({risk_label})'),
    ("Delegated Authority Exposure", f'{s["delegated_authority_exposure"]}%'),
    ("External Dependency Risk",     f'{s["external_dependency_risk_kpi"]} / 100'),
    ("Active Alerts",                f'{critical_count} Critical · {warning_count} Warning · {watch_count} Watch'),
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
        '<div style="background:#0f172a;border:1px solid rgba(239,68,68,0.2);border-radius:14px;padding:24px 28px;">'
        '<h4 style="color:white;margin:0 0 16px 0;">Ecosystem Trust Report</h4>'
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
        '<div style="background:#0a0f1e;border:1px solid rgba(239,68,68,0.2);border-radius:10px;padding:16px 18px;">'
        '<div style="color:#fca5a5;font-size:0.8rem;font-weight:700;margin-bottom:6px;">MONITORING CADENCE</div>'
        '<div style="color:#64748b;font-size:0.8rem;line-height:1.7;">'
        'Continuous third-party trust signal ingestion<br>'
        'Ecosystem risk assessment: every execution cycle<br>'
        'Boundary review: every governance period<br>'
        'Executive summary: on-demand or scheduled'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown(
    '<p style="color:#334155;font-size:0.75rem;text-align:center;margin-top:8px;">'
    'Treasurety Shield™ — Third-Party &amp; Ecosystem Governance<br>'
    'Partner-ready · White-label capable · Trust signals feed Treasurety Govern policy engine'
    '</p>',
    unsafe_allow_html=True
)
