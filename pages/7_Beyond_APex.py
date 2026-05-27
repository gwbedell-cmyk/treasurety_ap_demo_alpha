import streamlit as st

st.set_page_config(layout="wide")

st.title("Treasurety Platform")
st.caption("Trust infrastructure modules — governance runtime at every layer of autonomous execution")

st.markdown("---")

st.markdown("""
<div style="
    background: #0f172a;
    border-left: 4px solid #3b82f6;
    padding: 16px 20px;
    border-radius: 10px;
    margin-bottom: 28px;
    color: #94a3b8;
    font-size: 0.9rem;
">
    Treasurety is a platform, not a single product.
    Each module extends governance capability — from runtime enforcement to memory, simulation, and shields.
</div>
""", unsafe_allow_html=True)

# ── ACTIVE MODULE ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: #0f172a;
    border: 2px solid #3b82f6;
    padding: 28px 32px;
    border-radius: 16px;
    margin-bottom: 12px;
">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
        <div style="
            background: #3b82f6;
            color: white;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 3px 12px;
            border-radius: 999px;
        ">ACTIVE</div>
        <h2 style="color:white; margin:0;">Treasurety Govern</h2>
    </div>
    <p style="color:#94a3b8; margin:0 0 12px 0; font-size:0.95rem;">
        Core governance runtime for autonomous execution.
        Policy enforcement, authority validation, trust verification,
        intervention controls, and decision provenance.
    </p>
    <div style="display:flex; flex-wrap:wrap; gap:8px;">
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">Policy Engine</span>
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">Authority Validation</span>
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">Trust Verification</span>
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">Intervention Console</span>
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">Decision Provenance</span>
        <span style="background:#1e3a5f; color:#93c5fd; padding:4px 12px; border-radius:6px; font-size:0.8rem;">ALLOW / HOLD / ESCALATE / BLOCK</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    "<div style='text-align:center; color:#334155; font-size:1.4rem; margin:4px 0;'>↓</div>",
    unsafe_allow_html=True
)

# ── ROADMAP MODULES ─────────────────────────────────────────────────────────────
roadmap_modules = [
    {
        "name": "Treasurety Assess",
        "tagline": "Pre-execution risk intelligence for autonomous actions.",
        "description": (
            "Deep counterparty assessment, contract compliance validation, "
            "and authority scope analysis before the action reaches the runtime. "
            "Assess reduces runtime load by surfacing risk earlier in the agent lifecycle."
        ),
        "tags": ["Counterparty Intelligence", "Contract Validation", "Pre-Flight Risk", "Scope Analysis"],
    },
    {
        "name": "Treasurety Monitor",
        "tagline": "Continuous observability across all autonomous agent activity.",
        "description": (
            "Live telemetry on agent behavior, execution patterns, drift detection, "
            "and anomaly identification across agent fleets. "
            "Monitor feeds trust signal data back into the Govern runtime."
        ),
        "tags": ["Agent Telemetry", "Drift Detection", "Behavioral Anomaly", "Trust Signal Feed"],
    },
    {
        "name": "Treasurety Shield",
        "tagline": "Adversarial protection and trust boundary enforcement.",
        "description": (
            "Protects the governance runtime against prompt injection, "
            "agent impersonation, delegation forgery, and replay attacks. "
            "Shield hardens the trust surface of the entire Treasurety platform."
        ),
        "tags": ["Prompt Injection Defense", "Agent Impersonation Detection", "Replay Prevention", "Trust Hardening"],
    },
    {
        "name": "Treasurety Simulate",
        "tagline": "Governance simulation engine for policy design and stress-testing.",
        "description": (
            "Run synthetic agent fleets against proposed policy configurations. "
            "Simulate edge cases, adversarial inputs, and governance failure modes "
            "before deploying policy changes to production."
        ),
        "tags": ["Policy Stress Testing", "Synthetic Agent Fleets", "Failure Mode Analysis", "Pre-Deploy Simulation"],
    },
    {
        "name": "Treasurety Memory",
        "tagline": "Persistent governance context across agent sessions and actions.",
        "description": (
            "Stores execution history, trust signals, counterparty behavior patterns, "
            "and override precedents. Memory enables governance decisions that improve "
            "over time — informed by what has happened before."
        ),
        "tags": ["Execution History", "Trust Signal Persistence", "Override Precedent", "Adaptive Governance"],
    },
]

for idx, module in enumerate(roadmap_modules):
    st.markdown(
        f"""
        <div style="
            background: #1e293b;
            border: 1px solid #334155;
            padding: 24px 28px;
            border-radius: 14px;
            margin-bottom: 8px;
            opacity: 0.92;
        ">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px; flex-wrap:wrap;">
                <div style="
                    background: #334155;
                    color: #94a3b8;
                    font-weight: 700;
                    font-size: 0.73rem;
                    padding: 3px 12px;
                    border-radius: 999px;
                    letter-spacing: 0.06em;
                ">COMING NEXT</div>
                <h3 style="color:white; margin:0;">{module['name']}</h3>
                <span style="color:#64748b; font-size:0.9rem; font-style:italic;">{module['tagline']}</span>
            </div>
            <p style="color:#94a3b8; margin:0 0 14px 0; font-size:0.88rem;">{module['description']}</p>
            <div style="display:flex; flex-wrap:wrap; gap:6px;">
                {"".join(
                    f'<span style="background:#0f172a; color:#64748b; padding:3px 10px; border-radius:6px; font-size:0.78rem;">{tag}</span>'
                    for tag in module["tags"]
                )}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if idx < len(roadmap_modules) - 1:
        st.markdown(
            "<div style='text-align:center; color:#1e293b; font-size:1.2rem; margin:2px 0;'>↓</div>",
            unsafe_allow_html=True
        )

st.markdown("---")

st.markdown("""
<div style="
    text-align: center;
    padding: 24px;
    color: #475569;
    font-size: 0.9rem;
">
    <p style="margin:0 0 6px 0;">
        <strong style="color:#64748b;">Treasurety</strong> — Trust Infrastructure for Autonomous Execution
    </p>
    <p style="margin:0; font-style:italic;">
        AI can think. Treasurety decides whether it gets to act.
    </p>
</div>
""", unsafe_allow_html=True)
