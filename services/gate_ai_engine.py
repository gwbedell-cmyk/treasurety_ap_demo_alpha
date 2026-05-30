"""
Treasurety Gate AI — EPC Conversational Assessment Engine
AI-native intake for Agentic Trust Certificate (ATC) assessment.

Treasurety Gate is the front door. Treasurety Govern is the engine.
"""

import uuid
import json
from datetime import datetime
from typing import Any


# ── STAGE SEQUENCE ─────────────────────────────────────────────────────────────

STAGES = [
    "system_identity",
    "agentic_scope",
    "authority_mapping",
    "financial_exposure",
    "governance_controls",
    "evidence_readiness",
    "ecosystem_exposure",
    "monitoring_readiness",
    "verdict",
]

STAGE_LABELS = {
    "system_identity":      "Stage 1 — System Identity",
    "agentic_scope":        "Stage 2 — Agentic Scope",
    "authority_mapping":    "Stage 3 — Authority Mapping",
    "financial_exposure":   "Stage 4 — Financial & Operational Exposure",
    "governance_controls":  "Stage 5 — Governance Controls",
    "evidence_readiness":   "Stage 6 — Evidence Readiness",
    "ecosystem_exposure":   "Stage 7 — Ecosystem & Threat Exposure",
    "monitoring_readiness": "Stage 8 — Monitoring Readiness",
    "verdict":              "Stage 9 — Verdict",
}

STAGE_INTROS = {
    "system_identity": (
        "Treasurety Gate is the front door to Agentic Trust Certification. "
        "Before we can assess your system, we need to understand what it is and where it operates.\n\n"
        "Answer precisely. The accuracy of your ATC assessment depends on what you declare here."
    ),
    "agentic_scope": (
        "We now map the operational scope of your agentic system — "
        "how many agents, which workflows, and how much autonomy this system exercises."
    ),
    "authority_mapping": (
        "Authority mapping is the most critical stage of this assessment. "
        "The authority you grant an autonomous system directly determines its risk profile. "
        "Answer each question precisely — authority determines risk."
    ),
    "financial_exposure": (
        "We now quantify the financial and operational exposure this system carries. "
        "High exposure without commensurate governance controls is a primary ATC risk factor."
    ),
    "governance_controls": (
        "Governance controls determine whether this system can be trusted to operate. "
        "We are assessing actual controls — not documented intentions. "
        "Treasurety Govern is the runtime engine that enforces these controls in production."
    ),
    "evidence_readiness": (
        "The ATC system review examines the system itself — its architecture, authority, "
        "controls, and operational history. "
        "This stage assesses whether the evidence package supporting that review is ready. "
        "The review object is the system, not the documents."
    ),
    "ecosystem_exposure": (
        "An autonomous system is only as trustworthy as its dependencies. "
        "This stage maps your ecosystem exposure. "
        "Elevated threat surface routes to Treasurety Shield before ATC assessment."
    ),
    "monitoring_readiness": (
        "Trust is temporal. An ATC reflects conditions at the time of assessment. "
        "Continuous assurance requires Treasurety Monitor — "
        "but Monitor can only activate after a valid ATC is issued. "
        "This stage assesses your readiness for continuous assurance."
    ),
}


# ── QUESTION BANK ──────────────────────────────────────────────────────────────

