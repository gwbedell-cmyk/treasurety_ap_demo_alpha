import streamlit as st
import json
from services.ui_helpers import decision_color

st.set_page_config(layout="wide")

with open("data/scenarios.json") as f:
    all_scenarios = json.load(f)

# Demo scenarios with labels
demo_scenarios = [s for s in all_scenarios if "scenario_label" in s]

st.title("Governance Simulation")
st.caption("Interactive what-if environment — test governance decisions against proposed autonomous actions")

st.markdown("---")

tab1, tab2 = st.tabs(["Custom Simulation", "Demo Scenarios"])

with tab1:
    st.subheader("Simulation Variables")

    col_left, col_right = st.columns(2)

    with col_left:
        amount = st.slider(
            "Proposed Action Scope Value ($)",
            min_value=5000,
            max_value=600000,
            value=125000,
            step=5000
        )

        agent_confidence = st.slider(
            "Agent Confidence (%)",
            min_value=50,
            max_value=100,
            value=92,
            step=1
        )

        counterparty_trust = st.selectbox(
            "Counterparty Trust Profile",
            ["Low Risk", "Medium Risk", "High Risk"]
        )

        jurisdiction = st.selectbox(
            "Execution Jurisdiction",
            ["Domestic", "Cross-Border", "High-Risk Jurisdiction"]
        )

    with col_right:
        urgency = st.selectbox(
            "Execution Urgency",
            ["Standard", "Urgent", "Emergency"]
        )

        off_hours = st.toggle("Off-Hours Execution Request")
        destination_modified = st.toggle("Counterparty Destination Modified")
        authority_chain_complete = st.toggle("Authority Chain Complete", value=True)
        duplicate_suspected = st.toggle("Duplicate Submission Suspected")

    st.markdown("---")

    risk_score = 0
    findings = []
    policies = []

    if amount > 100000:
        risk_score += 35
        findings.append("High-value action exceeds autonomous execution scope boundary.")
        policies.append("Execution Scope Boundary Enforcement")

    if agent_confidence < 85:
        risk_score += 20
        findings.append("Reduced agent confidence increases governance uncertainty.")
        policies.append("AI Confidence Review")

    if agent_confidence < 70:
        risk_score += 35
        findings.append("Agent confidence below safe autonomous execution threshold.")
        policies.append("AI Confidence Escalation")

    if counterparty_trust == "Medium Risk":
        risk_score += 15
        findings.append("Counterparty trust profile elevated.")
        policies.append("Dynamic Counterparty Trust Scoring")

    if counterparty_trust == "High Risk":
        risk_score += 35
        findings.append("High-risk counterparty requires governance review.")
        policies.append("Counterparty Risk Escalation")

    if jurisdiction == "Cross-Border":
        risk_score += 20
        findings.append("Cross-jurisdiction execution requires heightened governance.")
        policies.append("Cross-Jurisdiction Execution Review")

    if jurisdiction == "High-Risk Jurisdiction":
        risk_score += 40
        findings.append("Execution jurisdiction classified as high-risk.")
        policies.append("High-Risk Jurisdiction Review")

    if urgency == "Urgent":
        risk_score += 10
        findings.append("Urgent execution introduces elevated operational risk.")
        policies.append("Execution Timing Risk")

    if urgency == "Emergency":
        risk_score += 20
        findings.append("Emergency execution requires exception pathway review.")
        policies.append("Emergency Execution Fast-Track")

    if off_hours:
        risk_score += 15
        findings.append("Off-hours execution violates standard operating controls.")
        policies.append("Off-Hours Execution Restriction")

    if destination_modified:
        risk_score += 30
        findings.append("Counterparty destination recently modified.")
        policies.append("Counterparty Destination Change Hold")

    if not authority_chain_complete:
        risk_score += 25
        findings.append("Authority chain incomplete — execution not fully delegated.")
        policies.append("Authority Chain Pre-Approval")

    if duplicate_suspected:
        risk_score += 35
        findings.append("Possible duplicate action submission detected.")
        policies.append("Duplicate Submission Detection")

    if risk_score >= 90:
        decision = "BLOCK"
    elif risk_score >= 70:
        decision = "ESCALATE"
    elif risk_score >= 40:
        decision = "HOLD"
    else:
        decision = "ALLOW"

    color = decision_color(decision)

    sim_left, sim_right = st.columns(2)

    with sim_left:
        st.subheader("Simulated Autonomous Proposal")

        st.write(f"**Scope Value:** ${amount:,.0f}")
        st.write(f"**Agent Confidence:** {agent_confidence}%")
        st.write(f"**Counterparty Trust:** {counterparty_trust}")
        st.write(f"**Jurisdiction:** {jurisdiction}")
        st.write(f"**Urgency:** {urgency}")
        st.write(f"**Off-Hours Request:** {'Yes' if off_hours else 'No'}")
        st.write(f"**Destination Modified:** {'Yes' if destination_modified else 'No'}")
        st.write(f"**Authority Chain Complete:** {'Yes' if authority_chain_complete else 'No'}")
        st.write(f"**Duplicate Suspected:** {'Yes' if duplicate_suspected else 'No'}")

    with sim_right:
        st.subheader("Governance Trust Evaluation")

        st.markdown(
            f"""
            <div style="
                background:{color};
                padding:20px;
                border-radius:16px;
                color:white;
                text-align:center;
            ">
                <h2>{decision}</h2>
                <h3>Risk Score: {risk_score}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("Execution Risk Signals")

    if findings:
        for item in findings:
            st.write(f"• {item}")
    else:
        st.success("No governance concerns detected. Action within authorized execution bounds.")

    st.markdown("---")

    st.subheader("Triggered Policies")

    if policies:
        for policy in policies:
            st.write(f"• {policy}")
    else:
        st.success("No policy interventions triggered.")


with tab2:
    st.subheader("Pre-Built Demo Scenarios")
    st.caption("Generalized autonomous execution scenarios across agent types and domains")

    if not demo_scenarios:
        st.info("No demo scenarios found. Add scenario_label fields to scenarios.json entries.")
    else:
        for scenario in demo_scenarios:
            from services.evaluator import evaluate_action
            evaluation = evaluate_action(scenario)
            color = decision_color(evaluation["decision"])

            with st.expander(
                f"{scenario['scenario_label']} — {scenario['id']} — **{evaluation['decision']}**"
            ):
                st.markdown(f"*{scenario['scenario_description']}*")
                st.markdown("---")

                col_a, col_b = st.columns(2)

                with col_a:
                    st.write(f"**Agent:** {scenario['agent_id']}")
                    st.write(f"**Action Type:** {scenario['action_type']}")
                    st.write(f"**Counterparty:** {scenario['counterparty']}")
                    st.write(f"**Action Ref:** {scenario['action_ref']}")
                    if scenario["amount"] > 0:
                        st.write(f"**Scope Value:** ${scenario['amount']:,.0f} {scenario['currency']}")
                    st.write(f"**Agent Confidence:** {int(scenario['confidence'] * 100)}%")

                with col_b:
                    st.markdown(
                        f"""
                        <div style="
                            background:{color};
                            padding:16px;
                            border-radius:12px;
                            color:white;
                            text-align:center;
                        ">
                            <h3 style="margin-bottom:6px;">{evaluation['decision']}</h3>
                            <div style="font-size:0.9rem;">Risk Score: {evaluation['risk_score']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                if evaluation["explanations"]:
                    st.markdown("**Execution Risk Signals:**")
                    for finding in evaluation["explanations"]:
                        st.write(f"• {finding}")

                if evaluation["triggered_policies"]:
                    st.markdown("**Triggered Policies:**")
                    for policy in evaluation["triggered_policies"]:
                        st.write(f"• {policy}")
