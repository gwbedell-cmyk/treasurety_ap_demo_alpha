import streamlit as st
import json

st.set_page_config(layout="wide")

with open("data/policies.json") as f:
    policies = json.load(f)

st.title("Policy Control Center")
st.caption("Runtime policy enforcement — governance controls for autonomous execution")

for policy in policies:
    with st.container():
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            st.write(f"### {policy['id']}")

        with col2:
            st.write(f"**{policy['name']}**")
            st.write(policy["description"])
            st.write(f"Risk Weight: {policy['weight']}")

        with col3:
            st.toggle(
                "Enabled",
                value=policy["enabled"],
                key=policy["id"]
            )

        st.markdown("---")