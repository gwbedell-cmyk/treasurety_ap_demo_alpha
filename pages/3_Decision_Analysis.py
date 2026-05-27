import streamlit as st
import json
from datetime import datetime

from services.evaluator import evaluate_action
from services.audit import load_audit_log, save_audit_log
from services.ui_helpers import decision_color

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

with open("data/scenarios.json") as f:
    actions = json.load(f)

st.title("Decision Provenance")
st.caption("Forensic review and governance intervention for autonomous execution")

counterparty_key = lambda x: x.get("counterparty", x.get("vendor_name", "—"))

selected = st.selectbox(
    "Select Proposed Autonomous Action",
    actions,
    format_func=lambda x: f"{x['id']} — {counterparty_key(x)}"
)

evaluation = evaluate_action(selected)
color = decision_color(evaluation["decision"])
counterparty = counterparty_key(selected)
action_ref = selected.get("action_ref", selected.get("invoice_id", "—"))

st.subheader("Proposed Autonomous Action")

col_a, col_b = st.columns(2)

with col_a:
    st.write(f"**Agent:** {selected['agent_id']}")
    st.write(f"**Action Type:** {selected['action_type']}")
    st.write(f"**Counterparty:** {counterparty}")
    st.write(f"**Action Reference:** {action_ref}")
    if selected["amount"] > 0:
        st.write(f"**Scope Value:** ${selected['amount']:,.0f}")
    st.write(f"**Agent Confidence:** {int(selected['confidence'] * 100)}%")

with col_b:
    st.markdown("**Authority Context**")
    st.markdown(f"""
<div style="
    background: #1e293b;
    padding: 16px;
    border-radius: 12px;
    font-size: 0.85rem;
    color: #94a3b8;
">
    <div style="margin-bottom: 6px;">
        <span style="color: #60a5fa; font-weight: 600;">Delegated Scope:</span> Single-action authorization
    </div>
    <div style="margin-bottom: 6px;">
        <span style="color: #60a5fa; font-weight: 600;">Policy Source:</span> Enterprise Governance Ruleset v2
    </div>
    <div>
        <span style="color: #60a5fa; font-weight: 600;">Authority Chain:</span> Agent → Operator → Policy Engine
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader("Execution Risk Signals")

if evaluation["explanations"]:
    for item in evaluation["explanations"]:
        st.write(f"• {item}")
else:
    st.success("No execution risk signals detected.")

st.markdown("---")

st.markdown("### Governance Trust Evaluation")

trust_col = st.columns([1, 1])

with trust_col[0]:
    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:24px;
            border-radius:16px;
            text-align:center;
            border:1px solid rgba(255,255,255,0.1);
        ">
            <h2 style="color:white; margin-bottom:8px;">{evaluation['decision']}</h2>
            <h3 style="color:white; margin:0;">Risk Score: {evaluation['risk_score']}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with trust_col[1]:
    st.markdown("**Decision Provenance**")

    if evaluation["triggered_policies"]:
        st.markdown("Governance decision triggered by:")
        for policy in evaluation["triggered_policies"]:
            st.write(f"• {policy}")
    else:
        st.write("No policies triggered — clean execution path.")

    decision = evaluation["decision"]
    if decision == "BLOCK":
        st.error("Blocked due to policy boundary breach.")
    elif decision == "ESCALATE":
        st.warning("Escalated — risk profile requires human authorization.")
    elif decision == "HOLD":
        st.warning("Held — governance review required before execution.")
    else:
        st.success("Authorized — action within trusted execution bounds.")

st.markdown("---")

st.subheader("Intervention Console")

button_col = st.columns([1, 1, 1, 4])

risk = evaluation["risk_score"]

with button_col[0]:
    execute_clicked = False
    if risk >= 70:
        execute_clicked = st.button("Override")
    else:
        execute_clicked = st.button("Authorize")

with button_col[1]:
    hold_clicked = False
    if risk >= 70:
        hold_clicked = st.button("Escalate")
    else:
        hold_clicked = st.button("Hold")

with button_col[2]:
    third_clicked = False
    if 40 <= risk < 70:
        third_clicked = st.button("Escalate")
    elif risk >= 70:
        third_clicked = st.button("Block")

alert_col = st.columns([1, 1])

with alert_col[0]:
    if execute_clicked:
        if risk >= 70:
            st.warning("Override pathway initiated. Decision provenance logged.")
        else:
            st.success("Execution authorized.")

    if hold_clicked:
        if risk >= 70:
            st.warning("Action escalated for human review.")
        else:
            st.warning("Execution placed on hold.")

    if third_clicked:
        if risk >= 70:
            st.error("Execution blocked.")
        else:
            st.warning("Action escalated for human review.")

st.markdown("---")

st.subheader("Human Intervention — Authority Override")

override_reason = st.text_area(
    "Business justification required for governance override"
)

if st.button("Record Override Decision"):
    if override_reason.strip():
        log = load_audit_log()

        log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "action_id": selected["id"],
            "agent_id": selected["agent_id"],
            "counterparty": counterparty,
            "decision": "HUMAN OVERRIDE",
            "risk_score": evaluation["risk_score"],
            "triggered_policies": evaluation["triggered_policies"],
            "findings": [override_reason]
        })

        save_audit_log(log)

        st.success("Override recorded in Decision Provenance Log.")
    else:
        st.error("Override justification required.")
