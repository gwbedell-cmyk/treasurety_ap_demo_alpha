import streamlit as st
import json
from datetime import datetime, timedelta
from services.evaluator import evaluate_action

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

with open("data/scenarios.json") as f:
    actions = json.load(f)

DECISION_COLORS = {
    "ALLOW":    "#16a34a",
    "HOLD":     "#f59e0b",
    "ESCALATE": "#ea580c",
    "BLOCK":    "#dc2626",
}

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Decision Provenance Log")
st.caption("Forensic testimony for every governance decision — complete immutable decision history")

st.markdown("---")

base_time = datetime.utcnow()

for idx, action in enumerate(actions):
    evaluation = evaluate_action(action)
    event_time = base_time - timedelta(minutes=(idx * 7))
    counterparty = action.get("counterparty", action.get("vendor_name", "—"))
    decision     = evaluation["decision"]
    color        = DECISION_COLORS.get(decision, "#64748b")

    with st.expander(f"{action['id']} — {counterparty} — {decision}"):
        col_a, col_b = st.columns([3, 1])

        with col_a:
            detail_rows = [
                ("Captured",     event_time.strftime("%Y-%m-%d %H:%M:%S UTC")),
                ("Agent",        action["agent_id"]),
                ("Action Type",  action["action_type"]),
                ("Counterparty", counterparty),
            ]
            rows_html = "".join(
                f'<div style="display:flex;gap:14px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                f'<span style="color:#475569;font-size:0.82rem;min-width:110px;flex-shrink:0;">{label}</span>'
                f'<span style="color:#e2e8f0;font-size:0.82rem;">{value}</span>'
                f'</div>'
                for label, value in detail_rows
            )
            st.markdown(
                '<div style="background:#0a0f1e;border-radius:8px;padding:12px 16px;margin-bottom:12px;">'
                + rows_html +
                '</div>',
                unsafe_allow_html=True
            )

            if evaluation["triggered_policies"]:
                policies_html = "".join(
                    f'<div style="background:#0f172a;border-left:3px solid #3b82f6;padding:7px 12px;border-radius:5px;margin-bottom:4px;color:#94a3b8;font-size:0.82rem;">{p}</div>'
                    for p in evaluation["triggered_policies"]
                )
                st.markdown(
                    '<div style="color:#475569;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">Triggered Policies</div>'
                    + policies_html,
                    unsafe_allow_html=True
                )

            if evaluation["explanations"]:
                signals_html = "".join(
                    f'<div style="background:#0f172a;border-left:3px solid #ea580c;padding:7px 12px;border-radius:5px;margin-bottom:4px;color:#94a3b8;font-size:0.82rem;">{s}</div>'
                    for s in evaluation["explanations"]
                )
                st.markdown(
                    '<div style="color:#475569;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;margin-top:10px;">Execution Risk Signals</div>'
                    + signals_html,
                    unsafe_allow_html=True
                )

            if not evaluation["triggered_policies"] and not evaluation["explanations"]:
                st.markdown(
                    '<div style="background:#0f172a;border:1px solid rgba(22,163,74,0.3);border-radius:8px;padding:10px 14px;color:#86efac;font-size:0.83rem;">'
                    'No risk signals. Action within authorized execution bounds.'
                    '</div>',
                    unsafe_allow_html=True
                )

        with col_b:
            st.markdown(
                f'<div style="background:{color};border-radius:12px;padding:20px 16px;text-align:center;">'
                f'<div style="color:rgba(255,255,255,0.65);font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">DECISION</div>'
                f'<div style="color:white;font-weight:800;font-size:1.15rem;margin-bottom:6px;">{decision}</div>'
                f'<div style="color:rgba(255,255,255,0.75);font-size:0.8rem;">Score: {evaluation["risk_score"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
