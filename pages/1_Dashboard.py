import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.evaluator import evaluate_action
from services.audit import record_decision, load_audit_log

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

with open("data/scenarios.json") as f:
    actions = json.load(f)

evaluations = []

for action in actions:
    evaluation = evaluate_action(action)
    record_decision(action, evaluation)
    evaluations.append(evaluation)

allowed   = sum(1 for e in evaluations if e["decision"] == "ALLOW")
held      = sum(1 for e in evaluations if e["decision"] == "HOLD")
escalated = sum(1 for e in evaluations if e["decision"] == "ESCALATE")
blocked   = sum(1 for e in evaluations if e["decision"] == "BLOCK")
third_party = sum(1 for a in actions if a["agent_id"].startswith("EXT-"))

audit_log = load_audit_log()
human_interventions = sum(1 for r in audit_log if r.get("decision") == "HUMAN OVERRIDE")
policy_exceptions   = sum(1 for e in evaluations if len(e["triggered_policies"]) > 0)

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Governance Dashboard")
st.caption("Treasurety runtime — live governance state across all proposed autonomous actions")

# ── ROW 1 METRICS ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Actions Evaluated", len(actions))
with col2:
    st.metric("ALLOW Decisions", allowed)
with col3:
    st.metric("HOLD Queue", held)
with col4:
    st.metric("Escalations", escalated)

# ── ROW 2 METRICS ─────────────────────────────────────────────────────────────
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric("Blocked Actions", blocked)
with col6:
    st.metric("Third-Party Trust Events", third_party)
with col7:
    st.metric("Human Interventions", human_interventions)
with col8:
    st.metric("Policy Exceptions", policy_exceptions)

st.markdown("---")

# ── CHARTS ────────────────────────────────────────────────────────────────────
color_map = {
    "ALLOW":   "#16a34a",
    "HOLD":    "#f59e0b",
    "ESCALATE":"#ea580c",
    "BLOCK":   "#dc2626"
}

rows = []
for action, evaluation in zip(actions, evaluations):
    rows.append({
        "Counterparty":       action.get("counterparty", action.get("vendor_name", "—")),
        "Agent":              action["agent_id"],
        "Governance Decision":evaluation["decision"],
        "Risk Score":         evaluation["risk_score"],
        "Action Type":        action["action_type"],
    })

df = pd.DataFrame(rows)

left, right = st.columns(2)

with left:
    st.subheader("Decision Distribution")

    fig = px.pie(
        df,
        names="Governance Decision",
        color="Governance Decision",
        color_discrete_map=color_map,
        hole=0.45
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        legend=dict(font=dict(color="#94a3b8")),
        margin=dict(t=10, b=10)
    )
    fig.update_traces(textfont_color="white")

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Risk Score by Agent")

    fig = px.bar(
        df,
        x="Agent",
        y="Risk Score",
        color="Governance Decision",
        color_discrete_map=color_map,
        text="Governance Decision"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        xaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(tickfont=dict(color="#94a3b8"), gridcolor="rgba(255,255,255,0.05)"),
        legend=dict(font=dict(color="#94a3b8")),
        margin=dict(t=10, b=10)
    )
    fig.update_traces(textfont_color="white", textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ── GOVERNANCE EVALUATIONS ────────────────────────────────────────────────────
st.subheader("Governance Trust Evaluations")

for action, evaluation in zip(actions, evaluations):
    counterparty = action.get("counterparty", action.get("vendor_name", "—"))
    action_ref   = action.get("action_ref", action.get("invoice_id", "—"))
    decision     = evaluation["decision"]
    color        = color_map.get(decision, "#64748b")

    scenario_label = action.get("scenario_label", "")

    header = f"{action['id']} — {counterparty} — **{decision}**"
    if scenario_label:
        header = f"[{scenario_label}] {header}"

    with st.expander(header):
        col_a, col_b = st.columns(2)

        with col_a:
            st.write(f"**Action Type:** {action['action_type']}")
            st.write(f"**Counterparty:** {counterparty}")
            st.write(f"**Action Ref:** {action_ref}")
            st.write(f"**Agent:** {action['agent_id']}")
            if action.get("scenario_description"):
                st.caption(action["scenario_description"])

        with col_b:
            st.markdown(
                f'<div style="background:{color};padding:16px;border-radius:12px;text-align:center;margin-bottom:12px;">'
                f'<div style="color:white;font-weight:700;font-size:1.1rem;">{decision}</div>'
                f'<div style="color:rgba(255,255,255,0.85);font-size:0.85rem;">Risk Score: {evaluation["risk_score"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            if evaluation["explanations"]:
                st.markdown("**Execution Risk Signals:**")
                for item in evaluation["explanations"]:
                    st.write(f"• {item}")
            else:
                st.success("Clean execution path.")
