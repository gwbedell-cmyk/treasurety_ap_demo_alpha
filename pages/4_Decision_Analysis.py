import streamlit as st
import json
from datetime import datetime

from services.evaluator import evaluate_action
from services.audit import load_audit_log, save_audit_log
from services.ui_helpers import decision_color
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_nav()

with open("data/scenarios.json") as f:
    actions = json.load(f)

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Decision Provenance")
st.caption("Forensic review and governance intervention for autonomous execution")

counterparty_key = lambda x: x.get("counterparty", x.get("vendor_name", "—"))

selected = st.selectbox(
    "Select Proposed Autonomous Action",
    actions,
    format_func=lambda x: f"{x['id']} — {counterparty_key(x)}"
)

evaluation  = evaluate_action(selected)
color       = decision_color(evaluation["decision"])
counterparty = counterparty_key(selected)
action_ref  = selected.get("action_ref", selected.get("invoice_id", "—"))

st.markdown("---")

# ── ACTION DETAILS + AUTHORITY CONTEXT ────────────────────────────────────────

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(
        '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Proposed Autonomous Action</div>',
        unsafe_allow_html=True
    )
    details = [
        ("Agent",            selected["agent_id"]),
        ("Action Type",      selected["action_type"]),
        ("Counterparty",     counterparty),
        ("Action Reference", action_ref),
        ("Agent Confidence", f"{int(selected['confidence'] * 100)}%"),
    ]
    if selected["amount"] > 0:
        details.insert(4, ("Scope Value", f"${selected['amount']:,.0f}"))

    rows_html = "".join(
        f'<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
        f'<span style="color:#64748b;font-size:0.85rem;">{label}</span>'
        f'<span style="color:#e2e8f0;font-size:0.85rem;font-weight:600;">{value}</span>'
        f'</div>'
        for label, value in details
    )
    st.markdown(
        '<div style="background:#0f172a;border:1px solid #1e293b;border-radius:12px;padding:18px 20px;">'
        + rows_html +
        '</div>',
        unsafe_allow_html=True
    )

