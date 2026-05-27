import streamlit as st
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

st.title("Platform Roadmap")
st.caption("Treasurety modules — governance runtime at every layer of autonomous execution")

st.markdown("---")

st.markdown(
    '<div style="background:#0f172a;border-left:4px solid #3b82f6;padding:16px 20px;border-radius:10px;margin-bottom:28px;color:#94a3b8;font-size:0.9rem;">'
    'Treasurety is a platform, not a single product. '
    'Each module extends governance capability — from runtime enforcement to memory, simulation, and shields.'
    '</div>',
    unsafe_allow_html=True
)

# ── ACTIVE MODULE ─────────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#0f172a;border:2px solid #3b82f6;padding:28px 32px;border-radius:16px;margin-bottom:12px;">'
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
    '<div style="background:#3b82f6;color:white;font-weight:700;font-size:0.75rem;padding:3px 12px;border-radius:999px;">ACTIVE</div>'
    '<h2 style="color:white;margin:0;">Treasurety Govern</h2>'
    '</div>'
    '<p style="color:#94a3b8;margin:0 0 12px 0;font-size:0.95rem;">Core governance runtime for autonomous execution. Policy enforcement, authority validation, trust verification, intervention controls, and decision provenance.</p>'
    '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Policy Engine</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Authority Validation</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Trust Verification</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Intervention Console</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Decision Provenance</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">ALLOW / HOLD / ESCALATE / BLOCK</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;color:#334155;font-size:1.4rem;margin:4px 0;">↓</div>',
    unsafe_allow_html=True
)

# ── SECOND ACTIVE MODULE ───────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#0f172a;border:2px solid #3b82f6;padding:28px 32px;border-radius:16px;margin-bottom:12px;">'
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
    '<div style="background:#3b82f6;color:white;font-weight:700;font-size:0.75rem;padding:3px 12px;border-radius:999px;">ACTIVE</div>'
    '<h2 style="color:white;margin:0;">Treasurety Assess</h2>'
    '</div>'
    '<p style="color:#94a3b8;margin:0 0 12px 0;font-size:0.95rem;">Pre-deployment readiness and risk assurance for autonomous systems. Authority scope analysis, behavioral drift assessment, ecosystem exposure mapping, and operational governance scoring before deployment.</p>'
    '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Authority Scope Analysis</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Behavioral Drift Risk</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Ecosystem Exposure</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Ops Governance Scoring</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Deployment Verdict</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;color:#334155;font-size:1.4rem;margin:4px 0;">↓</div>',
    unsafe_allow_html=True
)

# ── THIRD ACTIVE MODULE ────────────────────────────────────────────────────────
st.markdown(
    '<div style="background:#0f172a;border:2px solid #3b82f6;padding:28px 32px;border-radius:16px;margin-bottom:12px;">'
    '<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">'
    '<div style="background:#3b82f6;color:white;font-weight:700;font-size:0.75rem;padding:3px 12px;border-radius:999px;">ACTIVE</div>'
    '<h2 style="color:white;margin:0;">Treasurety Monitor</h2>'
    '</div>'
    '<p style="color:#94a3b8;margin:0 0 12px 0;font-size:0.95rem;">Continuous drift detection and governance assurance for autonomous systems. Live telemetry on agent behavior, drift scoring across five dimensions, alert engine, and assurance verdict — all feeding trust signal data back into the Govern runtime.</p>'
    '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Drift Detection Engine</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Behavioral Anomaly</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Trust Signal Feed</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Alert Engine</span>'
    '<span style="background:#1e3a5f;color:#93c5fd;padding:4px 12px;border-radius:6px;font-size:0.8rem;">Assurance Verdict</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="text-align:center;color:#334155;font-size:1.4rem;margin:4px 0;">↓</div>',
    unsafe_allow_html=True
)

# ── ROADMAP MODULES ───────────────────────────────────────────────────────────
roadmap_modules = [
    {
        "name": "Treasurety Shield",
        "tagline": "Adversarial protection and trust boundary enforcement.",
        "description": "Protects the governance runtime against prompt injection, agent impersonation, delegation forgery, and replay attacks. Shield hardens the trust surface of the entire Treasurety platform.",
        "tags": ["Prompt Injection Defense", "Agent Impersonation Detection", "Replay Prevention", "Trust Hardening"],
    },
    {
        "name": "Treasurety Simulate",
        "tagline": "Governance simulation engine for policy design and stress-testing.",
        "description": "Run synthetic agent fleets against proposed policy configurations. Simulate edge cases, adversarial inputs, and governance failure modes before deploying policy changes to production.",
        "tags": ["Policy Stress Testing", "Synthetic Agent Fleets", "Failure Mode Analysis", "Pre-Deploy Simulation"],
    },
    {
        "name": "Treasurety Memory",
        "tagline": "Persistent governance context across agent sessions and actions.",
        "description": "Stores execution history, trust signals, counterparty behavior patterns, and override precedents. Memory enables governance decisions that improve over time — informed by what has happened before.",
        "tags": ["Execution History", "Trust Signal Persistence", "Override Precedent", "Adaptive Governance"],
    },
]

for idx, module in enumerate(roadmap_modules):
    tags_html = "".join(
        f'<span style="background:#0f172a;color:#64748b;padding:3px 10px;border-radius:6px;font-size:0.78rem;">{tag}</span>'
        for tag in module["tags"]
    )
    st.markdown(
        f'<div style="background:#1e293b;border:1px solid #334155;padding:24px 28px;border-radius:14px;margin-bottom:8px;">'
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap;">'
        f'<div style="background:#334155;color:#94a3b8;font-weight:700;font-size:0.73rem;padding:3px 12px;border-radius:999px;letter-spacing:0.06em;">COMING NEXT</div>'
        f'<h3 style="color:white;margin:0;">{module["name"]}</h3>'
        f'<span style="color:#64748b;font-size:0.9rem;font-style:italic;">{module["tagline"]}</span>'
        f'</div>'
        f'<p style="color:#94a3b8;margin:0 0 14px 0;font-size:0.88rem;">{module["description"]}</p>'
        f'<div style="display:flex;flex-wrap:wrap;gap:6px;">{tags_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if idx < len(roadmap_modules) - 1:
        st.markdown(
            '<div style="text-align:center;color:#1e293b;font-size:1.2rem;margin:2px 0;">↓</div>',
            unsafe_allow_html=True
        )

st.markdown("---")

st.markdown(
    '<p style="text-align:center;color:#475569;font-size:0.9rem;padding:16px 0;">'
    '<strong style="color:#64748b;">Treasurety</strong> — Trust Infrastructure for Autonomous Execution<br>'
    '<em>AI can think. Treasurety decides whether it gets to act.</em>'
    '</p>',
    unsafe_allow_html=True
)
