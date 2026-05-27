import streamlit as st
import json
import pandas as pd
import plotly.express as px

from services.evaluator import evaluate_action
from services.audit import record_decision

st.set_page_config(layout="wide")

with open("data/scenarios.json") as f:
    actions = json.load(f)

evaluations = []

for action in actions:
    evaluation = evaluate_action(action)
    record_decision(action, evaluation)
    evaluations.append(evaluation)

blocked = sum(1 for e in evaluations if e["decision"] == "BLOCK")
escalated = sum(1 for e in evaluations if e["decision"] == "ESCALATE")
held = sum(1 for e in evaluations if e["decision"] == "HOLD")
total_value = sum(a["amount"] for a in actions)

st.title("Governance Dashboard")
st.caption("Treasurety runtime — live governance state across all proposed autonomous actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Proposed Actions", len(actions))

with col2:
    st.metric("Governed Execution Value", f"${total_value:,.0f}")

with col3:
    st.metric("Blocked", blocked, delta_color="inverse")

with col4:
    st.metric("Hold Queue", held + escalated)

st.markdown("---")

rows = []

for action, evaluation in zip(actions, evaluations):
    rows.append({
        "Counterparty": action.get("counterparty", action.get("vendor_name", "—")),
        "Governance Decision": evaluation["decision"],
        "Risk Score": evaluation["risk_score"],
        "Action Scope Value": action["amount"]
    })

df = pd.DataFrame(rows)

left, right = st.columns(2)

with left:
    st.subheader("Decision Distribution")

    decision_order = ["ALLOW", "HOLD", "ESCALATE", "BLOCK"]
    color_map = {
        "ALLOW": "#16a34a",
        "HOLD": "#f59e0b",
        "ESCALATE": "#ea580c",
        "BLOCK": "#dc2626"
    }

    fig = px.pie(
        df,
        names="Governance Decision",
        color="Governance Decision",
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Risk Scores by Counterparty")

    fig = px.bar(
        df,
        x="Counterparty",
        y="Risk Score",
        color="Governance Decision",
        color_discrete_map=color_map
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Governance Trust Evaluations")

for action, evaluation in zip(actions, evaluations):
    counterparty = action.get("counterparty", action.get("vendor_name", "—"))
    action_ref = action.get("action_ref", action.get("invoice_id", "—"))

    with st.expander(f"{action['id']} — {counterparty} — {evaluation['decision']}"):
        col_a, col_b = st.columns(2)

        with col_a:
            st.write(f"**Action Type:** {action['action_type']}")
            st.write(f"**Counterparty:** {counterparty}")
            st.write(f"**Action Ref:** {action_ref}")
            if action["amount"] > 0:
                st.write(f"**Scope Value:** ${action['amount']:,.0f}")

        with col_b:
            st.write(f"**Governance Decision:** {evaluation['decision']}")
            st.write(f"**Risk Score:** {evaluation['risk_score']}")
            st.write(f"**Agent:** {action['agent_id']}")

        if evaluation["explanations"]:
            st.markdown("**Execution Risk Signals:**")
            for item in evaluation["explanations"]:
                st.write(f"• {item}")
