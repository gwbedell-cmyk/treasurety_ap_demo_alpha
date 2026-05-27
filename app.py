import streamlit as st

st.set_page_config(
    page_title="Treasurety",
    page_icon="🛡️",
    layout="wide"
)

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<div style="padding: 8px 0 4px 0;">
    <h1 style="margin-bottom: 2px;">🛡️ Treasurety</h1>
    <p style="font-size: 1.25rem; color: #94a3b8; margin-top: 0;">
        Trust Infrastructure for Autonomous Execution
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Proposed Actions Today", "143", "+12")

with col2:
    st.metric("Governed Execution Value", "$612,400", "+8.2%")

with col3:
    st.metric("Blocked Executions", "13", "+3")

with col4:
    st.metric("Hold Queue", "21", "-4")

st.markdown("---")

st.info(
    "Treasurety governance runtime online. Trust verification and policy enforcement active."
)

st.markdown("---")

left, right = st.columns([3, 2])

with left:
    st.markdown("### Core Thesis")
    st.markdown("""
<div style="
    background: #0f172a;
    border-left: 4px solid #3b82f6;
    padding: 24px 28px;
    border-radius: 12px;
    margin-bottom: 16px;
">
    <p style="font-size: 1.4rem; font-weight: 600; color: white; margin: 0 0 8px 0;">
        AI can think.
    </p>
    <p style="font-size: 1.4rem; font-weight: 600; color: #60a5fa; margin: 0;">
        Treasurety decides whether it gets to act.
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
Treasurety is **governance middleware for autonomous systems** — the runtime layer that
enforces bounded authority, verifies trust, and controls whether AI agents
are permitted to execute.

Builders and enterprises embed Treasurety to ensure no autonomous action
proceeds without validation against policy, authority chain, and trust signals.
""")

with right:
    st.markdown("### Governance Controls")
    st.markdown("""
<div style="display: flex; flex-direction: column; gap: 8px;">
""", unsafe_allow_html=True)

    controls = [
        ("Bounded Authority", "Agents act only within delegated scope"),
        ("Runtime Policy Enforcement", "Every action checked against live policy"),
        ("Trust Verification", "Counterparty and agent trust validated"),
        ("Intervention Controls", "Pause, override, escalate, revoke"),
        ("Decision Provenance", "Why every governance decision occurred"),
        ("Execution Authorization", "Final gate before any action executes"),
    ]

    for label, desc in controls:
        st.markdown(f"""
<div style="
    background: #1e293b;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
">
    <span style="color: #60a5fa; font-weight: 600; font-size: 0.85rem;">{label}</span>
    <span style="color: #94a3b8; font-size: 0.82rem; margin-left: 8px;">{desc}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.caption(
    "Financial domain active as proving environment — "
    "Treasurety governance infrastructure operates across all autonomous execution domains."
)
