import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime
from services import branding
from services.gate_engine import evaluate_system
from services.gate_ai_engine import GateConversation

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()
branding.sidebar_nav()


# ── SESSION STATE ──────────────────────────────────────────────────────────────

def init_state():
    if "gate_step" not in st.session_state:
        st.session_state.gate_step = "landing"
    if "gate_intake" not in st.session_state:
        st.session_state.gate_intake = {}
    if "gate_results" not in st.session_state:
        st.session_state.gate_results = None
    if "gate_ai_conv" not in st.session_state:
        st.session_state.gate_ai_conv = None

def reset_gate():
    for key in ["gate_step", "gate_intake", "gate_results", "gate_ai_conv"]:
        if key in st.session_state:
            del st.session_state[key]

init_state()
step = st.session_state.gate_step


# ── SHARED COMPONENTS ──────────────────────────────────────────────────────────

def page_header():
    st.image("assets/logo.png", width=240)
    st.markdown(
        '<div style="margin-bottom:4px;">'
        '<span style="background:rgba(59,130,246,0.12);color:#7dd3fc;font-size:0.72rem;'
        'font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:4px 14px;'
        'border-radius:999px;border:1px solid rgba(59,130,246,0.3);">TREASURETY GATE</span>'
        '</div>',
        unsafe_allow_html=True
    )


def step_progress(current: int, total: int = 6):
    labels = [
        "Enterprise Context",
        "System Type",
        "Authority Scope",
        "Human Oversight",
        "Ecosystem Exposure",
        "Consequence & Controls",
    ]
    html = '<div style="display:flex;align-items:center;gap:0;margin-bottom:28px;">'
    for i, label in enumerate(labels):
        n = i + 1
        done   = n < current
        active = n == current

        if done:
            bg, fg, tc = "#16a34a", "white", "#16a34a"
            num = "✓"
        elif active:
            bg, fg, tc = "#3b82f6", "white", "#7dd3fc"
            num = str(n)
        else:
            bg, fg, tc = "#1e293b", "#64748b", "#475569"
            num = str(n)

        html += (
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<div style="width:28px;height:28px;border-radius:50%;background:{bg};'
            f'display:flex;align-items:center;justify-content:center;font-weight:700;'
            f'font-size:0.78rem;color:{fg};flex-shrink:0;">{num}</div>'
            f'<span style="font-size:0.78rem;font-weight:600;color:{tc};white-space:nowrap;">{label}</span>'
            f'</div>'
        )
        if i < len(labels) - 1:
            html += '<div style="flex:1;height:1px;background:#1e293b;margin:0 8px;min-width:12px;"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def info_card(text: str):
    st.markdown(
        f'<div style="background:#0f172a;border-left:4px solid #3b82f6;padding:14px 18px;'
        f'border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">{text}</div>',
        unsafe_allow_html=True
    )


def sev_color(sev: str) -> str:
    return {"CRITICAL": "#dc2626", "HIGH": "#ea580c", "MODERATE": "#f59e0b", "LOW": "#16a34a"}.get(sev, "#64748b")


def score_band(s: int) -> tuple[str, str]:
    if s < 25:  return "Low",      "#16a34a"
    if s < 50:  return "Moderate", "#f59e0b"
    if s < 75:  return "High",     "#ea580c"
    return              "Critical", "#dc2626"


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════

