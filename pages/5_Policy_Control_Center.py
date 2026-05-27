import streamlit as st
import json
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

with open("data/policies.json") as f:
    policies = json.load(f)

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Policy Control Center")
st.caption("Runtime policy enforcement — governance controls for autonomous execution")

st.markdown(
    '<div style="background:#0f172a;border-left:4px solid #3b82f6;padding:14px 18px;border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">'
    'Policy weights accumulate against each proposed action to produce a composite risk score. Active policies define the governance boundary for autonomous execution.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# ── POLICY CARDS ──────────────────────────────────────────────────────────────

def weight_color(w):
    if w >= 30: return "#dc2626"
    if w >= 20: return "#ea580c"
    if w >= 10: return "#f59e0b"
    return             "#16a34a"

for policy in policies:
    toggle_key = f"pcc_toggle_{policy['id']}"
    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = policy["enabled"]

    is_enabled   = st.session_state[toggle_key]
    border_color = "#3b82f6" if is_enabled else "#1e293b"
    wc           = weight_color(policy["weight"])

    card_col, toggle_col = st.columns([5, 1])

    with card_col:
        st.markdown(
            f'<div style="background:#0f172a;border:1px solid {border_color};border-radius:12px;padding:16px 20px;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap;">'
            f'<span style="background:rgba(59,130,246,0.12);color:#7dd3fc;font-weight:700;font-size:0.78rem;padding:2px 10px;border-radius:4px;font-family:monospace;">{policy["id"]}</span>'
            f'<span style="color:white;font-weight:600;font-size:0.9rem;">{policy["name"]}</span>'
            f'<span style="background:{wc};color:white;font-size:0.7rem;font-weight:700;padding:2px 8px;border-radius:999px;">W: {policy["weight"]}</span>'
            f'</div>'
            f'<div style="color:#64748b;font-size:0.83rem;">{policy["description"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with toggle_col:
        st.markdown('<div style="padding-top:12px;"></div>', unsafe_allow_html=True)
        st.toggle("Enabled" if is_enabled else "Disabled", key=toggle_key)

    st.markdown('<div style="margin-bottom:4px;"></div>', unsafe_allow_html=True)