with col_b:
    st.markdown(
        '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Authority Context</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div style="background:#0f172a;border:1px solid #1e3a5f;border-radius:12px;padding:18px 20px;">'
        '<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
        '<span style="color:#64748b;font-size:0.85rem;">Delegated Scope</span>'
        '<span style="color:#e2e8f0;font-size:0.85rem;font-weight:600;">Single-action authorization</span>'
        '</div>'
        '<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
        '<span style="color:#64748b;font-size:0.85rem;">Policy Source</span>'
        '<span style="color:#e2e8f0;font-size:0.85rem;font-weight:600;">Enterprise Governance Ruleset v2</span>'
        '</div>'
        '<div style="display:flex;justify-content:space-between;padding:7px 0;">'
        '<span style="color:#64748b;font-size:0.85rem;">Authority Chain</span>'
        '<span style="color:#e2e8f0;font-size:0.85rem;font-weight:600;">Agent → Operator → Policy Engine</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# ── GOVERNANCE TRUST EVALUATION ───────────────────────────────────────────────

st.markdown(
    '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Governance Trust Evaluation</div>',
    unsafe_allow_html=True
)

trust_left, trust_right = st.columns(2)

with trust_left:
    decision = evaluation["decision"]
    desc_map = {
        "ALLOW":    "Action within trusted execution bounds. Authorization granted.",
        "HOLD":     "Governance review required before execution proceeds.",
        "ESCALATE": "Risk profile requires human authorization.",
        "BLOCK":    "Policy boundary breached. Execution denied.",
    }
    st.markdown(
        f'<div style="background:{color};border-radius:16px;padding:28px 32px;text-align:center;">'
        f'<div style="color:rgba(255,255,255,0.7);font-size:0.8rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">GOVERNANCE DECISION</div>'
        f'<div style="color:white;font-size:2.4rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">{decision}</div>'
        f'<div style="color:rgba(255,255,255,0.85);font-size:0.9rem;">Risk Score: {evaluation["risk_score"]}/100</div>'
        f'<div style="color:rgba(255,255,255,0.7);font-size:0.83rem;margin-top:6px;">{desc_map.get(decision, "")}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with trust_right:
    if evaluation["triggered_policies"]:
        policies_html = "".join(
            f'<div style="background:#0f172a;border-left:3px solid #3b82f6;padding:8px 12px;border-radius:6px;margin-bottom:6px;color:#94a3b8;font-size:0.83rem;">{p}</div>'
            for p in evaluation["triggered_policies"]
        )
        st.markdown(
            '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Triggered Policies</div>'
            + policies_html,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="background:#0f172a;border:1px solid rgba(22,163,74,0.3);border-radius:10px;padding:14px 18px;color:#86efac;font-size:0.88rem;">'
            'No policies triggered — clean execution path.'
            '</div>',
            unsafe_allow_html=True
        )

    if evaluation["explanations"]:
        signals_html = "".join(
            f'<div style="background:#0f172a;border-left:3px solid #ea580c;padding:8px 12px;border-radius:6px;margin-bottom:6px;color:#94a3b8;font-size:0.83rem;">{s}</div>'
            for s in evaluation["explanations"]
        )
        st.markdown(
            '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;margin-top:14px;">Execution Risk Signals</div>'
            + signals_html,
            unsafe_allow_html=True
        )

st.markdown("---")

# ── INTERVENTION CONSOLE ──────────────────────────────────────────────────────

st.markdown(
    '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:14px;">Intervention Console</div>',
    unsafe_allow_html=True
)

risk = evaluation["risk_score"]
button_col = st.columns([1, 1, 1, 4])

with button_col[0]:
    execute_clicked = st.button("Override") if risk >= 70 else st.button("Authorize")
with button_col[1]:
    hold_clicked = st.button("Escalate") if risk >= 70 else st.button("Hold")
with button_col[2]:
    third_clicked = False
    if 40 <= risk < 70:
        third_clicked = st.button("Escalate")
    elif risk >= 70:
        third_clicked = st.button("Block")

if execute_clicked:
    st.warning("Override pathway initiated. Decision provenance logged.") if risk >= 70 else st.success("Execution authorized.")
if hold_clicked:
    st.warning("Action escalated for human review.") if risk >= 70 else st.warning("Execution placed on hold.")
if third_clicked:
    st.error("Execution blocked.") if risk >= 70 else st.warning("Action escalated for human review.")

st.markdown("---")

# ── HUMAN INTERVENTION — AUTHORITY OVERRIDE ────────────────────────────────────

st.markdown(
    '<div style="background:#0f172a;border:1px solid rgba(59,130,246,0.2);border-radius:14px;padding:22px 26px;margin-bottom:16px;">'
    '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Human Intervention — Authority Override</div>'
    '<div style="color:#64748b;font-size:0.83rem;">Business justification is required and logged for all governance overrides. Override decisions are permanently recorded in the Decision Provenance Log.</div>'
    '</div>',
    unsafe_allow_html=True
)

override_reason = st.text_area(
    "Business justification for governance override",
    label_visibility="collapsed",
    placeholder="Enter business justification for governance override..."
)

if st.button("Record Override Decision", type="primary"):
    if override_reason.strip():
        log = load_audit_log()
        log.append({
            "timestamp":         datetime.utcnow().isoformat(),
            "action_id":         selected["id"],
            "agent_id":          selected["agent_id"],
            "counterparty":      counterparty,
            "decision":          "HUMAN OVERRIDE",
            "risk_score":        evaluation["risk_score"],
            "triggered_policies":evaluation["triggered_policies"],
            "findings":          [override_reason],
        })
        save_audit_log(log)
        st.success("Override recorded in Decision Provenance Log.")
    else:
        st.error("Override justification required.")
