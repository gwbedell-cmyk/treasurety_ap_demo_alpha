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

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #060d1a 0%, #0d1f3c 100%);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 20px;
    padding: 48px 52px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
">
    <div style="
        position: absolute; top: 0; right: 0; width: 300px; height: 100%;
        background: radial-gradient(ellipse at top right, rgba(59,130,246,0.08), transparent 70%);
        pointer-events: none;
    "></div>

    <div style="margin-bottom: 6px;">
        <span style="
            background: rgba(59,130,246,0.15);
            color: #7dd3fc;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 4px 14px;
            border-radius: 999px;
            border: 1px solid rgba(59,130,246,0.3);
        ">GOVERNANCE RUNTIME ACTIVE</span>
    </div>

    <h1 style="
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 16px 0 6px 0;
        letter-spacing: -0.02em;
        line-height: 1.1;
    ">🛡️ Treasurety</h1>

    <p style="
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0 0 28px 0;
        font-weight: 400;
    ">Trust Infrastructure for Autonomous Execution</p>

    <div style="
        border-top: 1px solid rgba(255,255,255,0.07);
        padding-top: 24px;
        display: flex;
        flex-direction: column;
        gap: 6px;
    ">
        <p style="
            font-size: 1.6rem;
            font-weight: 700;
            color: #e2e8f0;
            margin: 0;
            line-height: 1.3;
        ">AI can think.</p>
        <p style="
            font-size: 1.6rem;
            font-weight: 700;
            color: #60a5fa;
            margin: 0;
            line-height: 1.3;
        ">Treasurety decides whether it gets to act.</p>
        <p style="
            color: #64748b;
            font-size: 0.92rem;
            margin: 10px 0 0 0;
            max-width: 620px;
        ">
            Governance middleware for autonomous systems — the runtime layer that enforces
            bounded authority, verifies trust, and controls whether AI agents are permitted to execute.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── RUNTIME STATUS ────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: rgba(22, 163, 74, 0.08);
    border: 1px solid rgba(22, 163, 74, 0.3);
    border-radius: 10px;
    padding: 10px 18px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
">
    <span style="
        display: inline-block;
        width: 8px; height: 8px;
        background: #16a34a;
        border-radius: 50%;
        box-shadow: 0 0 8px #16a34a;
    "></span>
    <span style="color: #86efac; font-size: 0.85rem; font-weight: 600;">
        Governance runtime online — policy enforcement, trust verification, and intervention controls active
    </span>
</div>
""", unsafe_allow_html=True)

# ── GOVERNANCE METRICS ────────────────────────────────────────────────────────
st.markdown("#### Runtime Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Actions Evaluated", "143", "+12")
with col2:
    st.metric("ALLOW Decisions", "96", "+9")
with col3:
    st.metric("HOLD Queue", "21", "-4")
with col4:
    st.metric("Escalations", "13", "+2")

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric("Blocked Actions", "13", "+3")
with col6:
    st.metric("Third-Party Trust Events", "8", "+1")
with col7:
    st.metric("Human Interventions", "5", "0")
with col8:
    st.metric("Policy Exceptions", "3", "+1")

st.markdown("---")

# ── GOVERNANCE CONTROLS ───────────────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    st.markdown("#### What Treasurety Governs")

    st.markdown("""
<div style="
    background: #0f172a;
    border-left: 4px solid #3b82f6;
    padding: 20px 24px;
    border-radius: 12px;
    color: #94a3b8;
    font-size: 0.92rem;
    line-height: 1.7;
">
    Builders and enterprises embed Treasurety to ensure no autonomous action proceeds
    without validation against policy, authority chain, and trust signals.<br><br>
    Every proposed action — from a finance agent releasing a payment to a procurement agent
    signing a contract to an external vendor AI requesting access — passes through the
    Treasurety governance runtime before execution is permitted.
</div>
""", unsafe_allow_html=True)

with right:
    st.markdown("#### Governance Controls")

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
    background: #0f172a;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
">
    <span style="
        background: rgba(59,130,246,0.12);
        color: #7dd3fc;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 2px 8px;
        border-radius: 4px;
        white-space: nowrap;
    ">{label}</span>
    <span style="color: #64748b; font-size: 0.81rem;">{desc}</span>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<p style="color: #334155; font-size: 0.8rem; text-align: center;">
    Financial domain active as proving environment —
    Treasurety governance runtime operates across all autonomous execution domains.
</p>
""", unsafe_allow_html=True)