QUESTIONS: dict[str, list[dict]] = {
    "system_identity": [
        {"key": "organization",    "type": "text",
         "text": "What is the name of your organization?"},
        {"key": "system_name",     "type": "text",
         "text": "What is the name of the system or agent being submitted for assessment?"},
        {"key": "system_type",     "type": "choice",
         "text": "How would you classify this system?",
         "options": [
             "Single autonomous agent",
             "Multi-agent system",
             "AI workflow automation",
             "AI decision support",
             "AI execution agent",
             "AI copilot with tool access",
             "AI orchestration layer",
             "RPA + LLM hybrid",
             "Third-party autonomous vendor system",
         ]},
        {"key": "business_function", "type": "text",
         "text": "What is the primary business function this system performs?",
         "hint": "e.g. Accounts payable processing, patient triage, contract review, procurement automation"},
        {"key": "deployment_status", "type": "choice",
         "text": "What is the current deployment status?",
         "options": ["Planned", "Pilot", "Production", "Scaling"]},
        {"key": "industry",          "type": "choice",
         "text": "What industry or sector does this system operate in?",
         "options": [
             "Financial Services", "Healthcare", "Manufacturing",
             "Supply Chain & Logistics", "Insurance", "Energy & Utilities",
             "Government", "Cybersecurity", "Enterprise Operations",
             "AI Infrastructure", "Multi-Agent Orchestration", "Other",
         ]},
    ],
    "agentic_scope": [
        {"key": "agent_count",    "type": "choice",
         "text": "How many agents or automated processes does this system comprise?",
         "options": ["1", "2–5", "6–20", "21–100", "100+", "Unknown"]},
        {"key": "workflow_count", "type": "choice",
         "text": "How many distinct workflows can this system initiate or execute?",
         "options": ["1–3", "4–10", "11–50", "50+", "Unknown"]},
        {"key": "autonomy_level", "type": "choice",
         "text": "To what extent do agents act without human confirmation?",
         "options": [
             "Fully supervised — every action requires human approval",
             "Mostly supervised — exceptions require approval",
             "Semi-autonomous — high-risk actions require approval",
             "Mostly autonomous — human reviews after the fact",
             "Fully autonomous — no routine human checkpoints",
         ]},
        {"key": "external_system_access", "type": "bool",
         "text": "Does this system interact with external systems, APIs, or third-party services?"},
        {"key": "real_world_outcomes",    "type": "bool",
         "text": "Can this system trigger real-world outcomes — financial transactions, "
                 "communications, record changes, or operational decisions — without human confirmation of each action?"},
    ],
    "authority_mapping": [
        {"key": "read_only",                   "type": "bool",
         "text": "Does the system have read-only data access — no write authority, no action execution?"},
        {"key": "recommendation",              "type": "bool",
         "text": "Does the system make recommendations that humans then act on?"},
        {"key": "approval",                    "type": "bool",
         "text": "Does the system have authority to approve requests, workflows, or access?"},
        {"key": "transaction_initiation",      "type": "bool",
         "text": "Can the system initiate transactions or business processes autonomously?"},
        {"key": "payment_execution",           "type": "bool",   "risk_flag": True,
         "text": "Can the system execute payments or move funds?"},
        {"key": "contract_or_vendor_authority","type": "bool",   "risk_flag": True,
         "text": "Can the system make or approve contracts, vendor selections, or procurement decisions?"},
        {"key": "system_modification_authority","type": "bool",  "risk_flag": True,
         "text": "Can the system modify other systems, permissions, records, or workflows?"},
    ],
    "financial_exposure": [
        {"key": "monthly_transaction_volume", "type": "choice",
         "text": "Approximate monthly transaction volume this system processes or influences?",
         "options": ["Under $10K", "$10K–$100K", "$100K–$1M", "$1M–$10M",
                     "Over $10M", "Not applicable", "Unknown"]},
        {"key": "max_single_action_exposure", "type": "choice",
         "text": "Maximum financial exposure of a single autonomous action?",
         "options": ["Under $1K", "$1K–$10K", "$10K–$100K", "$100K–$1M",
                     "Over $1M", "Not applicable", "Unknown"]},
        {"key": "money_movement",                 "type": "bool",
         "text": "Can this system directly move money — payments, transfers, or fund releases?"},
        {"key": "customer_vendor_obligations",    "type": "bool",
         "text": "Can this system create binding obligations with customers or vendors?"},
        {"key": "legal_or_compliance_consequence","type": "bool",
         "text": "Can a system error or misaction trigger legal, regulatory, or compliance consequences?"},
        {"key": "human_override",                 "type": "bool",
         "text": "Is there a reliable human override mechanism that can stop or reverse autonomous actions?"},
    ],
    "governance_controls": [
        {"key": "human_approval", "type": "choice",
         "text": "Describe the human approval checkpoints in this system.",
         "options": [
             "Pre-action approval required for all actions",
             "Pre-action approval for high-risk actions only",
             "Post-action review with escalation path",
             "Sampled review only",
             "Exception-based review",
             "No human approval checkpoints",
         ]},
        {"key": "segregation_of_duties", "type": "choice",
         "text": "Is segregation of duties enforced — no single agent can both initiate and approve a consequential action?",
         "options": ["Yes — enforced technically", "Yes — enforced by policy",
                     "Partially", "No", "Not applicable"]},
        {"key": "policy_constraints", "type": "choice",
         "text": "Are machine-enforceable policy constraints in place that limit what this system can do?",
         "options": ["Yes — hard technical limits", "Yes — soft policy limits", "Partially", "No"]},
        {"key": "audit_logs", "type": "choice",
         "text": "Are all system actions logged with sufficient detail for forensic reconstruction?",
         "options": ["Yes — complete and tamper-evident", "Yes — complete but not tamper-evident",
                     "Partial", "No"]},
        {"key": "fail_closed", "type": "bool",
         "text": "Does the system fail closed — defaulting to no action on error or ambiguity?"},
        {"key": "exception_handling", "type": "bool",
         "text": "Is there documented exception handling that routes edge cases to human review?"},
        {"key": "escalation_logic",   "type": "bool",
         "text": "Are escalation paths formally defined and operationally tested?"},
        {"key": "permission_boundaries", "type": "bool",
         "text": "Are permission boundaries machine-enforced — not just stated in policy?"},
        {"key": "rollback_controls", "type": "choice",
         "text": "Can the effects of erroneous autonomous actions be reversed?",
         "options": ["Yes — automated rollback", "Yes — manual rollback process",
                     "Partially", "No", "Not applicable"]},
    ],
    "evidence_readiness": [
        {"key": "system_documentation", "type": "choice",
         "text": "Complete system architecture and operational documentation?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "governance_policies",  "type": "choice",
         "text": "Governance policies covering authority limits, escalation, and exception handling?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "access_control_records","type": "choice",
         "text": "Access control configurations and permission records — current and auditable?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "audit_logs_evidence",  "type": "choice",
         "text": "Audit logs available and sufficient to support an independent system review?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "risk_assessment",      "type": "choice",
         "text": "Formal risk assessment completed for this system?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "incident_history",     "type": "choice",
         "text": "Incident history — including near-misses and anomalies — documented and available?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "agent_architecture",   "type": "choice",
         "text": "Agent model architecture, prompt design, tool access, and decision logic documented?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "vendor_documentation", "type": "choice",
         "text": "Vendor and dependency documentation — including third-party AI components — current?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
    ],
    "ecosystem_exposure": [
        {"key": "third_party_vendors", "type": "choice",
         "text": "Does this system rely on third-party vendors or AI providers whose governance posture is not fully known?",
         "options": [
             "No third-party dependencies",
             "Known vendors with strong governance",
             "Known vendors with unknown governance",
             "Unknown vendors or dependencies",
             "Multiple unaudited dependencies",
         ]},
        {"key": "external_apis", "type": "choice",
         "text": "How many external APIs does this system call, and are they audited?",
         "options": ["None", "1–3, all audited", "1–3, not all audited",
                     "4–10, all audited", "4–10, not all audited", "10+", "Unknown"]},
        {"key": "payment_rails",               "type": "bool",
         "text": "Does the system connect to payment infrastructure — ACH, wire, card networks, or payment APIs?"},
        {"key": "erp_crm_integrations",        "type": "bool",
         "text": "Does the system integrate with ERP or CRM systems containing authoritative business records?"},
        {"key": "cloud_dependencies",          "type": "bool",
         "text": "Are there critical cloud infrastructure dependencies where a failure could cascade?"},
        {"key": "data_sensitivity", "type": "choice",
         "text": "What is the sensitivity level of data this system accesses or processes?",
         "options": [
             "Public or non-sensitive",
             "Internal business data",
             "Confidential / proprietary",
             "Regulated data (PII, PHI, PCI, financial records)",
             "Multiple regulated data classes",
         ]},
        {"key": "adversarial_exposure", "type": "choice",
         "text": "Is this system exposed to adversarial input — prompt injection, malicious data, or untrusted external content?",
         "options": [
             "No external content ingestion",
             "Limited, with input validation",
             "Moderate, partially mitigated",
             "High, with known exposure",
             "Unknown",
         ]},
        {"key": "critical_infrastructure_connection", "type": "bool",
         "text": "Does this system connect to or control critical infrastructure — energy, utilities, healthcare systems, or financial market infrastructure?"},
    ],
    "monitoring_readiness": [
        {"key": "telemetry", "type": "choice",
         "text": "Does operational telemetry exist — capturing performance, error rates, and action volumes?",
         "options": ["Comprehensive", "Partial", "Minimal", "None"]},
        {"key": "governance_events", "type": "choice",
         "text": "Are governance events — policy violations, escalations, human overrides — captured in a structured log?",
         "options": ["Comprehensive", "Partial", "Minimal", "None"]},
        {"key": "drift_signals", "type": "choice",
         "text": "Are there mechanisms to detect behavioral drift — the system acting outside intended parameters?",
         "options": ["Active monitoring", "Periodic review", "Ad hoc", "None"]},
        {"key": "runtime_logs", "type": "choice",
         "text": "Are runtime decision logs available — recording what the system decided, why, and with what inputs?",
         "options": ["Complete", "Partial", "Minimal", "None"]},
        {"key": "exception_logs", "type": "choice",
         "text": "Are exception and anomaly logs captured and reviewed on a defined cadence?",
         "options": ["Complete and reviewed", "Captured but infrequently reviewed", "Partial", "None"]},
        {"key": "certificate_verification_readiness", "type": "bool",
         "text": "Is the system instrumented to verify an active Agentic Trust Certificate before operating?"},
        {"key": "continuous_assurance_readiness",     "type": "bool",
         "text": "Is the system designed to support continuous assurance — real-time trust posture monitoring?"},
    ],
}


# ── SCORING ENGINE ─────────────────────────────────────────────────────────────

def _bool(v: Any) -> bool:
    if isinstance(v, bool): return v
    if isinstance(v, str):  return v.lower() in ("yes", "true", "1", "y")
    return False


def _governance_score(state: dict) -> int:
    gc = state.get("governance_controls", {})
    score = 0
    score += {"Pre-action approval required for all actions": 25,
              "Pre-action approval for high-risk actions only": 18,
              "Post-action review with escalation path": 12,
              "Sampled review only": 6,
              "Exception-based review": 3,
              "No human approval checkpoints": 0,
              }.get(gc.get("human_approval", ""), 0)
    score += {"Yes — enforced technically": 15, "Yes — enforced by policy": 10,
              "Partially": 5, "No": 0, "Not applicable": 8,
              }.get(gc.get("segregation_of_duties", ""), 0)
    score += {"Yes — hard technical limits": 15, "Yes — soft policy limits": 10,
              "Partially": 5, "No": 0,
              }.get(gc.get("policy_constraints", ""), 0)
    score += {"Yes — complete and tamper-evident": 15,
              "Yes — complete but not tamper-evident": 10,
              "Partial": 5, "No": 0,
              }.get(gc.get("audit_logs", ""), 0)
    if _bool(gc.get("fail_closed")):          score += 10
    if _bool(gc.get("exception_handling")):   score += 5
    if _bool(gc.get("escalation_logic")):     score += 5
    if _bool(gc.get("permission_boundaries")):score += 5
    score += {"Yes — automated rollback": 5, "Yes — manual rollback process": 3,
              "Partially": 1, "No": 0, "Not applicable": 3,
              }.get(gc.get("rollback_controls", ""), 0)
    return min(100, score)


def _evidence_score(state: dict) -> int:
    ev = state.get("evidence_readiness", {})
    weights = {"system_documentation": 20, "governance_policies": 20,
               "access_control_records": 15, "audit_logs_evidence": 15,
               "risk_assessment": 10, "incident_history": 10,
               "agent_architecture": 5, "vendor_documentation": 5}
    completeness = {"Complete": 1.0, "Partial": 0.6, "Minimal": 0.25, "None": 0.0}
    return int(sum(weights[k] * completeness.get(ev.get(k, "None"), 0) for k in weights))


def _authority_risk_score(state: dict) -> int:
    a = state.get("authority_mapping", {})
    score = 0
    if _bool(a.get("payment_execution")):            score += 30
    if _bool(a.get("contract_or_vendor_authority")): score += 25
    if _bool(a.get("system_modification_authority")):score += 20
    if _bool(a.get("transaction_initiation")):       score += 15
    if _bool(a.get("approval")):                     score += 10
    return min(100, score)


def _exposure_risk_score(state: dict) -> int:
    exp = state.get("financial_exposure", {})
    score = 0
    score += {"Under $10K": 0, "$10K–$100K": 10, "$100K–$1M": 25,
              "$1M–$10M": 40, "Over $10M": 55,
              "Not applicable": 0, "Unknown": 15,
              }.get(exp.get("monthly_transaction_volume", ""), 0)
    score += {"Under $1K": 0, "$1K–$10K": 5, "$10K–$100K": 15,
              "$100K–$1M": 25, "Over $1M": 35,
              "Not applicable": 0, "Unknown": 10,
              }.get(exp.get("max_single_action_exposure", ""), 0)
    if _bool(exp.get("money_movement")):                  score += 15
    if _bool(exp.get("legal_or_compliance_consequence")): score += 10
    if not _bool(exp.get("human_override")):              score += 15
    return min(100, score)


def _shield_risk_score(state: dict) -> int:
    sh = state.get("ecosystem_exposure", {})
    score = 0
    score += {"No third-party dependencies": 0,
              "Known vendors with strong governance": 5,
              "Known vendors with unknown governance": 20,
              "Unknown vendors or dependencies": 35,
              "Multiple unaudited dependencies": 45,
              }.get(sh.get("third_party_vendors", ""), 0)
    score += {"None": 0, "1–3, all audited": 5, "1–3, not all audited": 15,
              "4–10, all audited": 10, "4–10, not all audited": 25,
              "10+": 30, "Unknown": 35,
              }.get(sh.get("external_apis", ""), 0)
    if _bool(sh.get("payment_rails")):                        score += 20
    if _bool(sh.get("erp_crm_integrations")):                 score += 10
    if _bool(sh.get("cloud_dependencies")):                   score += 10
    if _bool(sh.get("critical_infrastructure_connection")):   score += 30
    score += {"No external content ingestion": 0,
              "Limited, with input validation": 5,
              "Moderate, partially mitigated": 15,
              "High, with known exposure": 30,
              "Unknown": 20,
              }.get(sh.get("adversarial_exposure", ""), 0)
    score += {"Public or non-sensitive": 0, "Internal business data": 5,
              "Confidential / proprietary": 10,
              "Regulated data (PII, PHI, PCI, financial records)": 20,
              "Multiple regulated data classes": 30,
              }.get(sh.get("data_sensitivity", ""), 0)
    return min(100, score)


def _monitor_score(state: dict) -> int:
    mr = state.get("monitoring_readiness", {})
    score = 0
    score += {"Comprehensive": 25, "Partial": 15, "Minimal": 5, "None": 0
              }.get(mr.get("telemetry", ""), 0)
    score += {"Comprehensive": 20, "Partial": 12, "Minimal": 4, "None": 0
              }.get(mr.get("governance_events", ""), 0)
    score += {"Active monitoring": 20, "Periodic review": 12, "Ad hoc": 4, "None": 0
              }.get(mr.get("drift_signals", ""), 0)
    score += {"Complete": 15, "Partial": 9, "Minimal": 3, "None": 0
              }.get(mr.get("runtime_logs", ""), 0)
    score += {"Complete and reviewed": 10, "Captured but infrequently reviewed": 6,
              "Partial": 3, "None": 0,
              }.get(mr.get("exception_logs", ""), 0)
    if _bool(mr.get("certificate_verification_readiness")): score += 5
    if _bool(mr.get("continuous_assurance_readiness")):     score += 5
    return min(100, score)


# ── PRIMARY RISK DETECTION ─────────────────────────────────────────────────────

def detect_primary_risks(state: dict) -> list[str]:
    risks = []
    auth = state.get("authority_mapping", {})
    exp  = state.get("financial_exposure", {})
    gc   = state.get("governance_controls", {})
    sh   = state.get("ecosystem_exposure", {})

    if _bool(auth.get("payment_execution")):
        risks.append("Payment execution authority — financial system integrity requires verified governance controls.")
    if _bool(auth.get("contract_or_vendor_authority")):
        risks.append("Contract or vendor decision authority — high legal and financial exposure.")
    if _bool(auth.get("system_modification_authority")):
        risks.append("System modification authority — lateral movement and cascading failure risk.")
    if not _bool(exp.get("human_override")):
        risks.append("No reliable human override — autonomous errors cannot be stopped in flight.")
    if gc.get("audit_logs") in ("Partial", "No", None, ""):
        risks.append("Incomplete or absent audit logs — forensic reconstruction of failures is not possible.")
    if not _bool(gc.get("fail_closed")):
        risks.append("System does not fail closed — errors may propagate rather than halt.")
    if exp.get("monthly_transaction_volume") in ("$1M–$10M", "Over $10M"):
        risks.append("High monthly transaction volume amplifies the impact of any autonomous system failure.")
    if sh.get("data_sensitivity") in (
        "Regulated data (PII, PHI, PCI, financial records)", "Multiple regulated data classes"
    ):
        risks.append("Regulated data exposure — breach or mishandling triggers mandatory reporting obligations.")
    if _bool(sh.get("critical_infrastructure_connection")):
        risks.append("Critical infrastructure connection — failure impact extends beyond organizational boundaries.")
    if _bool(sh.get("payment_rails")):
        risks.append("Direct payment rail access — financial system integrity at risk.")
    if sh.get("third_party_vendors") in ("Unknown vendors or dependencies", "Multiple unaudited dependencies"):
        risks.append("Unaudited third-party dependencies — supply chain trust posture is unknown.")

    return risks


# ── VERDICT GENERATION ─────────────────────────────────────────────────────────

def generate_verdict(state: dict) -> dict:
    gov_score      = _governance_score(state)
    evidence_score = _evidence_score(state)
    authority_risk = _authority_risk_score(state)
    exposure_risk  = _exposure_risk_score(state)
    shield_risk    = _shield_risk_score(state)
    monitor_score  = _monitor_score(state)
    risks          = detect_primary_risks(state)
    sh             = state.get("ecosystem_exposure", {})

    # Governance readiness band
    if gov_score >= 75:   governance_readiness = "Strong"
    elif gov_score >= 50: governance_readiness = "Moderate"
    elif gov_score >= 25: governance_readiness = "Weak"
    else:                 governance_readiness = "Critical Gap"

    # Shield escalation trigger
    shield_required = (
        shield_risk >= 60
        or _bool(sh.get("critical_infrastructure_connection"))
        or (_bool(sh.get("payment_rails")) and authority_risk >= 30)
    )

    # Deployment verdict
    if shield_required and (authority_risk >= 50 or exposure_risk >= 50):
        deployment_verdict = "High Risk — Shield Review Required"
    elif gov_score >= 60 and evidence_score >= 50 and authority_risk < 50 and exposure_risk < 50:
        deployment_verdict = "Ready for ATC Review"
    elif gov_score >= 35 and evidence_score >= 30:
        deployment_verdict = "Conditionally Ready"
    else:
        deployment_verdict = "Not Ready"

    # ATC eligibility
    atc_map = {
        "High Risk — Shield Review Required": "Requires Shield review before ATC assessment",
        "Ready for ATC Review":               "Eligible for paid ATC system review",
        "Conditionally Ready":                "Potentially eligible after remediation",
        "Not Ready":                          "Not currently eligible",
    }
    atc_eligibility = atc_map[deployment_verdict]

    # Monitor eligibility — continuous assurance requires a valid ATC
    if deployment_verdict == "Ready for ATC Review":
        monitor_eligibility = "Eligible after valid ATC issuance"
    elif deployment_verdict == "Conditionally Ready":
        monitor_eligibility = "Not eligible until ATC is active"
    else:
        monitor_eligibility = "Not eligible — a valid Agentic Trust Certificate is required before activating Treasurety Monitor"

    # Required evidence gaps
    ev = state.get("evidence_readiness", {})
    evidence_labels = {
        "system_documentation":  "Complete system architecture and operational documentation",
        "governance_policies":   "Formal governance policies covering authority limits and escalation",
        "access_control_records":"Current access control configurations and permission records",
        "audit_logs_evidence":   "Complete audit logs sufficient for independent system review",
        "risk_assessment":       "Formal risk assessment for this system",
        "incident_history":      "Documented incident history including near-misses",
        "agent_architecture":    "Agent architecture and decision logic documentation",
        "vendor_documentation":  "Vendor and dependency documentation including third-party AI components",
    }
    required_evidence = [
        label for key, label in evidence_labels.items()
        if ev.get(key) in ("Partial", "Minimal", "None", None, "")
    ]

    # Recommended next step
    if deployment_verdict == "High Risk — Shield Review Required":
        next_step = (
            "Escalate to Treasurety Shield for ecosystem and threat exposure review "
            "before proceeding to ATC assessment. The current risk profile — ecosystem exposure, "
            "authority scope, or critical infrastructure connection — exceeds ATC threshold."
        )
    elif deployment_verdict == "Ready for ATC Review":
        next_step = (
            "Proceed to paid ATC system review. "
            "Treasurety Assess will conduct a structured diagnostic of the system, "
            "governance controls, and evidence package. "
            "Upon successful review, an Agentic Trust Certificate will be issued."
        )
    elif deployment_verdict == "Conditionally Ready":
        if governance_readiness in ("Weak", "Critical Gap"):
            gap_summary = "; ".join(r.split("—")[0].strip() for r in risks[:3])
            next_step = (
                f"Strengthen governance controls before ATC assessment. "
                f"Priority gaps: {gap_summary}. "
                "Engage Treasurety Govern to define authority boundaries, approval workflows, "
                "and audit infrastructure. Return for reassessment once remediation is complete."
            )
        else:
            next_step = (
                "Complete the evidence package and address identified gaps. "
                "A deeper Treasurety Assess diagnostic is recommended to validate "
                "governance readiness before ATC system review."
            )
    else:
        next_step = (
            "This system is not ready for ATC assessment. "
            "Foundational governance controls must be established before deployment authorization "
            "can proceed. Engage Treasurety Govern to define authority boundaries, "
            "approval workflows, and audit infrastructure."
        )

    return {
        "deployment_verdict":    deployment_verdict,
        "governance_readiness":  governance_readiness,
        "atc_eligibility":       atc_eligibility,
        "monitor_eligibility":   monitor_eligibility,
        "shield_review_required": shield_required,
        "primary_risks":         risks,
        "required_evidence":     required_evidence,
        "recommended_next_step": next_step,
        "_scores": {
            "governance":      gov_score,
            "evidence":        evidence_score,
            "authority_risk":  authority_risk,
            "exposure_risk":   exposure_risk,
            "shield_risk":     shield_risk,
            "monitor_readiness": monitor_score,
        },
    }


# ── EPC STATE OBJECT ───────────────────────────────────────────────────────────

def build_epc_object(session_id: str, state: dict, verdict: dict) -> dict:
    def b(v): return _bool(v)
    si = state.get("system_identity",    {})
    sc = state.get("agentic_scope",      {})
    au = state.get("authority_mapping",  {})
    fe = state.get("financial_exposure", {})
    gc = state.get("governance_controls",{})
    ev = state.get("evidence_readiness", {})
    sh = state.get("ecosystem_exposure", {})
    mr = state.get("monitoring_readiness",{})

    return {
        "gate_session_id":  session_id,
        "assessment_date":  datetime.utcnow().strftime("%Y-%m-%d"),
        "organization":     si.get("organization", "—"),
        "system": {
            "name":               si.get("system_name", "—"),
            "type":               si.get("system_type", "—"),
            "business_function":  si.get("business_function", "—"),
            "deployment_status":  si.get("deployment_status", "—"),
            "industry":           si.get("industry", "—"),
        },
        "agentic_scope": {
            "agent_count":            sc.get("agent_count", "—"),
            "workflow_count":          sc.get("workflow_count", "—"),
            "autonomy_level":          sc.get("autonomy_level", "—"),
            "external_system_access":  b(sc.get("external_system_access")),
            "real_world_outcomes":     b(sc.get("real_world_outcomes")),
        },
        "authority": {
            "read_only":                    b(au.get("read_only")),
            "recommendation":               b(au.get("recommendation")),
            "approval":                     b(au.get("approval")),
            "transaction_initiation":       b(au.get("transaction_initiation")),
            "payment_execution":            b(au.get("payment_execution")),
            "contract_or_vendor_authority": b(au.get("contract_or_vendor_authority")),
            "system_modification_authority":b(au.get("system_modification_authority")),
        },
        "exposure": {
            "monthly_transaction_volume":     fe.get("monthly_transaction_volume", "—"),
            "max_single_action_exposure":     fe.get("max_single_action_exposure", "—"),
            "money_movement":                 b(fe.get("money_movement")),
            "customer_vendor_obligations":    b(fe.get("customer_vendor_obligations")),
            "legal_or_compliance_consequence":b(fe.get("legal_or_compliance_consequence")),
            "human_override":                 b(fe.get("human_override")),
        },
        "governance_controls": {
            "human_approval":        gc.get("human_approval", "—"),
            "segregation_of_duties": gc.get("segregation_of_duties", "—"),
            "policy_constraints":    gc.get("policy_constraints", "—"),
            "audit_logs":            gc.get("audit_logs", "—"),
            "fail_closed":           b(gc.get("fail_closed")),
            "exception_handling":    b(gc.get("exception_handling")),
            "escalation_logic":      b(gc.get("escalation_logic")),
            "permission_boundaries": b(gc.get("permission_boundaries")),
            "rollback_controls":     gc.get("rollback_controls", "—"),
        },
        "evidence_readiness": {
            "system_documentation":  ev.get("system_documentation", "—"),
            "governance_policies":   ev.get("governance_policies", "—"),
            "access_control_records":ev.get("access_control_records", "—"),
            "audit_logs":            ev.get("audit_logs_evidence", "—"),
            "risk_assessment":       ev.get("risk_assessment", "—"),
            "incident_history":      ev.get("incident_history", "—"),
            "agent_architecture":    ev.get("agent_architecture", "—"),
            "vendor_documentation":  ev.get("vendor_documentation", "—"),
        },
        "shield_exposure": {
            "third_party_vendors":              sh.get("third_party_vendors", "—"),
            "external_apis":                    sh.get("external_apis", "—"),
            "payment_rails":                    b(sh.get("payment_rails")),
            "erp_crm_integrations":             b(sh.get("erp_crm_integrations")),
            "cloud_dependencies":               b(sh.get("cloud_dependencies")),
            "data_sensitivity":                 sh.get("data_sensitivity", "—"),
            "adversarial_exposure":             sh.get("adversarial_exposure", "—"),
            "critical_infrastructure_connection":b(sh.get("critical_infrastructure_connection")),
        },
        "monitor_readiness": {
            "telemetry":                         mr.get("telemetry", "—"),
            "governance_events":                 mr.get("governance_events", "—"),
            "drift_signals":                     mr.get("drift_signals", "—"),
            "runtime_logs":                      mr.get("runtime_logs", "—"),
            "exception_logs":                    mr.get("exception_logs", "—"),
            "certificate_verification_readiness":b(mr.get("certificate_verification_readiness")),
            "continuous_assurance_readiness":    b(mr.get("continuous_assurance_readiness")),
        },
        "verdict": {
            "deployment_verdict":    verdict["deployment_verdict"],
            "governance_readiness":  verdict["governance_readiness"],
            "atc_eligibility":       verdict["atc_eligibility"],
            "monitor_eligibility":   verdict["monitor_eligibility"],
            "shield_review_required":verdict["shield_review_required"],
            "primary_risks":         verdict["primary_risks"],
            "required_evidence":     verdict["required_evidence"],
            "recommended_next_step": verdict["recommended_next_step"],
        },
    }


# ── KEY FINDINGS GENERATOR ────────────────────────────────────────────────────

def generate_key_findings(state: dict, verdict: dict) -> list[dict]:
    """
    Produce exactly three executive-readable findings from the assessment state.
    Each finding has a dimension label and a one-sentence observation.
    """
    findings = []
    scores = verdict.get("_scores", {})
    au  = state.get("authority_mapping",  {})
    gc  = state.get("governance_controls", {})
    ev  = state.get("evidence_readiness", {})
    sh  = state.get("ecosystem_exposure", {})
    mr  = state.get("monitoring_readiness", {})
    fe  = state.get("financial_exposure", {})

    # ── Finding 1: Runtime Authority ─────────────────────────────────────────
    if _bool(au.get("payment_execution")) or _bool(au.get("contract_or_vendor_authority")) or _bool(au.get("system_modification_authority")):
        high_auth = [k.replace("_", " ").title() for k in
                     ("payment_execution", "contract_or_vendor_authority", "system_modification_authority")
                     if _bool(au.get(k))]
        gov_state = gc.get("human_approval", "No human approval checkpoints")
        if "No human" in gov_state or "Exception" in gov_state or "Sampled" in gov_state:
            ctrl = "lacks sufficient dual-control governance"
        elif "Post-action" in gov_state:
            ctrl = "relies on post-action review rather than pre-action approval"
        else:
            ctrl = "has approval checkpoints in place"
        findings.append({
            "label": "Runtime Authority",
            "finding": f"The system holds {', '.join(high_auth).lower()} authority and {ctrl}.",
        })
    elif _bool(au.get("transaction_initiation")) or _bool(au.get("approval")):
        findings.append({
            "label": "Runtime Authority",
            "finding": "The system has transaction or approval authority; governance controls determine whether that authority is sufficiently bounded.",
        })
    else:
        findings.append({
            "label": "Runtime Authority",
            "finding": "The system operates in a read-only or recommendation capacity, which limits direct authority risk.",
        })

    # ── Finding 2: Evidence Readiness ────────────────────────────────────────
    ev_score = scores.get("evidence", 0)
    gaps = [k for k in ("system_documentation", "governance_policies", "access_control_records",
                        "audit_logs_evidence", "risk_assessment")
            if ev.get(k) in ("Partial", "Minimal", "None", None, "")]
    if ev_score >= 70:
        findings.append({
            "label": "Evidence Readiness",
            "finding": "The evidence package is substantially complete and supports an independent system review.",
        })
    elif ev_score >= 40:
        gap_names = ", ".join(g.replace("_evidence", "").replace("_", " ") for g in gaps[:3])
        findings.append({
            "label": "Evidence Readiness",
            "finding": f"The organization has partial documentation but requires completion of {gap_names} before ATC system review.",
        })
    else:
        findings.append({
            "label": "Evidence Readiness",
            "finding": "The evidence package is insufficient for ATC system review; foundational documentation must be established before assessment can proceed.",
        })

    # ── Finding 3: Continuous Assurance ─────────────────────────────────────
    mon_score = scores.get("monitor_readiness", 0)
    atc_elig  = verdict.get("atc_eligibility", "")
    if "Eligible for paid" in atc_elig:
        if mon_score >= 60:
            findings.append({
                "label": "Continuous Assurance",
                "finding": "Monitoring infrastructure is in place; Treasurety Monitor can activate upon valid ATC issuance.",
            })
        else:
            findings.append({
                "label": "Continuous Assurance",
                "finding": "The system may be eligible for Treasurety Monitor only after a valid Agentic Trust Certificate is issued; monitoring infrastructure requires strengthening.",
            })
    elif "remediation" in atc_elig:
        findings.append({
            "label": "Continuous Assurance",
            "finding": "Continuous assurance is not available until governance gaps are resolved and a valid ATC is issued.",
        })
    else:
        findings.append({
            "label": "Continuous Assurance",
            "finding": "This system is not eligible for Treasurety Monitor. A valid Agentic Trust Certificate is required before continuous assurance can be activated.",
        })

    return findings[:3]


# ── ATC FEE CALCULATOR ─────────────────────────────────────────────────────────

ATC_TIERS = {
    "Standard":   {"label": "Standard Review",   "base": 4500,  "range": (4500,  7500)},
    "Advanced":   {"label": "Advanced Review",   "base": 8500,  "range": (8500,  14500)},
    "Enterprise": {"label": "Enterprise Review",  "base": 16500, "range": (16500, 28500)},
}

def calculate_atc_fee(state: dict, verdict: dict) -> dict:
    """
    Derive ATC system review tier and estimated fee from assessment data.
    Returns tier label, fee range, breakdown, and scope summary.
    """
    scores     = verdict.get("_scores", {})
    au         = state.get("authority_mapping",  {})
    sc         = state.get("agentic_scope",      {})
    ev         = state.get("evidence_readiness", {})
    si         = state.get("system_identity",    {})
    fe         = state.get("financial_exposure", {})

    # Base tier from authority risk + governance score
    auth_risk  = scores.get("authority_risk", 0)
    gov_score  = scores.get("governance", 0)
    shield_risk= scores.get("shield_risk", 0)

    if auth_risk >= 50 or shield_risk >= 50 or gov_score < 35:
        tier_key = "Enterprise"
    elif auth_risk >= 25 or gov_score < 60:
        tier_key = "Advanced"
    else:
        tier_key = "Standard"

    tier = ATC_TIERS[tier_key]
    base = tier["base"]
    lo, hi = tier["range"]

    # Surcharge components
    surcharges = []

    high_auth_flags = [k for k in ("payment_execution", "contract_or_vendor_authority",
                                   "system_modification_authority") if _bool(au.get(k))]
    if high_auth_flags:
        amt = len(high_auth_flags) * 1200
        surcharges.append({"item": f"High-risk authority scope ({len(high_auth_flags)} flag{'s' if len(high_auth_flags)>1 else ''})", "amount": amt})
        hi += amt

    agent_count = sc.get("agent_count", "1")
    if agent_count in ("21–100", "100+"):
        surcharges.append({"item": "Complex multi-agent architecture (21+ agents)", "amount": 2500})
        hi += 2500
    elif agent_count in ("6–20",):
        surcharges.append({"item": "Multi-agent architecture (6–20 agents)", "amount": 1000})
        hi += 1000

    ev_gaps = sum(1 for k in ("system_documentation", "governance_policies",
                               "access_control_records", "audit_logs_evidence",
                               "risk_assessment", "agent_architecture")
                  if ev.get(k) in ("Partial", "Minimal", "None", None, ""))
    if ev_gaps >= 5:
        surcharges.append({"item": f"Evidence remediation support ({ev_gaps} gaps)", "amount": 2000})
        hi += 2000
    elif ev_gaps >= 3:
        surcharges.append({"item": f"Evidence gap review ({ev_gaps} items)", "amount": 1000})
        hi += 1000

    industry = si.get("industry", "")
    if industry in ("Financial Services", "Healthcare", "Government", "Energy & Utilities"):
        surcharges.append({"item": f"Regulated industry premium ({industry})", "amount": 1500})
        hi += 1500

    status = si.get("deployment_status", "")
    if status in ("Production", "Scaling"):
        surcharges.append({"item": "Live production system — expedited assessment", "amount": 1000})
        hi += 1000

    total_vol = fe.get("monthly_transaction_volume", "")
    if total_vol in ("$1M–$10M", "Over $10M"):
        surcharges.append({"item": "High transaction volume — extended scope review", "amount": 1500})
        hi += 1500

    scope_items = []
    scope_items.append("Independent system review by Treasurety assessment team")
    scope_items.append("Governance controls verification against declared evidence")
    scope_items.append("Authority boundary and risk exposure analysis")
    scope_items.append("ATC issuance upon successful review")
    scope_items.append("Governance readiness report delivered post-review")
    if _bool(state.get("ecosystem_exposure", {}).get("payment_rails")) or \
       _bool(state.get("ecosystem_exposure", {}).get("critical_infrastructure_connection")):
        scope_items.append("Ecosystem and dependency risk assessment (Shield-aligned)")
    if ev_gaps >= 3:
        scope_items.append("Evidence gap advisory and documentation guidance")

    return {
        "tier":          tier_key,
        "tier_label":    tier["label"],
        "fee_range_low": lo,
        "fee_range_high":hi,
        "base_fee":      base,
        "surcharges":    surcharges,
        "scope_items":   scope_items,
        "ev_gaps":       ev_gaps,
        "high_auth_count": len(high_auth_flags),
    }


def build_atc_pricing_epc(session_id: str, state: dict, verdict: dict, fee_data: dict) -> dict:
    si = state.get("system_identity", {})
    return {
        "gate_session_id":  session_id,
        "assessment_date":  datetime.utcnow().strftime("%Y-%m-%d"),
        "organization":     si.get("organization", "—"),
        "system_name":      si.get("system_name", "—"),
        "industry":         si.get("industry", "—"),
        "deployment_status":si.get("deployment_status", "—"),
        "atc_review": {
            "tier":              fee_data["tier"],
            "tier_label":        fee_data["tier_label"],
            "fee_range":         f"${fee_data['fee_range_low']:,} – ${fee_data['fee_range_high']:,}",
            "base_fee":          f"${fee_data['base_fee']:,}",
            "surcharges":        fee_data["surcharges"],
            "scope":             fee_data["scope_items"],
        },
        "atc_eligibility":    verdict.get("atc_eligibility", "—"),
        "governance_readiness":verdict.get("governance_readiness", "—"),
        "evidence_gaps":       fee_data["ev_gaps"],
        "high_risk_authority_flags": fee_data["high_auth_count"],
        "shield_review_required": verdict.get("shield_review_required", False),
    }


# ── CONVERSATION STATE MACHINE ─────────────────────────────────────────────────

class GateConversation:
    """
    Drives the Treasurety Gate AI conversational assessment.
    Manages stage sequencing, answer parsing, EPC state collection,
    and verdict generation. No Streamlit imports — UI-agnostic.
    """

    def __init__(self):
        self.session_id    = f"GATE-AI-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        self.state         = {s: {} for s in STAGES[:-1]}
        self.current_stage = STAGES[0]
        self.current_q_idx = 0
        self.complete           = False   # True after free verdict delivered
        self.atc_path_active    = False   # True after user chooses to proceed to paid ATC
        self.awaiting_atc_decision = False  # True between free verdict and user response
        self.verdict_data       = None
        self.epc_object         = None
        self.atc_pricing_data   = None
        self.atc_pricing_epc    = None
        self.messages: list[dict] = []   # [{role, content}]

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self) -> str:
        """Return and store the opening message."""
        intro = (
            f"**Treasurety Gate — AI-Native Governance Intake**\n\n"
            f"Session ID: `{self.session_id}`\n\n"
            "This is a structured governance assessment for agentic system deployment authorization. "
            "At the conclusion, you will receive:\n\n"
            "- An executive deployment verdict\n"
            "- A governance readiness profile\n"
            "- Agentic Trust Certificate (ATC) eligibility status\n"
            "- Primary risks identified\n"
            "- Required evidence for system review\n"
            "- Recommended next step\n\n"
            "Eight stages. Answer precisely — the quality of your ATC assessment depends on what you declare here. "
            "Select numbered options or type your answer directly.\n\n"
            "---\n\n"
            f"**{STAGE_LABELS['system_identity']}**\n\n"
            f"{STAGE_INTROS['system_identity']}"
        )
        q = self._current_question()
        full = intro + ("\n\n---\n\n" + self._render_question(q) if q else "")
        self.messages.append({"role": "assistant", "content": full})
        return full

    def advance(self, user_input: str) -> str:
        """Process one user answer. Returns the next assistant message."""
        self.messages.append({"role": "user", "content": user_input})

        # Post-verdict: user is deciding whether to proceed to paid ATC
        if self.awaiting_atc_decision:
            raw = user_input.strip().lower()
            if any(w in raw for w in ("yes", "proceed", "1", "review", "atc", "continue")):
                return self._generate_atc_pricing_response()
            else:
                self.awaiting_atc_decision = False
                msg = (
                    "Understood. You can return to Treasurety Gate at any time to request an ATC system review.\n\n"
                    "**Remember:** Trust is temporal. The conditions assessed today will change. "
                    "An Agentic Trust Certificate should be obtained before expanding deployment scope.\n\n"
                    "*Treasurety Gate is the front door. Treasurety Govern is the engine.*"
                )
                self.messages.append({"role": "assistant", "content": msg})
                return msg

        q = self._current_question()
        if not q:
            return self._finish()

        answer = self._parse(q, user_input.strip())
        self.state[self.current_stage][q["key"]] = answer

        flags = []
        if q.get("risk_flag") and _bool(answer):
            flags.append(
                f"> **Authority risk flagged:** {q['text'].rstrip('?')} "
                "is a high-risk authority class and will be weighted in ATC eligibility."
            )

        self.current_q_idx += 1

        if self.current_q_idx >= len(self._stage_questions()):
            response = self._next_stage(flags)
        else:
            parts = flags + ["", self._render_question(self._current_question())]
            response = "\n".join(parts)
            self.messages.append({"role": "assistant", "content": response})

        return response

    def get_epc_json(self) -> str:
        if self.epc_object:
            return json.dumps(self.epc_object, indent=2)
        return "{}"

    def progress(self) -> dict:
        idx      = STAGES.index(self.current_stage)
        total_q  = sum(len(QUESTIONS.get(s, [])) for s in STAGES[:-1])
        done_q   = sum(len(QUESTIONS.get(s, [])) for s in STAGES[:idx]) + self.current_q_idx
        return {
            "stage":          self.current_stage,
            "stage_label":    STAGE_LABELS.get(self.current_stage, self.current_stage),
            "stage_number":   idx + 1,
            "total_stages":   len(STAGES) - 1,
            "questions_done": done_q,
            "total_questions":total_q,
            "pct":            int(done_q / max(total_q, 1) * 100),
        }

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _stage_questions(self) -> list:
        return QUESTIONS.get(self.current_stage, [])

    def _current_question(self) -> dict | None:
        qs = self._stage_questions()
        return qs[self.current_q_idx] if self.current_q_idx < len(qs) else None

    def _render_question(self, q: dict) -> str:
        lines = [f"**{q['text']}**"]
        if q.get("hint"):
            lines.append(f"*{q['hint']}*")
        if q["type"] == "choice":
            lines.append("")
            lines += [f"{i+1}. {o}" for i, o in enumerate(q["options"])]
        elif q["type"] == "bool":
            lines.append("\n1. Yes\n2. No")
        return "\n".join(lines)

    def _parse(self, q: dict, raw: str) -> Any:
        if q["type"] == "bool":
            return raw.lower() in ("1", "yes", "y", "true")
        if q["type"] == "choice":
            opts = q["options"]
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(opts):
                    return opts[idx]
            raw_l = raw.lower()
            for opt in opts:
                if raw_l in opt.lower():
                    return opt
            return raw
        return raw

    def _next_stage(self, flags: list) -> str:
        idx = STAGES.index(self.current_stage)
        if idx >= len(STAGES) - 2:
            return self._finish()

        self.current_stage = STAGES[idx + 1]
        self.current_q_idx = 0

        if self.current_stage == "verdict":
            return self._finish()

        label = STAGE_LABELS[self.current_stage]
        intro = STAGE_INTROS.get(self.current_stage, "")
        parts = flags + [f"---\n\n**{label}**\n\n{intro}"]
        q = self._current_question()
        if q:
            parts += ["", self._render_question(q)]
        response = "\n".join(parts)
        self.messages.append({"role": "assistant", "content": response})
        return response

    def _finish(self) -> str:
        """Deliver the free executive verdict — the conversion moment."""
        self.complete     = True
        self.verdict_data = generate_verdict(self.state)
        self.epc_object   = build_epc_object(self.session_id, self.state, self.verdict_data)
        v        = self.verdict_data
        findings = generate_key_findings(self.state, v)

        icons = {
            "Ready for ATC Review":               "✅",
            "Conditionally Ready":                "⚠️",
            "Not Ready":                          "🚫",
            "High Risk — Shield Review Required": "🔴",
        }

        findings_md = ""
        for i, f in enumerate(findings, 1):
            findings_md += f"\n**Finding {i} — {f['label']}**\n{f['finding']}\n"

        # ATC decision prompt — only if eligible
        atc_elig = v["atc_eligibility"]
        if "Eligible for paid" in atc_elig:
            atc_prompt = (
                "\n---\n\n"
                "**Would you like to proceed to paid ATC system review?**\n\n"
                "Type **yes** to receive your ATC system review estimate and next steps, "
                "or **no** to close this assessment."
            )
            self.awaiting_atc_decision = True
        elif "after remediation" in atc_elig:
            atc_prompt = (
                "\n---\n\n"
                "**Once remediation is complete, you may return to request ATC system review.**\n\n"
                "Type **yes** to see an indicative ATC system review estimate based on current scope, "
                "or **no** to close this assessment."
            )
            self.awaiting_atc_decision = True
        else:
            atc_prompt = (
                "\n\n*This system is not currently eligible for ATC assessment. "
                "Address the governance gaps identified above and return for reassessment.*"
            )

        output = f"""---

## Treasurety Gate — Deployment Verdict

**Session:** `{self.session_id}`
**Organization:** {self.epc_object.get('organization', '—')}
**System:** {self.epc_object['system'].get('name', '—')}

---

### {icons.get(v['deployment_verdict'], '—')} {v['deployment_verdict']}

---

### Three Key Findings
{findings_md}
---

### Recommended Next Step

{v['recommended_next_step']}

---

*Trust Is Temporal. This verdict reflects conditions at the time of assessment. Autonomous systems change, dependencies drift, and trust conditions degrade over time.*

*Treasurety Gate is the front door. Treasurety Govern is the engine.*{atc_prompt}"""

        self.messages.append({"role": "assistant", "content": output})
        return output

    def _generate_atc_pricing_response(self) -> str:
        """Generate the paid ATC path: pricing EPC + calculated review fee."""
        self.awaiting_atc_decision = False
        self.atc_path_active = True

        fee = calculate_atc_fee(self.state, self.verdict_data)
        self.atc_pricing_data = fee
        self.atc_pricing_epc  = build_atc_pricing_epc(
            self.session_id, self.state, self.verdict_data, fee
        )

        surcharge_lines = ""
        for s in fee["surcharges"]:
            surcharge_lines += f"  - {s['item']}: +${s['amount']:,}\n"
        if not surcharge_lines:
            surcharge_lines = "  - No surcharges applicable\n"

        scope_lines = "\n".join(f"- {item}" for item in fee["scope_items"])

        output = f"""---

## ATC System Review — Estimate

**Session:** `{self.session_id}`
**System:** {self.atc_pricing_epc.get('system_name', '—')}
**Organization:** {self.atc_pricing_epc.get('organization', '—')}

---

### Review Tier
**{fee['tier_label']}**

### Estimated ATC System Review Fee
# ${fee['fee_range_low']:,} – ${fee['fee_range_high']:,}

---

### Fee Composition

**Base fee ({fee['tier_label']}):** ${fee['base_fee']:,}

**Scope adjustments:**
{surcharge_lines}
*Final fee confirmed at engagement. Range reflects minimum and maximum based on declared scope.*

---

### What This Review Covers

{scope_lines}

---

### ATC Eligibility
**{self.verdict_data['atc_eligibility']}**

### Monitor Eligibility After ATC
**{self.verdict_data['monitor_eligibility']}**

> *Continuous assurance requires a valid Agentic Trust Certificate. Systems require a valid ATC before activating Treasurety Monitor.*

---

### Next Step to Engage

To initiate the ATC system review, contact Treasurety with your session ID: `{self.session_id}`

Your EPC state record is complete and will be transmitted to the review team upon engagement.

*Trust Is Temporal. An Agentic Trust Certificate is a point-in-time authorization — not a permanent status. Treasurety Monitor provides continuous assurance after issuance.*"""

        self.messages.append({"role": "assistant", "content": output})
        return output

    def get_atc_pricing_json(self) -> str:
        if self.atc_pricing_epc:
            return json.dumps(self.atc_pricing_epc, indent=2)
        return "{}"
