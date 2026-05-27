import streamlit as st
import json
from services.evaluator import evaluate_action

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<style>
div[data-testid="stButton"] button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    min-height: 42px !important;
}

/* Execute / Allow */
div[data-testid="stButton"]:has(button[key*="execute"]) button {
    background-color: #dbeafe !important;
    color: #1e3a8a !important;
    border: 1px solid #93c5fd !important;
}

/* Hold */
div[data-testid="stButton"]:has(button[key*="hold"]) button {
    background-color: #fee2e2 !important;
    color: #991b1b !important;
    border: 1px solid #fca5a5 !important;
}

/* Resume */
div[data-testid="stButton"]:has(button[key*="resume"]) button {
    background-color: #dcfce7 !important;
    color: #166534 !important;
    border: 1px solid #86efac !important;
}

/* Escalate */
div[data-testid="stButton"]:has(button[key*="escalate"]) button {
    background-color: #fef3c7 !important;
    color: #92400e !important;
    border: 1px solid #fcd34d !important;
}

/* Override */
div[data-testid="stButton"]:has(button[key*="override"]) button {
    background-color: #ede9fe !important;
    color: #5b21b6 !important;
    border: 1px solid #c4b5fd !important;
}

/* Block / Cancel */
div[data-testid="stButton"]:has(button[key*="cancel"]) button,
div[data-testid="stButton"]:has(button[key*="block"]) button {
    background-color: #fecaca !important;
    color: #7f1d1d !important;
    border: 1px solid #f87171 !important;
}
</style>
""", unsafe_allow_html=True)

with open("data/scenarios.json") as f:
    actions = json.load(f)

st.title("Proposed Autonomous Actions")
st.caption("Governance queue — human control over autonomous execution")

if "execution_queue" not in st.session_state:
    queue = []

    for action in actions:
        evaluation = evaluate_action(action)
        decision = evaluation["decision"]

        if decision == "ALLOW":
            status = "Ready"
        elif decision == "HOLD":
            status = "Hold Required"
        elif decision == "ESCALATE":
            status = "Escalation Required"
        else:
            status = "Blocked"

        counterparty = action.get("counterparty", action.get("vendor_name", "—"))

        queue.append({
            "id": action["id"],
            "agent": action["agent_id"],
            "action": action["action_type"],
            "counterparty": counterparty,
            "amount": action["amount"],
            "decision": decision,
            "risk": evaluation["risk_score"],
            "status": status
        })

    st.session_state.execution_queue = queue

queue = st.session_state.execution_queue

if not queue:
    st.success("No proposed autonomous actions currently awaiting governance review.")

for idx, item in enumerate(queue.copy()):
    st.markdown("---")

    st.subheader(f"{item['id']} — {item['action']}")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.write(f"**Counterparty:** {item['counterparty']}")
        if item["amount"] > 0:
            st.write(f"**Scope Value:** ${item['amount']:,.0f}")

    with c2:
        st.write(f"**Agent:** {item['agent']}")
        st.write(f"**Risk Score:** {item['risk']}")

    with c3:
        st.write(f"**Governance Decision:** {item['decision']}")
        st.write(f"**Governance State:** {item['status']}")

    with c4:
        if item["status"] == "Ready":
            if st.button("Authorize", key=f"execute_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized for execution.")
                st.rerun()

            if st.button("Hold", key=f"hold_{idx}"):
                item["status"] = "Held"
                st.rerun()

        elif item["status"] == "Hold Required":
            if st.button("Authorize", key=f"execute_review_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized for execution.")
                st.rerun()

            if st.button("Hold", key=f"hold_review_{idx}"):
                item["status"] = "Held"
                st.rerun()

            if st.button("Escalate", key=f"escalate_{idx}"):
                item["status"] = "Escalated"
                st.rerun()

        elif item["status"] == "Escalation Required":
            if st.button("Override", key=f"override_esc_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} override authorized and executed.")
                st.rerun()

            if st.button("Escalate", key=f"escalate_esc_{idx}"):
                item["status"] = "Escalated"
                st.rerun()

            if st.button("Block", key=f"block_esc_{idx}"):
                item["status"] = "Blocked"
                st.rerun()

        elif item["status"] == "Blocked":
            if st.button("Override", key=f"override_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} override approved and executed.")
                st.rerun()

            if st.button("Escalate", key=f"blocked_escalate_{idx}"):
                item["status"] = "Escalated"
                st.rerun()

        elif item["status"] == "Escalated":
            if st.button("Authorize", key=f"execute_escalated_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized following escalation review.")
                st.rerun()

            if st.button("Block", key=f"block_escalated_{idx}"):
                item["status"] = "Blocked"
                st.rerun()

        elif item["status"] == "Held":
            if st.button("Resume", key=f"resume_{idx}"):
                item["status"] = "Ready"
                st.rerun()

            if st.button("Cancel", key=f"cancel_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.warning(f"{item['id']} cancelled.")
                st.rerun()
