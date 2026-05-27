import streamlit as st
import json
from services.evaluator import evaluate_action
from services import branding

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_logo()

DECISION_COLORS = {
    "ALLOW":    "#16a34a",
    "HOLD":     "#f59e0b",
    "ESCALATE": "#ea580c",
    "BLOCK":    "#dc2626",
}
STATUS_COLORS = {
    "Ready":               "#16a34a",
    "Hold Required":       "#f59e0b",
    "Escalation Required": "#ea580c",
    "Blocked":             "#dc2626",
    "Escalated":           "#ea580c",
    "Held":                "#f59e0b",
}

# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(59,130,246,0.15);color:#7dd3fc;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GOVERN™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Autonomous Action Queue")
st.caption("Governance queue — human control over autonomous execution")

st.markdown("---")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────

with open("data/scenarios.json") as f:
    actions = json.load(f)

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
            "id":           action["id"],
            "agent":        action["agent_id"],
            "action":       action["action_type"],
            "counterparty": counterparty,
            "amount":       action["amount"],
            "decision":     decision,
            "risk":         evaluation["risk_score"],
            "status":       status,
        })
    st.session_state.execution_queue = queue

queue = st.session_state.execution_queue

if not queue:
    st.markdown(
        '<div style="background:#0f172a;border:1px solid rgba(22,163,74,0.3);border-radius:12px;padding:20px 24px;text-align:center;color:#86efac;font-size:0.9rem;">'
        'No proposed autonomous actions currently awaiting governance review.'
        '</div>',
        unsafe_allow_html=True
    )

# ── QUEUE ITEMS ───────────────────────────────────────────────────────────────

for idx, item in enumerate(queue.copy()):
    d_color = DECISION_COLORS.get(item["decision"], "#64748b")
    s_color = STATUS_COLORS.get(item["status"], "#64748b")
    amount_str = f"${item['amount']:,.0f}" if item["amount"] > 0 else "—"

    st.markdown(
        f'<div style="background:#0f172a;border:1px solid #1e293b;border-left:4px solid {d_color};border-radius:12px;padding:18px 22px;margin-bottom:4px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<span style="color:#64748b;font-size:0.8rem;font-weight:600;font-family:monospace;">{item["id"]}</span>'
        f'<span style="color:white;font-weight:700;font-size:0.95rem;">{item["action"]}</span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="background:{d_color};color:white;font-weight:700;font-size:0.72rem;padding:3px 10px;border-radius:999px;">{item["decision"]}</span>'
        f'<span style="background:rgba(255,255,255,0.04);color:{s_color};font-weight:600;font-size:0.72rem;padding:3px 10px;border-radius:999px;border:1px solid {s_color};">{item["status"]}</span>'
        f'</div>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;">'
        f'<div><div style="color:#475569;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;">Counterparty</div><div style="color:#e2e8f0;font-size:0.85rem;">{item["counterparty"]}</div></div>'
        f'<div><div style="color:#475569;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;">Agent</div><div style="color:#e2e8f0;font-size:0.85rem;">{item["agent"]}</div></div>'
        f'<div><div style="color:#475569;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;">Scope Value</div><div style="color:#e2e8f0;font-size:0.85rem;">{amount_str}</div></div>'
        f'<div><div style="color:#475569;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px;">Risk Score</div><div style="color:{d_color};font-size:0.85rem;font-weight:700;">{item["risk"]}</div></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    btn_cols = st.columns([1, 1, 1, 1, 5])

    if item["status"] == "Ready":
        with btn_cols[0]:
            if st.button("Authorize", key=f"execute_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized for execution.")
                st.rerun()
        with btn_cols[1]:
            if st.button("Hold", key=f"hold_{idx}"):
                item["status"] = "Held"
                st.rerun()

    elif item["status"] == "Hold Required":
        with btn_cols[0]:
            if st.button("Authorize", key=f"execute_review_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized for execution.")
                st.rerun()
        with btn_cols[1]:
            if st.button("Hold", key=f"hold_review_{idx}"):
                item["status"] = "Held"
                st.rerun()
        with btn_cols[2]:
            if st.button("Escalate", key=f"escalate_{idx}"):
                item["status"] = "Escalated"
                st.rerun()

    elif item["status"] == "Escalation Required":
        with btn_cols[0]:
            if st.button("Override", key=f"override_esc_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} override authorized and executed.")
                st.rerun()
        with btn_cols[1]:
            if st.button("Escalate", key=f"escalate_esc_{idx}"):
                item["status"] = "Escalated"
                st.rerun()
        with btn_cols[2]:
            if st.button("Block", key=f"block_esc_{idx}"):
                item["status"] = "Blocked"
                st.rerun()

    elif item["status"] == "Blocked":
        with btn_cols[0]:
            if st.button("Override", key=f"override_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} override approved and executed.")
                st.rerun()
        with btn_cols[1]:
            if st.button("Escalate", key=f"blocked_escalate_{idx}"):
                item["status"] = "Escalated"
                st.rerun()

    elif item["status"] == "Escalated":
        with btn_cols[0]:
            if st.button("Authorize", key=f"execute_escalated_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.success(f"{item['id']} authorized following escalation review.")
                st.rerun()
        with btn_cols[1]:
            if st.button("Block", key=f"block_escalated_{idx}"):
                item["status"] = "Blocked"
                st.rerun()

    elif item["status"] == "Held":
        with btn_cols[0]:
            if st.button("Resume", key=f"resume_{idx}"):
                item["status"] = "Ready"
                st.rerun()
        with btn_cols[1]:
            if st.button("Cancel", key=f"cancel_{idx}"):
                st.session_state.execution_queue.remove(item)
                st.warning(f"{item['id']} cancelled.")
                st.rerun()

    st.markdown('<div style="margin-bottom:6px;"></div>', unsafe_allow_html=True)
