import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(layout="wide")

def load_css():
    with open("assets/css.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── SCORING ENGINE ────────────────────────────────────────────────────────────

AUTHORITY_WEIGHTS = {
    "read_data": 5, "recommend": 10, "approve": 20, "execute": 30,
    "move_money": 35, "change_records": 25, "trigger_workflows": 20,
    "call_apis": 15, "invoke_agents": 25
}
AUTHORITY_MAX = sum(AUTHORITY_WEIGHTS.values())  # 185

def compute_scores(auth, drift, eco, ops, econ):
    auth_raw = sum(AUTHORITY_WEIGHTS[k] for k, v in auth.items() if v)
    authority = min(100, int((auth_raw / AUTHORITY_MAX) * 140))

    drift_score = int(
        (drift["prompt_fragility"] / 5) * 20 +
        (drift["context_dependency"] / 5) * 15 +
        (drift["model_volatility"] / 5) * 15 +
        (20 if drift["memory_persistence"] else 0) +
        (15 if drift["many_tools"] else 0) +
        (15 if drift["multi_llm"] else 0)
    )
    drift_risk = min(100, drift_score)

    eco_score = (
        (25 if eco["third_party_agents"] else 0) +
        (20 if eco["external_apis_many"] else 0) +
        (20 if eco["chained_orchestration"] else 0) +
        (20 if eco["delegated_authority"] else 0) +
        (15 if eco["vendor_dependency"] else 0)
    )
    ecosystem = min(100, eco_score)

    ops_score = (
        (0 if ops["human_intervention"] else 25) +
        (0 if ops["kill_switch"] else 25) +
        (0 if ops["rollback"] else 20) +
        (0 if ops["auditability"] else 20) +
        (0 if ops["escalation_path"] else 10)
    )
    ops_gov = ops_score  # already 0-100

    econ_score = int(
        {"low": 5, "medium": 15, "high": 30}[econ["token_sensitivity"]] +
        (25 if econ["supervision_burden"] else 5) +
        {"low": 5, "medium": 10, "high": 20}[econ["intervention_overhead"]] +
        (15 if econ["no_cost_controls"] else 0)
    )
    economic = min(100, econ_score)

    composite = int(
        0.30 * authority +
        0.20 * drift_risk +
        0.20 * ecosystem +
        0.20 * ops_gov +
        0.10 * economic
    )

    return {
        "authority": authority,
        "drift":     drift_risk,
        "ecosystem": ecosystem,
        "ops_gov":   ops_gov,
        "economic":  economic,
        "composite": composite
    }

def readiness_verdict(composite):
    if composite < 25:   return "READY",                 "#16a34a", "System demonstrates strong deployment readiness."
    elif composite < 45: return "READY WITH GOVERNANCE", "#0891b2", "Deploy with Treasurety Govern runtime controls active."
    elif composite < 65: return "PILOT ONLY",            "#f59e0b", "Restrict to controlled pilot. Do not expand to production."
    elif composite < 80: return "HOLD",                  "#ea580c", "Significant risk exposure. Remediate before any deployment."
    else:                return "BLOCK",                  "#dc2626", "Deployment blocked. Risk profile is incompatible with production."

def score_band(score):
    if score < 25:   return "Low",      "#16a34a"
    elif score < 50: return "Moderate", "#f59e0b"
    elif score < 75: return "High",     "#ea580c"
    else:            return "Critical", "#dc2626"

def generate_recommendations(scores, auth, ops):
    recs = []
    if scores["authority"] >= 60:
        recs.append(("Authority Risk", "CRITICAL", "Reduce autonomous execution authority or require Treasurety Govern runtime before deployment. Systems with broad execution power must operate under bounded authority controls."))
    elif scores["authority"] >= 35:
        recs.append(("Authority Risk", "MODERATE", "Document and constrain the delegation chain. Define explicit scope boundaries before production."))

    if scores["drift"] >= 60:
        recs.append(("Drift Risk", "HIGH", "Restrict to pilot environment. Implement prompt stability testing, model change freeze policy, and behavioral baselines before expanding."))
    elif scores["drift"] >= 35:
        recs.append(("Drift Risk", "MODERATE", "Deploy Treasurety Monitor to track behavioral drift before production expansion."))

    if scores["ecosystem"] >= 50:
        recs.append(("Ecosystem Risk", "HIGH", "Require Treasurety Shield before deployment. Third-party agent trust verification and API dependency audits are mandatory."))
    elif scores["ecosystem"] >= 30:
        recs.append(("Ecosystem Risk", "MODERATE", "Audit all external dependencies. Establish trust boundaries and vendor risk profiles."))

    if scores["ops_gov"] >= 60:
        recs.append(("Operational Governance", "CRITICAL", "Human intervention pathway, kill switch, and rollback controls are non-negotiable for production autonomous systems. Implement before any deployment."))
    elif scores["ops_gov"] >= 30:
        recs.append(("Operational Governance", "MODERATE", "Strengthen auditability and escalation pathways. Incomplete governance controls are a production liability."))

    if scores["economic"] >= 50:
        recs.append(("Economic Risk", "MODERATE", "Establish token cost controls and supervision cost budgets. Uncontrolled autonomous operation creates hidden financial exposure."))

    if not recs:
        recs.append(("Overall", "LOW", "System demonstrates strong deployment readiness. Proceed with standard Treasurety Govern runtime monitoring and periodic reassessment."))

    return recs

def recommend_modules(scores):
    modules = []
    if scores["composite"] >= 20:
        modules.append(("Treasurety Govern", "Runtime policy enforcement and execution authorization for all autonomous actions.", "#3b82f6"))
    if scores["ecosystem"] >= 35:
        modules.append(("Treasurety Shield", "Adversarial protection — prompt injection, agent impersonation, delegation forgery.", "#dc2626"))
    if scores["drift"] >= 35:
        modules.append(("Treasurety Monitor", "Continuous observability across autonomous agent behavior and execution patterns.", "#f59e0b"))
    if scores["composite"] >= 45:
        modules.append(("Treasurety Simulate", "Pre-production governance simulation and policy stress-testing.", "#8b5cf6"))
    if scores["ops_gov"] >= 40:
        modules.append(("Treasurety Memory", "Persistent governance context — execution history and override precedents.", "#06b6d4"))
    return modules


# ── DEMO DATA ─────────────────────────────────────────────────────────────────

DEMO_SYSTEM = {
    "name": "FinanceOps AI Agent",
    "use_case": "Autonomous accounts payable processing — invoice intake, approval routing, and payment release.",
    "owner": "Finance Operations / Platform Engineering",
    "domain": "Financial Services",
    "criticality": "High",
    "agent_type": "Multi-agent",
    "framework": "LangChain + custom orchestrator",
    "llm_providers": "OpenAI GPT-4o (primary), Anthropic Claude (fallback)",
    "memory": True,
    "tool_count": "6-10",
    "api_deps": True,
    "external_services": "SAP ERP, Stripe, NetSuite, Coupa",
}
DEMO_AUTH = {
    "read_data": True, "recommend": True, "approve": True, "execute": True,
    "move_money": True, "change_records": True, "trigger_workflows": True,
    "call_apis": True, "invoke_agents": True
}
DEMO_DRIFT = {
    "prompt_fragility": 4, "context_dependency": 4, "model_volatility": 3,
    "memory_persistence": True, "many_tools": True, "multi_llm": True
}
DEMO_ECO = {
    "third_party_agents": True, "external_apis_many": True,
    "chained_orchestration": True, "delegated_authority": True, "vendor_dependency": True
}
DEMO_OPS = {
    "human_intervention": False, "kill_switch": False,
    "rollback": False, "auditability": True, "escalation_path": False
}
DEMO_ECON = {
    "token_sensitivity": "high", "supervision_burden": True,
    "intervention_overhead": "high", "no_cost_controls": True
}


# ── SESSION STATE ─────────────────────────────────────────────────────────────

def init_state():
    if "assess_step" not in st.session_state:
        st.session_state.assess_step = 1
    if "assess_system" not in st.session_state:
        st.session_state.assess_system = {}
    if "assess_auth" not in st.session_state:
        st.session_state.assess_auth = {k: False for k in AUTHORITY_WEIGHTS}
    if "assess_drift" not in st.session_state:
        st.session_state.assess_drift = {"prompt_fragility": 3, "context_dependency": 3, "model_volatility": 2, "memory_persistence": False, "many_tools": False, "multi_llm": False}
    if "assess_eco" not in st.session_state:
        st.session_state.assess_eco = {k: False for k in ["third_party_agents", "external_apis_many", "chained_orchestration", "delegated_authority", "vendor_dependency"]}
    if "assess_ops" not in st.session_state:
        st.session_state.assess_ops = {k: False for k in ["human_intervention", "kill_switch", "rollback", "auditability", "escalation_path"]}
    if "assess_econ" not in st.session_state:
        st.session_state.assess_econ = {"token_sensitivity": "medium", "supervision_burden": False, "intervention_overhead": "medium", "no_cost_controls": False}

def load_demo():
    st.session_state.assess_system = DEMO_SYSTEM.copy()
    st.session_state.assess_auth = DEMO_AUTH.copy()
    st.session_state.assess_drift = DEMO_DRIFT.copy()
    st.session_state.assess_eco = DEMO_ECO.copy()
    st.session_state.assess_ops = DEMO_OPS.copy()
    st.session_state.assess_econ = DEMO_ECON.copy()

init_state()


# ── HEADER ────────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="margin-bottom:4px;">'
    '<span style="background:rgba(139,92,246,0.15);color:#c4b5fd;font-size:0.72rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:4px 14px;border-radius:999px;border:1px solid rgba(139,92,246,0.3);">TREASURETY ASSESS™</span>'
    '</div>',
    unsafe_allow_html=True
)

