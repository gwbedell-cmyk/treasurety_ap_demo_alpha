import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.evaluator import evaluate_action
from services.audit import record_decision, load_audit_log
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

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
        col_a, col_b = st.columns([3, 1])

        with col_a:
            detail_rows = [
                ("Agent",        action["agent_id"]),
                ("Action Type",  action["action_type"]),
                ("Counterparty", counterparty),
                ("Action Ref",   action_ref),
            ]
            if action.get("amount", 0) > 0:
                detail_rows.append(("Scope Value", f"${action['amount']:,.0f}"))
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
