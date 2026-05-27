import streamlit as st
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

st.title("Treasurety Runtime Architecture")
st.caption("Trust infrastructure for autonomous execution — governance model")

st.markdown("---")

st.markdown(
    '<div style="background:#0f172a;border-left:4px solid #3b82f6;padding:16px 20px;border-radius:10px;margin-bottom:24px;color:#94a3b8;font-size:0.9rem;">'
    'Every autonomous action passes through the Treasurety governance runtime before execution is permitted. '
    'No agent acts without clearing authority validation, policy enforcement, and trust verification.'
    '</div>',
    unsafe_allow_html=True
)

steps = [
    {"step": "01", "label": "Autonomous Agent",       "description": "An AI agent — internal, third-party, or delegated — proposes an action to the runtime.", "color": "#1e3a5f", "border": "#3b82f6", "badge": "ENTRY POINT"},
    {"step": "02", "label": "Proposed Action",         "description": "The action is structured: type, scope value, counterparty, authority chain, confidence level.", "color": "#1e293b", "border": "#475569", "badge": "INTAKE"},
    {"step": "03", "label": "Authority Validation",    "description": "Is this agent authorized to propose this class of action? Is the delegation chain intact?", "color": "#1e293b", "border": "#475569", "badge": "VALIDATION"},
    {"step": "04", "label": "Policy Enforcement",      "description": "Runtime policy engine evaluates the action against all active governance policies. Weights accumulate.", "color": "#1e293b", "border": "#475569", "badge": "ENFORCEMENT"},
    {"step": "05", "label": "Trust Verification",      "description": "Counterparty trust signals checked. Anomaly indicators evaluated. Third-party trust state assessed.", "color": "#1e293b", "border": "#475569", "badge": "TRUST"},
    {"step": "06", "label": "Risk Assessment",         "description": "Composite risk score calculated from policy weights, trust signals, and execution context.", "color": "#1e293b", "border": "#475569", "badge": "RISK"},
    {"step": "07", "label": "Governance Decision",     "description": "Runtime issues one of four governance decisions based on risk score and policy state.", "color": "#14532d", "border": "#16a34a", "badge": "DECISION", "decisions": True},
    {"step": "08", "label": "Human Intervention",      "description": "If required (HOLD or ESCALATE), human operator reviews. Controls: pause, override, escalate, revoke, block.", "color": "#451a03", "border": "#f59e0b", "badge": "INTERVENTION"},
    {"step": "09", "label": "Execution Authorization", "description": "ALLOW or approved Override proceeds. Action executes with full provenance recorded.", "color": "#052e16", "border": "#16a34a", "badge": "EXECUTION"},
]

for idx, step in enumerate(steps):
    st.markdown(
        f'<div style="background:{step["color"]};border:1px solid {step["border"]};padding:20px 24px;border-radius:14px;margin-bottom:4px;">'
        f'<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:8px;">'
        f'<div style="background:{step["border"]};color:white;font-weight:700;font-size:0.75rem;padding:3px 10px;border-radius:999px;white-space:nowrap;">{step["badge"]}</div>'
        f'<span style="color:#94a3b8;font-size:0.8rem;font-weight:600;letter-spacing:0.08em;">{step["step"]}</span>'
        f'<h3 style="color:white;margin:0;font-size:1.1rem;">{step["label"]}</h3>'
        f'</div>'
        f'<p style="color:#94a3b8;margin:0;font-size:0.88rem;">{step["description"]}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    if step.get("decisions"):
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        decisions = [
            ("ALLOW",   "#16a34a", "Risk < 40",  "Clean execution path. Action authorized."),
            ("HOLD",    "#f59e0b", "Risk 40–69", "Paused. Governance review required."),
            ("ESCALATE","#ea580c", "Risk 70–89", "Human authorization required before execution."),
            ("BLOCK",   "#dc2626", "Risk ≥ 90",  "Explicit denial. Policy boundary breached."),
        ]
        for col, (label, color, threshold, desc) in zip([d_col1, d_col2, d_col3, d_col4], decisions):
            with col:
                st.markdown(
                    f'<div style="background:{color};padding:14px;border-radius:10px;text-align:center;margin:4px 0;">'
                    f'<div style="color:white;font-weight:700;font-size:1rem;">{label}</div>'
                    f'<div style="color:rgba(255,255,255,0.8);font-size:0.75rem;margin-top:4px;">{threshold}</div>'
                    f'<div style="color:rgba(255,255,255,0.7);font-size:0.73rem;margin-top:6px;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    if idx < len(steps) - 1:
        st.markdown(
            '<div style="text-align:center;color:#475569;font-size:1.4rem;margin:0;">↓</div>',
            unsafe_allow_html=True
        )

st.markdown("---")
st.subheader("Proving Environment")

st.markdown(
    '<div style="background:#1e293b;padding:20px 24px;border-radius:12px;color:#94a3b8;font-size:0.9rem;">'
    '<p style="margin:0 0 10px 0;"><strong style="color:white;">Financial Proving Environment</strong> — '
    'The Treasurety governance runtime was first deployed against autonomous financial execution: '
    'accounts payable, treasury operations, cross-border payments.</p>'
    '<p style="margin:0;">Money is an unforgiving autonomous execution domain — zero error tolerance, high fraud surface, '
    'irreversible consequences. A runtime that governs financial agents governs any agent. '
    'The same policy engine, trust verification, and decision provenance layer operates '
    'across procurement, HR, operations, infrastructure, and multi-agent pipelines.</p>'
    '</div>',
    unsafe_allow_html=True
)