st.title("Pre-Deployment Readiness & Risk Assurance")
st.caption("Before autonomous systems enter production, Treasurety Assess determines whether they are ready.")

col_hero, col_demo = st.columns([4, 1])
with col_demo:
    if st.button("⚡ Load Demo System", use_container_width=True):
        load_demo()
        st.session_state.assess_step = 1
        st.rerun()

st.markdown("---")

# ── PROGRESS INDICATOR ────────────────────────────────────────────────────────

step = st.session_state.assess_step
steps_meta = [
    ("1", "System Profile"),
    ("2", "Risk Factors"),
    ("3", "Assessment"),
]

prog_html = '<div style="display:flex;align-items:center;gap:0;margin-bottom:24px;">'
for i, (num, label) in enumerate(steps_meta):
    active = (i + 1 == step)
    done   = (i + 1 < step)
    if done:
        circle_bg, circle_color, text_color = "#16a34a", "white", "#16a34a"
        num_display = "✓"
    elif active:
        circle_bg, circle_color, text_color = "#8b5cf6", "white", "#c4b5fd"
        num_display = num
    else:
        circle_bg, circle_color, text_color = "#1e293b", "#64748b", "#475569"
        num_display = num

    prog_html += (
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<div style="width:32px;height:32px;border-radius:50%;background:{circle_bg};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;color:{circle_color};flex-shrink:0;">{num_display}</div>'
        f'<span style="font-size:0.85rem;font-weight:600;color:{text_color};white-space:nowrap;">{label}</span>'
        f'</div>'
    )
    if i < len(steps_meta) - 1:
        prog_html += '<div style="flex:1;height:1px;background:#1e293b;margin:0 12px;min-width:20px;"></div>'

