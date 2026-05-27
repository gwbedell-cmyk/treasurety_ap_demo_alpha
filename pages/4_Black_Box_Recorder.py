import streamlit as st
import json
from datetime import datetime, timedelta
from services.evaluator import evaluate_action

st.set_page_config(layout="wide")

with open("data/scenarios.json") as f:
    actions = json.load(f)

st.title("Decision Provenance Log")
st.caption("Black Box Recorder for Cognitive Intelligence™ — forensic testimony for every governance decision")

color_map = {
    "ALLOW":   "#16a34a",
    "HOLD":    "#f59e0b",
    "ESCALATE":"#ea580c",
    "BLOCK":   "#dc2626"
}

base_time = datetime.utcnow()

for idx, action in enumerate(actions):
    evaluation = evaluate_action(action)
    event_time = base_time - timedelta(minutes=(idx * 7))
    counterparty = action.get("counterparty", action.get("vendor_name", "—"))
    decision = evaluation["decision"]
    color = color_map.get(decision, "#64748b")

    with st.expander(f"{action['id']} — {counterparty} — {decision}"):
        col_a, col_b = st.columns([3, 1])

        with col_a:
            st.write(f"**Captured:** {event_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            st.write(f"**Agent:** {action['agent_id']}")
            st.write(f"**Action Type:** {action['action_type']}")
            st.write(f"**Counterparty:** {counterparty}")

        with col_b:
            st.markdown(
                f'<div style="background:{color};padding:12px;border-radius:10px;text-align:center;">'
                f'<div style="color:white;font-weight:700;font-size:1rem;">{decision}</div>'
                f'<div style="color:white;font-size:0.8rem;">Score: {evaluation["risk_score"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        if evaluation["triggered_policies"]:
            st.markdown("**Triggered Policies:**")
            for policy in evaluation["triggered_policies"]:
                st.write(f"• {policy}")

        if evaluation["explanations"]:
            st.markdown("**Execution Risk Signals:**")
            for finding in evaluation["explanations"]:
                st.write(f"• {finding}")

        if not evaluation["triggered_policies"] and not evaluation["explanations"]:
            st.success("No risk signals. Action within authorized execution bounds.")
