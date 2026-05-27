import streamlit as st
import json

st.set_page_config(layout="wide")

LOCKED_POLICIES = {
    "P-06": "Treasurety Monitor module required",
    "P-08": "Treasurety Shield integration required",
    "P-19": "ERP connector required",
    "P-20": "Treasurety Assess — contract intelligence module required"
}

with open("data/policies.json") as f:
    policies = json.load(f)

st.title("Policy Control Center")
st.caption("Runtime policy enforcement — governance controls for autonomous execution")

st.markdown("---")

for policy in policies:
    locked = policy["id"] in LOCKED_POLICIES
    toggle_key = f"toggle_{policy['id']}"

    with st.container():
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            st.write(f"### {policy['id']}")

        with col2:
            st.write(f"**{policy['name']}**")
            st.write(policy["description"])
            st.write(f"Policy Weight: {policy['weight']}")

            if locked:
                st.caption(f"🔒 {LOCKED_POLICIES[policy['id']]}")

        with col3:
            if locked:
                st.toggle(
                    "Disabled",
                    value=False,
                    key=f"locked_{policy['id']}",
                    disabled=True
                )
            else:
                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = policy["enabled"]

                current_state = st.session_state[toggle_key]

                st.toggle(
                    "Enabled" if current_state else "Disabled",
                    key=toggle_key
                )

        st.markdown("---")