prog_html += '</div>'
st.markdown(prog_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — SYSTEM PROFILE
# ═══════════════════════════════════════════════════════════════════════════════

if step == 1:
    sys = st.session_state.assess_system
    auth = st.session_state.assess_auth

    st.markdown(
        '<div style="background:#0f172a;border-left:4px solid #8b5cf6;padding:14px 18px;border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">'
        'Provide core information about the autonomous system being assessed. This establishes the risk context.'
        '</div>',
        unsafe_allow_html=True
    )

    # ── SYSTEM INFORMATION ────────────────────────────────────────────────────
    st.markdown("#### System Information")
    c1, c2 = st.columns(2)
    with c1:
        sys["name"] = st.text_input("System Name", value=sys.get("name", ""), placeholder="e.g. FinanceOps AI Agent")
        sys["owner"] = st.text_input("Owner / Team", value=sys.get("owner", ""), placeholder="e.g. Platform Engineering")
        sys["domain"] = st.selectbox("Business Domain",
            ["Financial Services", "Healthcare", "Legal", "HR & People Ops", "Supply Chain",
             "Customer Operations", "IT & Infrastructure", "Sales & Marketing", "Research", "Other"],
            index=["Financial Services","Healthcare","Legal","HR & People Ops","Supply Chain",
                   "Customer Operations","IT & Infrastructure","Sales & Marketing","Research","Other"]
                   .index(sys.get("domain","Financial Services")) if sys.get("domain") else 0
        )
    with c2:
        sys["use_case"] = st.text_area("Use Case Description", value=sys.get("use_case", ""), height=100, placeholder="What does this system do autonomously?")
        sys["criticality"] = st.selectbox("Deployment Criticality",
            ["Low", "Medium", "High", "Mission Critical"],
            index=["Low","Medium","High","Mission Critical"].index(sys.get("criticality","Medium")) if sys.get("criticality") else 1
        )

    st.markdown("---")

    # ── ARCHITECTURE ──────────────────────────────────────────────────────────
    st.markdown("#### Architecture Profile")
    a1, a2 = st.columns(2)
    with a1:
        sys["agent_type"] = st.selectbox("Agent Architecture",
            ["Single agent", "Multi-agent", "Orchestrated agent fleet", "Agentic pipeline"],
            index=["Single agent","Multi-agent","Orchestrated agent fleet","Agentic pipeline"]
                  .index(sys.get("agent_type","Single agent")) if sys.get("agent_type") else 0
        )
        sys["framework"] = st.text_input("Orchestration Framework", value=sys.get("framework",""), placeholder="e.g. LangChain, AutoGen, custom")
        sys["llm_providers"] = st.text_input("LLM Provider(s)", value=sys.get("llm_providers",""), placeholder="e.g. OpenAI, Anthropic, Azure")
    with a2:
        sys["memory"] = st.toggle("Memory / Persistence Enabled", value=sys.get("memory", False))
        sys["tool_count"] = st.selectbox("Tool Count",
            ["None", "1-2", "3-5", "6-10", "10+"],
            index=["None","1-2","3-5","6-10","10+"].index(sys.get("tool_count","1-2")) if sys.get("tool_count") else 1
        )
        sys["api_deps"] = st.toggle("External API Dependencies", value=sys.get("api_deps", False))
        sys["external_services"] = st.text_input("External Services / Integrations", value=sys.get("external_services",""), placeholder="e.g. Salesforce, SAP, Stripe")

    st.markdown("---")

    # ── AUTHORITY PROFILE ─────────────────────────────────────────────────────
    st.markdown("#### Authority Profile")
    st.caption("Can this autonomous system do any of the following?")

    capabilities = [
        ("read_data",         "Read data",                    "Access and retrieve data from systems"),
        ("recommend",         "Recommend actions",            "Propose actions for human review"),
        ("approve",           "Approve actions",              "Approve requests or actions autonomously"),
        ("execute",           "Execute actions",              "Take actions without human confirmation"),
        ("move_money",        "Move money",                   "Initiate or approve financial transactions"),
        ("change_records",    "Change records",               "Modify data in authoritative systems"),
        ("trigger_workflows", "Trigger workflows",            "Start automated processes or pipelines"),
        ("call_apis",         "Call external APIs",           "Invoke third-party services autonomously"),
        ("invoke_agents",     "Invoke other agents",          "Delegate tasks to or orchestrate other AI agents"),
    ]

    cols = st.columns(3)
    for i, (key, label, desc) in enumerate(capabilities):
        with cols[i % 3]:
            auth[key] = st.toggle(
                label,
                value=auth.get(key, False),
                help=desc,
                key=f"auth_{key}"
            )

    st.session_state.assess_system = sys
    st.session_state.assess_auth = auth

    st.markdown("---")
    _, nav_right = st.columns([4, 1])
    with nav_right:
        if sys.get("name"):
            if st.button("Next: Risk Factors →", use_container_width=True, type="primary"):
                st.session_state.assess_step = 2
                st.rerun()
        else:
            st.button("Next: Risk Factors →", use_container_width=True, disabled=True, help="Enter system name to continue")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — RISK FACTORS
# ═══════════════════════════════════════════════════════════════════════════════

elif step == 2:
    drift = st.session_state.assess_drift
    eco   = st.session_state.assess_eco
    ops   = st.session_state.assess_ops
    econ  = st.session_state.assess_econ

    st.markdown(
        '<div style="background:#0f172a;border-left:4px solid #8b5cf6;padding:14px 18px;border-radius:8px;margin-bottom:20px;color:#94a3b8;font-size:0.88rem;">'
        'Characterise the risk profile across four dimensions. Honest inputs produce accurate assessments.'
        '</div>',
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4 = st.tabs(["Drift Risk", "Ecosystem Risk", "Operational Governance", "Economic Risk"])

    # ── DRIFT RISK ────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("**How stable and predictable is this system's behaviour over time?**")
        st.markdown("")

        drift["prompt_fragility"] = st.slider(
            "Prompt Fragility — how sensitive is behaviour to prompt changes?",
            1, 5, value=drift.get("prompt_fragility", 3),
            help="1 = highly stable, 5 = highly sensitive"
        )
        drift["context_dependency"] = st.slider(
            "Context Dependency — how much does behaviour depend on conversation/session state?",
            1, 5, value=drift.get("context_dependency", 3),
            help="1 = stateless, 5 = heavily context-dependent"
        )
        drift["model_volatility"] = st.slider(
            "Model Change Risk — how frequently does the underlying model version change?",
            1, 5, value=drift.get("model_volatility", 2),
            help="1 = frozen/pinned, 5 = unpinned/frequently updated"
        )
        st.markdown("")
        drift["memory_persistence"] = st.toggle(
            "Memory or state persists across sessions",
            value=drift.get("memory_persistence", False),
            help="Persistent memory can accumulate mutations over time"
        )
        drift["many_tools"] = st.toggle(
            "System uses 6 or more tools",
            value=drift.get("many_tools", False),
            help="More tools introduces more unpredictable behaviour surfaces"
        )
        drift["multi_llm"] = st.toggle(
            "Multiple LLM providers (fallback or routing)",
            value=drift.get("multi_llm", False),
            help="Multi-provider setups introduce model behaviour inconsistency"
        )

    # ── ECOSYSTEM RISK ────────────────────────────────────────────────────────
    with tab2:
        st.markdown("**How exposed is this system to third-party trust dependencies?**")
        st.markdown("")

        eco["third_party_agents"] = st.toggle("Involves third-party or external AI agents", value=eco.get("third_party_agents", False))
        eco["external_apis_many"] = st.toggle("Calls more than 3 external APIs", value=eco.get("external_apis_many", False))
        eco["chained_orchestration"] = st.toggle("Uses chained or multi-hop agent orchestration", value=eco.get("chained_orchestration", False))
        eco["delegated_authority"] = st.toggle("Authority is delegated from another system or agent", value=eco.get("delegated_authority", False))
        eco["vendor_dependency"] = st.toggle("Critical dependency on a single vendor's infrastructure", value=eco.get("vendor_dependency", False))

    # ── OPERATIONAL GOVERNANCE ────────────────────────────────────────────────
    with tab3:
        st.markdown("**What governance controls are already in place?** (check what exists)")
        st.markdown("")

        ops["human_intervention"] = st.toggle("Human intervention pathway exists", value=ops.get("human_intervention", False), help="Can a human pause or override the system in real-time?")
        ops["kill_switch"] = st.toggle("Kill switch / emergency stop implemented", value=ops.get("kill_switch", False))
        ops["rollback"] = st.toggle("Rollback or undo capability exists", value=ops.get("rollback", False))
        ops["auditability"] = st.toggle("All actions are logged and auditable", value=ops.get("auditability", False))
        ops["escalation_path"] = st.toggle("Defined escalation path for unexpected behaviour", value=ops.get("escalation_path", False))

        missing = sum(1 for v in ops.values() if not v)
        if missing >= 3:
            st.error(f"⚠ {missing} of 5 governance controls are missing — this significantly increases operational risk.")
        elif missing >= 1:
            st.warning(f"{missing} governance control(s) missing.")
        else:
            st.success("All operational governance controls are present.")

    # ── ECONOMIC RISK ─────────────────────────────────────────────────────────
    with tab4:
        st.markdown("**What is the economic exposure profile of this system?**")
        st.markdown("")

        econ["token_sensitivity"] = st.selectbox(
            "Token / compute cost sensitivity",
            ["low", "medium", "high"],
            index=["low","medium","high"].index(econ.get("token_sensitivity","medium")),
            format_func=lambda x: x.capitalize()
        )
        econ["supervision_burden"] = st.toggle(
            "Significant human supervision cost expected",
            value=econ.get("supervision_burden", False),
            help="Does correct operation require substantial ongoing human oversight?"
        )
        econ["intervention_overhead"] = st.selectbox(
            "Expected intervention overhead",
            ["low", "medium", "high"],
            index=["low","medium","high"].index(econ.get("intervention_overhead","medium")),
            format_func=lambda x: x.capitalize()
        )
        econ["no_cost_controls"] = st.toggle(
            "No cost controls or spend limits implemented",
            value=econ.get("no_cost_controls", False)
        )

    st.session_state.assess_drift = drift
    st.session_state.assess_eco   = eco
    st.session_state.assess_ops   = ops
    st.session_state.assess_econ  = econ

    st.markdown("---")
    nav_left, nav_right = st.columns([1, 1])
    with nav_left:
        if st.button("← Back: System Profile", use_container_width=True):
            st.session_state.assess_step = 1
            st.rerun()
    with nav_right:
        if st.button("Run Assessment →", use_container_width=True, type="primary"):
            st.session_state.assess_step = 3
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — ASSESSMENT RESULTS
# ═══════════════════════════════════════════════════════════════════════════════

elif step == 3:
    sys   = st.session_state.assess_system
    auth  = st.session_state.assess_auth
    drift = st.session_state.assess_drift
    eco   = st.session_state.assess_eco
    ops   = st.session_state.assess_ops
    econ  = st.session_state.assess_econ

    scores = compute_scores(auth, drift, eco, ops, econ)
    verdict, verdict_color, verdict_desc = readiness_verdict(scores["composite"])
    recs = generate_recommendations(scores, auth, ops)
    modules = recommend_modules(scores)

    # ── VERDICT BANNER ────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{verdict_color};border-radius:16px;padding:28px 32px;margin-bottom:24px;text-align:center;">'
        f'<div style="color:rgba(255,255,255,0.7);font-size:0.8rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">DEPLOYMENT READINESS DECISION</div>'
        f'<div style="color:white;font-size:2.4rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:6px;">{verdict}</div>'
        f'<div style="color:rgba(255,255,255,0.85);font-size:1rem;">{sys.get("name","Assessed System")} — Composite Risk Score: {scores["composite"]}/100</div>'
        f'<div style="color:rgba(255,255,255,0.7);font-size:0.88rem;margin-top:6px;">{verdict_desc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── DIMENSION SCORECARDS ──────────────────────────────────────────────────
    st.markdown("#### Risk Dimension Scores")

    dim_labels = ["Authority Risk", "Drift Risk", "Ecosystem Risk", "Ops Governance", "Economic Risk"]
    dim_keys   = ["authority",      "drift",      "ecosystem",       "ops_gov",        "economic"]

    d_cols = st.columns(5)
    for col, label, key in zip(d_cols, dim_labels, dim_keys):
        score = scores[key]
        band, bcolor = score_band(score)
        with col:
            st.markdown(
                f'<div style="background:#0f172a;border:1px solid {bcolor};border-radius:12px;padding:16px;text-align:center;">'
                f'<div style="color:#94a3b8;font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">{label}</div>'
                f'<div style="color:white;font-size:2rem;font-weight:800;line-height:1;">{score}</div>'
                f'<div style="color:{bcolor};font-size:0.78rem;font-weight:600;margin-top:6px;">{band}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── RADAR CHART + RECOMMENDATIONS ────────────────────────────────────────
    left, right = st.columns([2, 3])

    with left:
        st.markdown("#### Risk Heatmap")

        radar_labels = dim_labels + [dim_labels[0]]
        radar_values = [scores[k] for k in dim_keys] + [scores[dim_keys[0]]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill='toself',
            fillcolor='rgba(139,92,246,0.15)',
            line=dict(color='#8b5cf6', width=2),
            name="Risk Profile"
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(15,23,42,0.8)',
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(color="#64748b", size=9), gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)"),
                angularaxis=dict(tickfont=dict(color="#94a3b8", size=10), gridcolor="rgba(255,255,255,0.07)", linecolor="rgba(255,255,255,0.07)")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("#### Recommendations")

        sev_colors = {"CRITICAL": "#dc2626", "HIGH": "#ea580c", "MODERATE": "#f59e0b", "LOW": "#16a34a"}
        for dim, severity, rec_text in recs:
            sc = sev_colors.get(severity, "#64748b")
            st.markdown(
                f'<div style="background:#0f172a;border-left:3px solid {sc};padding:12px 16px;border-radius:8px;margin-bottom:8px;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">'
                f'<span style="background:{sc};color:white;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">{severity}</span>'
                f'<span style="color:#e2e8f0;font-weight:600;font-size:0.85rem;">{dim}</span>'
                f'</div>'
                f'<p style="color:#94a3b8;font-size:0.82rem;margin:0;line-height:1.5;">{rec_text}</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    # ── RECOMMENDED MODULES ───────────────────────────────────────────────────
    if modules:
        st.markdown("#### Recommended Treasurety Modules")
        m_cols = st.columns(len(modules))
        for col, (mod_name, mod_desc, mod_color) in zip(m_cols, modules):
            with col:
                st.markdown(
                    f'<div style="background:#0f172a;border:1px solid {mod_color};border-radius:12px;padding:16px;text-align:center;height:100%;">'
                    f'<div style="color:{mod_color};font-weight:700;font-size:0.85rem;margin-bottom:8px;">{mod_name}</div>'
                    f'<div style="color:#64748b;font-size:0.78rem;line-height:1.5;">{mod_desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("")

    # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### Executive Summary")

    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    gov_gaps = [label for label, key in zip(["Human Intervention","Kill Switch","Rollback","Auditability","Escalation Path"],
                                              ["human_intervention","kill_switch","rollback","auditability","escalation_path"])
                if not ops.get(key)]
    auth_caps = [label for key, label, _ in [
        ("execute","Autonomous Execution",None),("move_money","Financial Transactions",None),
        ("change_records","Record Modification",None),("invoke_agents","Agent Delegation",None)]
        if auth.get(key)]

    st.markdown(
        f'<div style="background:#0f172a;border:1px solid rgba(139,92,246,0.2);border-radius:16px;padding:28px 32px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;margin-bottom:20px;">'
        f'<div>'
        f'<div style="color:white;font-size:1.2rem;font-weight:700;margin-bottom:4px;">{sys.get("name","Autonomous System")} — Treasurety Assess™ Report</div>'
        f'<div style="color:#64748b;font-size:0.8rem;">{sys.get("domain","—")} · {sys.get("criticality","—")} Criticality · {ts}</div>'
        f'</div>'
        f'<div style="background:{verdict_color};color:white;font-weight:700;font-size:0.9rem;padding:6px 20px;border-radius:8px;">{verdict}</div>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
        f'<div>'
        f'<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">System Profile</div>'
        f'<div style="color:#94a3b8;font-size:0.82rem;line-height:1.8;">'
        f'<b style="color:#e2e8f0;">Architecture:</b> {sys.get("agent_type","—")}<br>'
        f'<b style="color:#e2e8f0;">Framework:</b> {sys.get("framework","—")}<br>'
        f'<b style="color:#e2e8f0;">LLM:</b> {sys.get("llm_providers","—")}<br>'
        f'<b style="color:#e2e8f0;">Owner:</b> {sys.get("owner","—")}'
        f'</div>'
        f'</div>'
        f'<div>'
        f'<div style="color:#7dd3fc;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Risk Summary</div>'
        f'<div style="color:#94a3b8;font-size:0.82rem;line-height:1.8;">'
        f'<b style="color:#e2e8f0;">Composite Score:</b> {scores["composite"]}/100<br>'
        f'<b style="color:#e2e8f0;">Highest Risk:</b> {dim_labels[dim_keys.index(max(dim_keys, key=lambda k: scores[k]))]}<br>'
        f'<b style="color:#e2e8f0;">Execution Authority:</b> {", ".join(auth_caps) if auth_caps else "None"}<br>'
        f'<b style="color:#e2e8f0;">Governance Gaps:</b> {", ".join(gov_gaps) if gov_gaps else "None"}'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown(
        '<p style="color:#334155;font-size:0.75rem;text-align:center;margin-top:8px;">'
        'Treasurety Assess™ — Partner-ready · White-label capable · Outputs feed Treasurety Govern policy engine'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    nav_l, _, nav_r = st.columns([1, 3, 1])
    with nav_l:
        if st.button("← Back: Risk Factors", use_container_width=True):
            st.session_state.assess_step = 2
            st.rerun()
    with nav_r:
        if st.button("New Assessment", use_container_width=True):
            for key in ["assess_step","assess_system","assess_auth","assess_drift","assess_eco","assess_ops","assess_econ"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
