import streamlit as st
import json
from services.evaluator import evaluate_action
from services.ui_helpers import decision_color
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

with open("data/scenarios.json") as f:
    actions = json.load(f)

scenario_map = {
    "Invoice_ACME_Approved_18K.pdf":  "ACT-002",
    "Invoice_Duplicate_125K.pdf":     "ACT-001",
    "Vendor_Bank_Update_Request.pdf": "ACT-003",
    "Treasury_Transfer_Exception.csv":"ACT-008",
    "Contract_Approval_Request.pdf":  "ACT-011"
}

artifact_metadata = {
    "Invoice_ACME_Approved_18K.pdf":  {"counterparty": "ACME Industrial",         "amount": "$18,000",  "objective": "Payment Authorization Request"},
    "Invoice_Duplicate_125K.pdf":     {"counterparty": "Global Supply Corp",       "amount": "$125,000", "objective": "Payment Authorization Request"},
    "Vendor_Bank_Update_Request.pdf": {"counterparty": "NorthBridge Logistics",    "amount": "$92,000",  "objective": "Counterparty Record Update"},
    "Treasury_Transfer_Exception.csv":{"counterparty": "Treasury Operations",      "amount": "$250,000", "objective": "Off-Hours Treasury Transfer"},
    "Contract_Approval_Request.pdf":  {"counterparty": "Meridian Consulting Group","amount": "$240,000", "objective": "Contract Approval Request"},
}

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Governance Flow")
st.caption("Enterprise context enters. AI agent proposes. Treasurety governs.")

st.markdown(
    '<div style="background:#0f172a;border-left:4px solid #3b82f6;padding:12px 18px;border-radius:8px;margin-bottom:16px;font-size:0.85rem;color:#94a3b8;">'
    '<strong style="color:#60a5fa;">Financial Proving Environment</strong> — '
    'demonstrating Treasurety governance runtime on autonomous financial execution. '
    'The same runtime governs any autonomous execution domain.'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")
st.subheader("Select an Artifact to Ingest")

st.markdown(
    '<style>div.stButton > button {background:#1e3a5f !important;border:1px solid #3b82f6 !important;color:#7dd3fc !important;border-radius:12px !important;min-height:90px !important;white-space:normal !important;font-weight:600 !important;} div.stButton > button:hover {background:#1e4a7a !important;border-color:#60a5fa !important;}</style>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)
selected_artifact = None

with col1:
    if st.button("📄 Invoice_ACME_Approved_18K.pdf"):
        selected_artifact = "Invoice_ACME_Approved_18K.pdf"
with col2:
    if st.button("📄 Invoice_Duplicate_125K.pdf"):
        selected_artifact = "Invoice_Duplicate_125K.pdf"
with col3:
    if st.button("📄 Vendor_Bank_Update_Request.pdf"):
        selected_artifact = "Vendor_Bank_Update_Request.pdf"
with col4:
    if st.button("📊 Treasury_Transfer_Exception.csv"):
        selected_artifact = "Treasury_Transfer_Exception.csv"
with col5:
    if st.button("📄 Contract_Approval_Request.pdf"):
        selected_artifact = "Contract_Approval_Request.pdf"

st.markdown("---")
st.file_uploader("Production artifact ingestion interface", disabled=True)

if selected_artifact:
    proposed = next(a for a in actions if a["id"] == scenario_map[selected_artifact])
    evaluation = evaluate_action(proposed)
    color = decision_color(evaluation["decision"])
    artifact = artifact_metadata[selected_artifact]
    counterparty = proposed.get("counterparty", proposed.get("vendor_name", "—"))

    st.success(f"Artifact ingested: {selected_artifact}")
    st.markdown("---")

    st.subheader("Structured Extraction")
    st.write(f"**Counterparty:** {artifact['counterparty']}")
    st.write(f"**Scope Value:** {artifact['amount']}")
    st.write(f"**AI Proposed Objective:** {artifact['objective']}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Proposed Autonomous Action")
        st.write(f"**Action Type:** {proposed['action_type']}")
        st.write(f"**Counterparty:** {counterparty}")
        if proposed["amount"] > 0:
            st.write(f"**Scope Value:** ${proposed['amount']:,.0f}")
        st.write(f"**Agent Confidence:** {int(proposed['confidence'] * 100)}%")
        st.write(f"**Agent ID:** {proposed['agent_id']}")

    with col2:
        st.markdown(
            '<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Governance Trust Evaluation</div>',
            unsafe_allow_html=True
        )
        desc_map = {
            "ALLOW":    "Action within trusted execution bounds.",
            "HOLD":     "Governance review required before execution.",
            "ESCALATE": "Human authorization required.",
            "BLOCK":    "Policy boundary breached. Execution denied.",
        }
        d = evaluation["decision"]
        st.markdown(
            f'<div style="background:{color};border-radius:16px;padding:24px 28px;text-align:center;">'
            f'<div style="color:rgba(255,255,255,0.7);font-size:0.78rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">GOVERNANCE DECISION</div>'
            f'<div style="color:white;font-size:2rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">{d}</div>'
            f'<div style="color:rgba(255,255,255,0.85);font-size:0.88rem;">Risk Score: {evaluation["risk_score"]}/100</div>'
            f'<div style="color:rgba(255,255,255,0.7);font-size:0.82rem;margin-top:6px;">{desc_map.get(d, "")}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.subheader("Execution Risk Signals")

    if evaluation["explanations"]:
        for finding in evaluation["explanations"]:
            st.write(f"• {finding}")
    else:
        st.success("No execution risk signals detected.")

    st.markdown("---")

    if evaluation["risk_score"] <= 25:
        if st.button("Authorize Execution"):
            st.success("Execution authorized by Treasurety governance runtime.")
    else:
        if st.button("Escalate to Governance Control Plane"):
            st.success("Proposed action escalated to governance control plane.")