if step == "landing":
    page_header()

    st.markdown(
        '<h1 style="font-size:2.8rem;font-weight:800;letter-spacing:-0.03em;'
        'margin-bottom:4px;">Treasurety Gate</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="color:#7dd3fc;font-size:1.15rem;font-weight:500;margin-bottom:32px;">'
        'Operational Trust Certification Infrastructure for Agentic Systems</p>',
        unsafe_allow_html=True
    )

    # Hero card
    st.markdown(
        '<div style="background:linear-gradient(135deg,#060d1a 0%,#0d1f3c 100%);'
        'border:1px solid rgba(59,130,246,0.25);border-radius:20px;padding:44px 52px;'
        'margin-bottom:32px;">'
        '<div style="max-width:680px;">'
        '<div style="color:rgba(255,255,255,0.45);font-size:0.78rem;font-weight:700;'
        'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:16px;">'
        'THE DEPLOYMENT AUTHORIZATION QUESTION</div>'
        '<div style="color:white;font-size:1.55rem;font-weight:700;line-height:1.45;margin-bottom:20px;">'
        'Should this autonomous system be deployed?'
        '</div>'
        '<p style="color:#94a3b8;font-size:0.96rem;line-height:1.7;margin-bottom:0;">'
        'Treasurety Gate evaluates whether an autonomous system has sufficient governance maturity, '
        'authority boundaries, intervention capability, escalation readiness, and ecosystem trust posture '
        'to operate in your enterprise environment — under a declared scope, today.'
        '</p>'
        '</div>'
        '<div style="margin-top:28px;display:flex;align-items:center;gap:8px;">'
        '<div style="width:8px;height:8px;border-radius:50%;background:#16a34a;'
        'box-shadow:0 0 8px #16a34a;"></div>'
        '<span style="color:#64748b;font-size:0.78rem;">This is not an AI quiz. '
        'This is deployment authorization.</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # CTA buttons
    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        if st.button("Standard Assessment", use_container_width=True, type="primary",
                     help="Structured form wizard — step-by-step intake"):
            st.session_state.gate_step = 1
            st.rerun()
    with c2:
        if st.button("AI-Native Assessment", use_container_width=True,
                     help="Conversational EPC intake — governed dialogue with ATC eligibility verdict"):
            st.session_state.gate_step = "ai_chat"
            st.rerun()

    st.markdown(
        '<div style="display:flex;gap:24px;margin-top:10px;">'
        '<div style="flex:1;color:#475569;font-size:0.78rem;">Form-based wizard. '
        'Six structured steps. Produces a Trust Certificate.</div>'
        '<div style="flex:1;color:#475569;font-size:0.78rem;">Conversational intake. '
        'Eight governed stages. Produces a free deployment verdict and ATC eligibility assessment.</div>'
        '<div style="flex:1;"></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Value props
    vp1, vp2, vp3 = st.columns(3)
    props = [
        ("#3b82f6", "Deployment Authorization",
         "Gate answers the question enterprises are not yet asking systematically: "
         "Is this autonomous system operationally trustworthy enough to deploy?"),
        ("#8b5cf6", "Three Executive Verdicts",
         "SAFE TO DEPLOY — SAFE WITH EXCEPTIONS — DANGER: DO NOT DEPLOY. "
         "No gamified scores. No fake precision. The verdict is the product."),
        ("#0891b2", "Trust Certificate",
         "Every assessment produces a Provisional Trust Certificate — a point-in-time "
         "deployment authorization artifact suitable for executive governance."),
    ]
    for col, (color, title, desc) in zip([vp1, vp2, vp3], props):
        with col:
            st.markdown(
                f'<div style="background:#0f172a;border:1px solid rgba(255,255,255,0.06);'
                f'border-top:3px solid {color};border-radius:12px;padding:22px 20px;height:100%;">'
                f'<div style="color:{color};font-size:0.75rem;font-weight:700;letter-spacing:0.1em;'
                f'text-transform:uppercase;margin-bottom:10px;">{title}</div>'
                f'<p style="color:#64748b;font-size:0.84rem;line-height:1.6;margin:0;">{desc}</p>'
                f'</div>',
                unsafe_allow_html=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — ENTERPRISE CONTEXT
# ══════════════════════════════════════════════════════════════════════════════

elif step == 1:
    page_header()
    st.title("Trust Application — Enterprise Context")
    st.caption("Establish the operational domain and deployment context for this autonomous system.")
    st.markdown("---")
    step_progress(1)
    info_card("This section establishes domain weighting, consequence class, and regulatory context. Honest answers produce accurate authorization verdicts.")

    d = st.session_state.gate_intake

    c1, c2 = st.columns(2)
    with c1:
        d["system_name"] = st.text_input(
            "System Name", value=d.get("system_name", ""),
            placeholder="e.g. FinanceOps AP Agent"
        )
        d["industry"] = st.selectbox(
            "Industry",
            ["Financial Services", "Healthcare", "Manufacturing", "Supply Chain & Logistics",
             "Insurance", "Energy & Utilities", "Government", "Cybersecurity",
             "Enterprise Operations", "AI Infrastructure", "Multi-Agent Orchestration", "Other"],
            index=["Financial Services","Healthcare","Manufacturing","Supply Chain & Logistics",
                   "Insurance","Energy & Utilities","Government","Cybersecurity",
                   "Enterprise Operations","AI Infrastructure","Multi-Agent Orchestration","Other"]
                  .index(d.get("industry", "Financial Services"))
        )
        d["business_function"] = st.text_input(
            "Business Function",
            value=d.get("business_function", ""),
            placeholder="e.g. Accounts Payable, Patient Triage, Procurement"
        )

    with c2:
        d["system_origin"] = st.selectbox(
            "System Origin",
            ["Internally built", "Vendor-provided", "Hybrid"],
            index=["Internally built","Vendor-provided","Hybrid"].index(d.get("system_origin","Internally built"))
        )
        d["deployment_stage"] = st.selectbox(
            "Deployment Stage",
            ["Pre-deployment", "Piloting", "Deployed — limited scope", "Deployed — production"],
            index=["Pre-deployment","Piloting","Deployed — limited scope","Deployed — production"]
                  .index(d.get("deployment_stage","Pre-deployment"))
        )
        d["scale"] = st.selectbox(
            "Scale — Users, Workflows, or Transactions Affected",
            ["Under 100", "100 – 1,000", "1,000 – 10,000", "Over 10,000"],
            index=["Under 100","100 – 1,000","1,000 – 10,000","Over 10,000"]
                  .index(d.get("scale","Under 100"))
        )

    st.markdown("")
    d["regulated_environment"] = st.toggle(
        "This system operates in a regulated environment (financial, clinical, legal, government, or critical infrastructure)",
        value=d.get("regulated_environment", False)
    )

    st.session_state.gate_intake = d
    st.markdown("---")
    _, nav = st.columns([4, 1])
    with nav:
        disabled = not bool(d.get("system_name", "").strip())
        if st.button("Next →", use_container_width=True, type="primary", disabled=disabled,
                     help="Enter system name to continue"):
            st.session_state.gate_step = 2
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — AUTONOMOUS SYSTEM TYPE
# ══════════════════════════════════════════════════════════════════════════════

elif step == 2:
    page_header()
    st.title("Trust Application — System Type")
    st.caption("Characterize the system architecture and its operational agency.")
    st.markdown("---")
    step_progress(2)
    info_card("This section distinguishes passive assistance from operational agency. A system that can execute actions carries fundamentally different deployment risk.")

    d = st.session_state.gate_intake

    c1, c2 = st.columns(2)
    with c1:
        d["system_type"] = st.selectbox(
            "Autonomous System Type",
            ["Single Agent", "Multi-Agent System", "AI Workflow Automation",
             "AI Decision Support", "AI Execution Agent", "AI Copilot with Tool Access",
             "AI Orchestration Layer", "RPA + LLM", "AI Infrastructure Layer",
             "Third-Party Autonomous Vendor"],
            index=["Single Agent","Multi-Agent System","AI Workflow Automation",
                   "AI Decision Support","AI Execution Agent","AI Copilot with Tool Access",
                   "AI Orchestration Layer","RPA + LLM","AI Infrastructure Layer",
                   "Third-Party Autonomous Vendor"].index(d.get("system_type","Single Agent"))
        )

    st.markdown("#### Operational Agency Profile")
    st.caption("Does this system do any of the following?")

    rc1, rc2 = st.columns(2)
    with rc1:
        d["action_recommend"]  = st.toggle("Recommends actions for human review",           value=d.get("action_recommend", False))
        d["action_write"]      = st.toggle("Writes to or modifies records",                 value=d.get("action_write", False))
        d["action_execution"]  = st.toggle("Executes actions without human confirmation",   value=d.get("action_execution", False))
        d["calls_apis"]        = st.toggle("Calls external APIs autonomously",              value=d.get("calls_apis", False))
    with rc2:
        d["accesses_production"]       = st.toggle("Accesses production systems",                   value=d.get("accesses_production", False))
        d["modifies_records"]          = st.toggle("Modifies authoritative data records",           value=d.get("modifies_records", False))
        d["initiates_sensitive_workflows"] = st.toggle(
            "Initiates financial, clinical, legal, or security workflows",
            value=d.get("initiates_sensitive_workflows", False)
        )

    st.session_state.gate_intake = d
    st.markdown("---")
    nl, nr = st.columns(2)
    with nl:
        if st.button("← Back", use_container_width=True):
            st.session_state.gate_step = 1
            st.rerun()
    with nr:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.gate_step = 3
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — AUTHORITY SCOPE
# ══════════════════════════════════════════════════════════════════════════════

elif step == 3:
    page_header()
    st.title("Trust Application — Authority Scope")
    st.caption("Define the explicit authority granted to this system and its boundary integrity.")
    st.markdown("---")
    step_progress(3)
    info_card("Authority scope determines whether this system has excessive agency risk. Unbounded or expandable authority is a primary deployment blocker.")

    d = st.session_state.gate_intake

    st.markdown("#### Action Authority Types")
    ac1, ac2 = st.columns(2)
    with ac1:
        d["financial_authority"]  = st.toggle("Financial execution authority (payments, transactions, orders)", value=d.get("financial_authority", False))
        d["access_changes"]       = st.toggle("Access or permission changes (IAM, credentials, roles)",        value=d.get("access_changes", False))
        d["clinical_workflows"]   = st.toggle("Clinical or patient-impacting workflows",                       value=d.get("clinical_workflows", False))
        d["legal_workflows"]      = st.toggle("Legal or contractual workflow execution",                       value=d.get("legal_workflows", False))
    with ac2:
        d["infra_changes"]        = st.toggle("Infrastructure changes (cloud, network, compute)",              value=d.get("infra_changes", False))
        d["security_actions"]     = st.toggle("Security actions (firewall rules, incident response, revocation)", value=d.get("security_actions", False))
        d["customer_comms"]       = st.toggle("Autonomous customer or external communications",                value=d.get("customer_comms", False))
        d["can_create_subagents"] = st.toggle("Can create sub-agents or delegate tasks to other agents",       value=d.get("can_create_subagents", False))

    st.markdown("---")
    st.markdown("#### Authority Boundary Integrity")

    bc1, bc2 = st.columns(2)
    with bc1:
        d["authority_limits_enforced"] = st.toggle(
            "Authority limits are explicit and machine-enforced",
            value=d.get("authority_limits_enforced", False),
            help="Are there hard technical controls — not just policies — that prevent the system from exceeding its authority?"
        )
        d["authority_can_expand"] = st.toggle(
            "Authority scope can expand dynamically at runtime",
            value=d.get("authority_can_expand", False),
            help="Can the system acquire broader permissions or access without human re-authorization?"
        )
    with bc2:
        d["hard_boundaries"] = st.toggle(
            "Hard action boundaries exist that the system cannot cross",
            value=d.get("hard_boundaries", False)
        )

    if d.get("authority_can_expand") and not d.get("authority_limits_enforced"):
        st.error("Dynamic authority expansion without machine-enforced limits is a critical deployment blocker.")

    st.session_state.gate_intake = d
    st.markdown("---")
    nl, nr = st.columns(2)
    with nl:
        if st.button("← Back", use_container_width=True):
            st.session_state.gate_step = 2
            st.rerun()
    with nr:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.gate_step = 4
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — HUMAN OVERSIGHT
# ══════════════════════════════════════════════════════════════════════════════

elif step == 4:
    page_header()
    st.title("Trust Application — Human Oversight")
    st.caption("Evaluate whether human governance of this system is real or cosmetic.")
    st.markdown("---")
    step_progress(4)
    info_card("Human-in-the-loop exists on paper at many organizations but fails operationally. This section determines actual intervention capacity.")

    d = st.session_state.gate_intake

    _approval_opts = ["Pre-action approval", "Post-action review", "Sampled review",
                      "Exception-based", "None — system acts autonomously"]
    # "None" is the engine-normalized form of "None — system acts autonomously";
    # map it back to the display label when re-rendering after back-navigation.
    _stored = d.get("approval_model", "Exception-based")
    _approval_default = "None — system acts autonomously" if _stored == "None" else (
        _stored if _stored in _approval_opts else "Exception-based"
    )

    c1, c2 = st.columns(2)
    with c1:
        _selected = st.selectbox(
            "Human Review Model",
            _approval_opts,
            index=_approval_opts.index(_approval_default)
        )
        # Normalize display label to engine token before storing
        d["approval_model"] = "None" if _selected == "None — system acts autonomously" else _selected

        d["reviewers_trained"] = st.toggle(
            "Human reviewers are trained on this system's risks and authority",
            value=d.get("reviewers_trained", False)
        )
        d["reviewer_overload"] = st.toggle(
            "Human reviewers are likely to experience alert fatigue or overload",
            value=d.get("reviewer_overload", False)
        )

    with c2:
        d["kill_switch"] = st.toggle(
            "Kill switch or emergency stop is implemented and tested",
            value=d.get("kill_switch", False),
            help="Can operations be halted immediately without system cooperation?"
        )
        d["fallback_mode"] = st.toggle(
            "Fallback mode exists if autonomous operation is suspended",
            value=d.get("fallback_mode", False)
        )
        d["escalation_defined"] = st.toggle(
            "Escalation paths are formally defined and operationally tested",
            value=d.get("escalation_defined", False)
        )

    # Governance gap warnings
    missing = sum(1 for k in ["kill_switch", "fallback_mode", "escalation_defined", "reviewers_trained"] if not d.get(k))
    if missing >= 3:
        st.error(f"{missing} of 4 critical oversight controls are absent. This profile approaches an automatic DANGER verdict.")
    elif missing >= 1:
        st.warning(f"{missing} oversight control(s) absent. Exceptions will be raised in the Trust Certificate.")

    st.session_state.gate_intake = d
    st.markdown("---")
    nl, nr = st.columns(2)
    with nl:
        if st.button("← Back", use_container_width=True):
            st.session_state.gate_step = 3
            st.rerun()
    with nr:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.gate_step = 5
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — ECOSYSTEM EXPOSURE
# ══════════════════════════════════════════════════════════════════════════════

elif step == 5:
    page_header()
    st.title("Trust Application — Ecosystem Exposure")
    st.caption("Measure the blast radius and supply chain trust exposure of this system.")
    st.markdown("---")
    step_progress(5)
    info_card("The more systems an autonomous agent connects to, the larger the failure blast radius. This section maps operational attack surface.")

    d = st.session_state.gate_intake

    d["connected_systems"] = st.multiselect(
        "Connected Production Systems",
        ["Banking / Payments", "EHR / Clinical Systems", "IAM / Identity", "ERP",
         "CRM", "DevOps / CI/CD", "Cloud Infrastructure", "Supply Chain",
         "Customer Communications", "Procurement"],
        default=d.get("connected_systems", []),
        help="Select all systems this autonomous agent can read from or write to"
    )

    st.markdown("")
    ec1, ec2 = st.columns(2)
    with ec1:
        d["third_party_tools"]        = st.toggle("Relies on third-party tools, plugins, or connectors",       value=d.get("third_party_tools", False))
        d["external_content"]         = st.toggle("Retrieves or processes untrusted external content",         value=d.get("external_content", False))
    with ec2:
        d["plugin_connector_actions"] = st.toggle("Executes actions via plugins or API connectors",            value=d.get("plugin_connector_actions", False))
        d["regulated_data_access"]    = st.toggle("Accesses regulated data (PII, PHI, PCI, financial records)", value=d.get("regulated_data_access", False))

    st.session_state.gate_intake = d
    st.markdown("---")
    nl, nr = st.columns(2)
    with nl:
        if st.button("← Back", use_container_width=True):
            st.session_state.gate_step = 4
            st.rerun()
    with nr:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.gate_step = 6
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — CONSEQUENCE & CONTROLS
# ══════════════════════════════════════════════════════════════════════════════

elif step == 6:
    page_header()
    st.title("Trust Application — Consequence & Governance Controls")
    st.caption("Classify the operational harm potential and declare existing governance controls.")
    st.markdown("---")
    step_progress(6)
    info_card("Consequence severity must be matched by governance maturity. A system with high consequence exposure and weak controls cannot be safely authorized for deployment.")

    d = st.session_state.gate_intake

    st.markdown("#### Consequence Severity")

    cc1, cc2 = st.columns(2)
    with cc1:
        d["financial_exposure"] = st.selectbox(
            "Financial Exposure",
            ["None", "Low", "Medium", "High", "Critical"],
            index=["None","Low","Medium","High","Critical"].index(d.get("financial_exposure","None")),
            help="Worst-case financial impact of an autonomous system failure or misaction"
        )
        d["safety_impact"]           = st.toggle("Could failure affect physical safety or patient outcomes",    value=d.get("safety_impact", False))
        d["legal_rights_impact"]     = st.toggle("Could failure affect legal rights, entitlements, or due process", value=d.get("legal_rights_impact", False))
        d["infrastructure_disruption"] = st.toggle("Could failure disrupt critical infrastructure or operations", value=d.get("infrastructure_disruption", False))
    with cc2:
        d["sensitive_data_exposure"] = st.toggle("Could failure expose sensitive, regulated, or personal data",  value=d.get("sensitive_data_exposure", False))
        d["regulatory_reporting"]    = st.toggle("Could failure trigger mandatory regulatory reporting",         value=d.get("regulatory_reporting", False))
        d["reputational_damage"]     = st.toggle("Could failure cause material reputational damage",             value=d.get("reputational_damage", False))

    st.markdown("---")
    st.markdown("#### Governance Controls — Declare What Exists")

    gc1, gc2 = st.columns(2)
    with gc1:
        d["audit_logging"]  = st.toggle("All actions are logged and auditable",                     value=d.get("audit_logging", False))
        d["incident_owner"] = st.toggle("Incident ownership is formally assigned",                  value=d.get("incident_owner", False))
    with gc2:
        d["policy_versioning"] = st.toggle("Policies, prompts, and models are versioned and change-controlled", value=d.get("policy_versioning", False))
        d["drift_monitoring"]  = st.toggle("System behavior is monitored for drift over time",      value=d.get("drift_monitoring", False))

    st.session_state.gate_intake = d
    st.markdown("---")
    nl, nr = st.columns(2)
    with nl:
        if st.button("← Back", use_container_width=True):
            st.session_state.gate_step = 5
            st.rerun()
    with nr:
        if st.button("Submit for Trust Evaluation", use_container_width=True, type="primary"):
            st.session_state.gate_step = "evaluating"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# EVALUATION ANIMATION SCREEN
# ══════════════════════════════════════════════════════════════════════════════

elif step == "evaluating":
    page_header()
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;padding:32px 0 16px 0;">'
        '<div style="color:#7dd3fc;font-size:0.78rem;font-weight:700;letter-spacing:0.16em;'
        'text-transform:uppercase;margin-bottom:12px;">TREASURETY GATE</div>'
        '<div style="color:white;font-size:2rem;font-weight:700;letter-spacing:-0.02em;margin-bottom:8px;">'
        'Operational Trust Evaluation</div>'
        '<div style="color:#475569;font-size:0.92rem;">'
        'Analyzing deployment authorization for autonomous system...</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    progress_bar = st.progress(0)
    status_slot  = st.empty()

    eval_phases = [
        ("Evaluating Authority Boundaries...",      "#8b5cf6"),
        ("Assessing Governance Maturity...",         "#3b82f6"),
        ("Mapping Ecosystem Exposure...",            "#0891b2"),
        ("Calculating Operational Trust Capacity...", "#f59e0b"),
        ("Validating Intervention Readiness...",     "#ea580c"),
        ("Determining Deployment Authorization...", "#16a34a"),
    ]

    completed = []
    for i, (phase_text, phase_color) in enumerate(eval_phases):
        time.sleep(0.65)
        completed.append((phase_text, phase_color))

        rows = ""
        for j, (txt, col) in enumerate(completed):
            is_cur = (j == len(completed) - 1)
            rows += (
                f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
                f'<div style="width:10px;height:10px;border-radius:50%;background:{col};flex-shrink:0;'
                f'{"box-shadow:0 0 10px " + col if is_cur else "opacity:0.5"}"></div>'
                f'<span style="color:{"#e2e8f0" if is_cur else "#334155"};font-size:0.9rem;'
                f'font-weight:{"600" if is_cur else "400"};">{txt}</span>'
                f'{"<span style=\"color:#16a34a;font-size:0.78rem;margin-left:auto;\">✓ Complete</span>" if not is_cur else ""}'
                f'</div>'
            )

        with status_slot.container():
            st.markdown(
                f'<div style="max-width:480px;margin:0 auto;background:#0f172a;'
                f'border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:28px 32px;">'
                f'{rows}'
                f'</div>',
                unsafe_allow_html=True
            )

        progress_bar.progress((i + 1) / len(eval_phases))

    time.sleep(0.5)

    results = evaluate_system(st.session_state.gate_intake)
    st.session_state.gate_results = results
    st.session_state.gate_step = "results"
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS — VERDICT + CERTIFICATE + MONITOR CTA
# ══════════════════════════════════════════════════════════════════════════════

elif step == "results":
    results = st.session_state.gate_results
    intake  = st.session_state.gate_intake
    if not results:
        st.session_state.gate_step = "landing"
        st.rerun()

    verdict     = results["verdict"]
    color       = results["color"]
    rationale   = results["rationale"]
    scores      = results["scores"]
    blockers    = results["blockers"]
    exceptions  = results["exceptions"]
    cert        = results["certificate"]
    system_name = intake.get("system_name", "Autonomous System")

    page_header()

    # ── VERDICT BANNER ─────────────────────────────────────────────────────────

    st.markdown(
        f'<div style="background:{color};border-radius:20px;padding:36px 40px;'
        f'margin-bottom:28px;text-align:center;">'
        f'<div style="color:rgba(255,255,255,0.6);font-size:0.75rem;font-weight:700;'
        f'letter-spacing:0.16em;text-transform:uppercase;margin-bottom:10px;">'
        f'TREASURETY GATE — DEPLOYMENT AUTHORIZATION VERDICT</div>'
        f'<div style="color:white;font-size:2.8rem;font-weight:900;letter-spacing:-0.02em;'
        f'margin-bottom:8px;">{verdict}</div>'
        f'<div style="color:rgba(255,255,255,0.75);font-size:0.92rem;max-width:640px;'
        f'margin:0 auto;line-height:1.6;">{system_name} — {cert["scope_summary"]}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── RATIONALE ──────────────────────────────────────────────────────────────

    st.markdown(
        f'<div style="background:#0f172a;border:1px solid rgba(255,255,255,0.06);'
        f'border-radius:14px;padding:24px 28px;margin-bottom:24px;">'
        f'<div style="color:#7dd3fc;font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.1em;margin-bottom:10px;">AUTHORIZATION RATIONALE</div>'
        f'<p style="color:#94a3b8;font-size:0.92rem;line-height:1.7;margin:0;">{rationale}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── CRITICAL BLOCKERS (if any) ─────────────────────────────────────────────

    if blockers:
        st.markdown(
            '<div style="color:#dc2626;font-size:0.78rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.1em;margin-bottom:10px;">CRITICAL BLOCKERS</div>',
            unsafe_allow_html=True
        )
        for b in blockers:
            st.markdown(
                f'<div style="background:rgba(220,38,38,0.08);border-left:3px solid #dc2626;'
                f'border-radius:6px;padding:10px 14px;margin-bottom:6px;">'
                f'<span style="color:#fca5a5;font-size:0.85rem;">{b}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown("")

    # ── DIMENSION SCORES ───────────────────────────────────────────────────────

    st.markdown(
        '<div style="color:#475569;font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;margin-bottom:12px;">EVALUATION DIMENSIONS</div>',
        unsafe_allow_html=True
    )

    dim_meta = [
        ("Authority Boundaries", "authority",   "Scope, enforcement, and delegation limits"),
        ("Human Oversight",      "oversight",   "Intervention, escalation, and kill-switch readiness"),
        ("Consequence Severity", "consequence", "Operational harm potential if system fails"),
        ("Ecosystem Exposure",   "ecosystem",   "Connected-system blast radius"),
        ("Governance Maturity",  "governance",  "Audit, versioning, and incident ownership"),
    ]

    d_cols = st.columns(5)
    for col, (label, key, desc) in zip(d_cols, dim_meta):
        s = scores[key]
        band, bc = score_band(s)
        with col:
            st.markdown(
                f'<div style="background:#0f172a;border:1px solid {bc};border-radius:12px;'
                f'padding:16px 12px;text-align:center;">'
                f'<div style="color:#94a3b8;font-size:0.68rem;font-weight:600;text-transform:uppercase;'
                f'letter-spacing:0.08em;margin-bottom:8px;">{label}</div>'
                f'<div style="color:white;font-size:2rem;font-weight:800;line-height:1;">{s}</div>'
                f'<div style="color:{bc};font-size:0.72rem;font-weight:600;margin-top:6px;">{band}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── RADAR CHART + EXCEPTIONS ───────────────────────────────────────────────

    left, right = st.columns([2, 3])

    with left:
        st.markdown("#### Trust Posture Map")

        radar_labels = [m[0] for m in dim_meta]
        radar_values = [scores[m[1]] for m in dim_meta]
        radar_labels_c = radar_labels + [radar_labels[0]]
        radar_values_c = radar_values + [radar_values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_values_c, theta=radar_labels_c,
            fill="toself",
            fillcolor="rgba(59,130,246,0.12)",
            line=dict(color="#3b82f6", width=2),
        ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(15,23,42,0.8)",
                radialaxis=dict(visible=True, range=[0, 100],
                    tickfont=dict(color="#64748b", size=8),
                    gridcolor="rgba(255,255,255,0.07)",
                    linecolor="rgba(255,255,255,0.07)"),
                angularaxis=dict(
                    tickfont=dict(color="#94a3b8", size=9),
                    gridcolor="rgba(255,255,255,0.07)",
                    linecolor="rgba(255,255,255,0.07)")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=310
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Key Findings")
        for exc in exceptions:
            sc = sev_color(exc["severity"])
            st.markdown(
                f'<div style="background:#0f172a;border-left:3px solid {sc};padding:14px 16px;'
                f'border-radius:8px;margin-bottom:10px;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
                f'<span style="background:{sc};color:white;font-size:0.66rem;font-weight:700;'
                f'padding:2px 8px;border-radius:4px;">{exc["severity"]}</span>'
                f'<span style="color:#e2e8f0;font-weight:600;font-size:0.83rem;">{exc["dimension"]}</span>'
                f'</div>'
                f'<p style="color:#94a3b8;font-size:0.82rem;margin:0;line-height:1.55;">'
                f'{exc["finding"]}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── TRUST CERTIFICATE ─────────────────────────────────────────────────────

    st.markdown(
        '<div style="color:#7dd3fc;font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.14em;margin-bottom:16px;">PROVISIONAL TRUST CERTIFICATE</div>',
        unsafe_allow_html=True
    )

    cert_status_color = {
        "Issued":                  "#16a34a",
        "Issued with Exceptions":  "#f59e0b",
        "Withheld":                "#dc2626",
    }.get(cert["certificate_status"], "#64748b")

    st.markdown(
        f'<div style="background:#0f172a;border:1px solid rgba(59,130,246,0.2);'
        f'border-radius:20px;padding:32px 36px;">'

        # Certificate header
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;'
        f'flex-wrap:wrap;gap:16px;margin-bottom:24px;padding-bottom:20px;'
        f'border-bottom:1px solid rgba(255,255,255,0.06);">'
        f'<div>'
        f'<div style="color:white;font-size:1.1rem;font-weight:700;margin-bottom:4px;">'
        f'Treasurety Gate — Operational Trust Certificate</div>'
        f'<div style="color:#475569;font-size:0.78rem;">'
        f'Provisional Self-Assessment · {cert["evidence_tier"]}</div>'
        f'</div>'
        f'<div style="background:{cert_status_color};color:white;font-weight:700;font-size:0.8rem;'
        f'padding:6px 16px;border-radius:8px;white-space:nowrap;">{cert["certificate_status"].upper()}</div>'
        f'</div>'

        # Certificate fields — two columns
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">'

        f'<div>'
        f'<div style="color:#7dd3fc;font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:10px;">Certificate Details</div>'
        f'<div style="color:#94a3b8;font-size:0.83rem;line-height:2;">'
        f'<b style="color:#e2e8f0;">Certificate ID:</b> {cert["certificate_id"]}<br>'
        f'<b style="color:#e2e8f0;">System Name:</b> {cert["system_name"]}<br>'
        f'<b style="color:#e2e8f0;">Industry:</b> {cert["industry"]}<br>'
        f'<b style="color:#e2e8f0;">System Type:</b> {cert["system_type"]}<br>'
        f'<b style="color:#e2e8f0;">Deployment Stage:</b> {cert.get("deployment_stage", "—")}'
        f'</div>'
        f'</div>'

        f'<div>'
        f'<div style="color:#7dd3fc;font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:10px;">Assessment Summary</div>'
        f'<div style="color:#94a3b8;font-size:0.83rem;line-height:2;">'
        f'<b style="color:#e2e8f0;">Assessment Date:</b> {cert["issued_date"]}<br>'
        f'<b style="color:#e2e8f0;">Certificate Valid Until:</b> {cert["expiry_date"]}<br>'
        f'<b style="color:#e2e8f0;">Validity Period:</b> {cert["validity_days"]} days<br>'
        f'<b style="color:#e2e8f0;">Assessment Method:</b> {cert["assessment_method"]}<br>'
        f'<b style="color:#e2e8f0;">Exceptions Raised:</b> {cert["exceptions_count"]}'
        f'</div>'
        f'</div>'

        f'</div>'

        # Scope summary
        f'<div style="background:#060d1a;border-radius:10px;padding:14px 18px;margin-bottom:20px;">'
        f'<div style="color:#475569;font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-bottom:6px;">Declared Scope</div>'
        f'<div style="color:#94a3b8;font-size:0.85rem;">{cert["scope_summary"]}</div>'
        f'</div>'

        # Verdict row
        f'<div style="background:{color};border-radius:10px;padding:16px 20px;text-align:center;'
        f'margin-bottom:20px;">'
        f'<div style="color:rgba(255,255,255,0.65);font-size:0.7rem;font-weight:700;'
        f'letter-spacing:0.14em;text-transform:uppercase;margin-bottom:4px;">AUTHORIZATION VERDICT</div>'
        f'<div style="color:white;font-size:1.5rem;font-weight:800;">{verdict}</div>'
        f'</div>'

        # Disclaimer
        f'<div style="color:#334155;font-size:0.75rem;line-height:1.6;">'
        f'This Trust Certificate reflects operational conditions at the time of assessment, based on self-declared inputs. '
        f'It is not a legal certification, regulatory approval, or government-recognized conformity assessment. '
        f'Validity is limited to the declared scope and expires on {cert["expiry_date"]}.'
        f'</div>'

        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ── MONITOR CONVERSION CTA ─────────────────────────────────────────────────

    st.markdown(
        '<div style="background:linear-gradient(135deg,#0a1628 0%,#0d1f3c 100%);'
        'border:1px solid rgba(59,130,246,0.2);border-radius:16px;padding:32px 36px;">'
        '<div style="color:#7dd3fc;font-size:0.72rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.14em;margin-bottom:12px;">CONTINUOUS ASSURANCE</div>'
        '<div style="color:white;font-size:1.25rem;font-weight:700;margin-bottom:12px;">'
        'Trust is temporal.</div>'
        '<p style="color:#94a3b8;font-size:0.9rem;line-height:1.7;max-width:620px;margin-bottom:0;">'
        'This Trust Certificate reflects operational conditions at the time of assessment.<br>'
        'Autonomous systems evolve. Dependencies change. Trust conditions degrade over time.<br><br>'
        '<b style="color:#e2e8f0;">Continuous assurance requires Treasurety Monitor™.</b>'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("")
    cta1, cta2, cta3 = st.columns([2, 2, 3])
    with cta1:
        if st.button("Activate Continuous Assurance", use_container_width=True, type="primary"):
            st.switch_page("pages/10_Treasurety_Monitor.py")
    with cta2:
        if st.button("Request Full Governance Assessment", use_container_width=True):
            st.switch_page("pages/9_Treasurety_Assess.py")
    with cta3:
        if st.button("Start New Trust Application", use_container_width=True):
            reset_gate()
            st.rerun()

    st.markdown("")
    st.markdown(
        '<p style="color:#1e293b;font-size:0.73rem;text-align:center;">'
        'Treasurety Gate — Operational Trust Certification Infrastructure for Agentic Systems · '
        'Provisional Certificate · Self-Assessment Tier'
        '</p>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# AI-NATIVE CONVERSATIONAL ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════

elif step == "ai_chat":
    page_header()

    # Initialize conversation on first entry
    if st.session_state.gate_ai_conv is None:
        conv = GateConversation()
        conv.start()
        st.session_state.gate_ai_conv = conv

    conv = st.session_state.gate_ai_conv

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="margin-bottom:4px;">'
        '<span style="background:rgba(59,130,246,0.12);color:#7dd3fc;font-size:0.72rem;'
        'font-weight:700;letter-spacing:0.14em;text-transform:uppercase;padding:4px 14px;'
        'border-radius:999px;border:1px solid rgba(59,130,246,0.3);">AI-NATIVE ASSESSMENT</span>'
        '</div>',
        unsafe_allow_html=True
    )

    # ── Progress bar (intake only) ────────────────────────────────────────────
    if not conv.complete:
        prog = conv.progress()
        st.progress(prog["pct"] / 100)
        st.caption(f"**{prog['stage_label']}** · Stage {prog['stage_number']} of {prog['total_stages']}"
                   f" · {prog['questions_done']} of {prog['total_questions']} questions")
    else:
        st.caption(f"Session `{conv.session_id}` — Assessment complete")

    st.markdown("---")

    # ── Message history ───────────────────────────────────────────────────────
    for msg in conv.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Post-verdict artifact panels ──────────────────────────────────────────
    if conv.complete:
        with st.expander("EPC State Object — JSON", expanded=False):
            st.code(conv.get_epc_json(), language="json")

    if conv.atc_path_active and conv.atc_pricing_epc:
        with st.expander("ATC Pricing EPC — JSON", expanded=False):
            st.code(conv.get_atc_pricing_json(), language="json")

    # ── Chat input or reset ───────────────────────────────────────────────────
    if conv.complete and not conv.awaiting_atc_decision and not conv.atc_path_active:
        st.markdown("")
        col1, _ = st.columns([2, 5])
        with col1:
            if st.button("Start New Assessment", use_container_width=True, type="primary"):
                reset_gate()
                st.rerun()
    else:
        placeholder = (
            "Type your answer or select a numbered option..."
            if not conv.awaiting_atc_decision
            else "Type 'yes' to proceed to ATC review, or 'no' to close..."
        )
        if prompt := st.chat_input(placeholder):
            conv.advance(prompt)
            st.rerun()
