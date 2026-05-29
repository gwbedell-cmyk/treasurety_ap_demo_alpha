"""
Treasurety Gate™ — Trust Evaluation Engine
Modular, rule-based evaluation for agentic system deployment authorization.
"""

import uuid
from datetime import datetime, timedelta


# ── INDUSTRY DIMENSION WEIGHTS ─────────────────────────────────────────────────
# Multipliers applied to each dimension score before composite calculation.
# Values > 1.0 make that industry more sensitive to that dimension.

INDUSTRY_WEIGHTS = {
    "Financial Services":         {"authority": 1.4, "oversight": 1.2, "consequence": 1.3, "ecosystem": 1.0, "governance": 1.3},
    "Healthcare":                 {"authority": 1.2, "oversight": 1.4, "consequence": 1.5, "ecosystem": 1.0, "governance": 1.2},
    "Manufacturing":              {"authority": 1.0, "oversight": 1.2, "consequence": 1.3, "ecosystem": 0.9, "governance": 1.1},
    "Supply Chain & Logistics":   {"authority": 1.1, "oversight": 1.0, "consequence": 1.1, "ecosystem": 1.2, "governance": 1.0},
    "Insurance":                  {"authority": 1.2, "oversight": 1.2, "consequence": 1.3, "ecosystem": 1.0, "governance": 1.3},
    "Energy & Utilities":         {"authority": 1.3, "oversight": 1.3, "consequence": 1.5, "ecosystem": 1.0, "governance": 1.2},
    "Government":                 {"authority": 1.2, "oversight": 1.3, "consequence": 1.3, "ecosystem": 1.0, "governance": 1.4},
    "Cybersecurity":              {"authority": 1.5, "oversight": 1.2, "consequence": 1.2, "ecosystem": 1.1, "governance": 1.1},
    "Enterprise Operations":      {"authority": 1.0, "oversight": 1.0, "consequence": 1.0, "ecosystem": 1.0, "governance": 1.0},
    "AI Infrastructure":          {"authority": 1.3, "oversight": 1.1, "consequence": 1.1, "ecosystem": 1.2, "governance": 1.0},
    "Multi-Agent Orchestration":  {"authority": 1.4, "oversight": 1.2, "consequence": 1.0, "ecosystem": 1.3, "governance": 1.1},
    "Other":                      {"authority": 1.0, "oversight": 1.0, "consequence": 1.0, "ecosystem": 1.0, "governance": 1.0},
}

DIMENSION_BASE_WEIGHTS = {
    "authority":   0.25,
    "oversight":   0.25,
    "consequence": 0.20,
    "ecosystem":   0.15,
    "governance":  0.15,
}


# ── AUTHORITY EVALUATOR ────────────────────────────────────────────────────────

def evaluate_authority(intake: dict) -> int:
    score = 0

    # Action capability tier
    if intake.get("action_execution"):      score += 45
    elif intake.get("action_write"):        score += 25
    elif intake.get("action_recommend"):    score += 10
    else:                                   score += 5   # read-only

    # High-consequence authority types
    if intake.get("financial_authority"):   score += 15
    if intake.get("access_changes"):        score += 12
    if intake.get("clinical_workflows"):    score += 15
    if intake.get("legal_workflows"):       score += 12
    if intake.get("infra_changes"):         score += 15
    if intake.get("security_actions"):      score += 13

    # Boundary controls (absence increases score)
    if not intake.get("authority_limits_enforced"): score += 20
    if intake.get("authority_can_expand"):           score += 15
    if intake.get("can_create_subagents"):           score += 10

    return min(100, score)


# ── OVERSIGHT EVALUATOR ────────────────────────────────────────────────────────

def evaluate_oversight(intake: dict) -> int:
    approval = intake.get("approval_model", "None")
    base = {
        "Pre-action approval":   5,
        "Post-action review":    15,
        "Sampled review":        25,
        "Exception-based":       35,
        "None":                  50,
    }.get(approval, 35)

    score = base
    if not intake.get("kill_switch"):           score += 20
    if not intake.get("fallback_mode"):         score += 15
    if not intake.get("escalation_defined"):    score += 15
    if not intake.get("reviewers_trained"):     score += 10
    if intake.get("reviewer_overload"):         score += 8

    return min(100, score)


# ── CONSEQUENCE EVALUATOR ──────────────────────────────────────────────────────

def evaluate_consequence(intake: dict) -> int:
    fin = {
        "None":     0,
        "Low":      10,
        "Medium":   30,
        "High":     55,
        "Critical": 80,
    }.get(intake.get("financial_exposure", "None"), 0)

    score = fin
    if intake.get("safety_impact"):             score += 25
    if intake.get("legal_rights_impact"):       score += 20
    if intake.get("infrastructure_disruption"): score += 20
    if intake.get("sensitive_data_exposure"):   score += 15
    if intake.get("regulatory_reporting"):      score += 10
    if intake.get("reputational_damage"):       score += 8

    return min(100, score)


# ── ECOSYSTEM EVALUATOR ────────────────────────────────────────────────────────

def evaluate_ecosystem(intake: dict) -> int:
    score = 0

    critical_systems = intake.get("connected_systems", [])
    system_weights = {
        "Banking / Payments":       20,
        "EHR / Clinical Systems":   20,
        "IAM / Identity":           15,
        "ERP":                      12,
        "CRM":                      8,
        "DevOps / CI/CD":           10,
        "Cloud Infrastructure":     15,
        "Supply Chain":             10,
        "Customer Communications":  10,
        "Procurement":              8,
    }
    for sys in critical_systems:
        score += system_weights.get(sys, 8)

    if intake.get("third_party_tools"):        score += 10
    if intake.get("external_content"):         score += 15
    if intake.get("plugin_connector_actions"): score += 10
    if intake.get("regulated_data_access"):    score += 15

    return min(100, score)


# ── GOVERNANCE MATURITY EVALUATOR ──────────────────────────────────────────────

def evaluate_governance(intake: dict) -> int:
    """Returns 0-100 where higher = less mature governance."""
    score = 0

    # Absence of controls drives score up
    if not intake.get("audit_logging"):         score += 30
    if not intake.get("kill_switch"):           score += 20
    if not intake.get("escalation_defined"):    score += 20
    if not intake.get("fallback_mode"):         score += 15
    if intake.get("system_origin") == "Vendor-provided":
        score += 15  # less visibility into vendor internals

    return min(100, score)


def governance_maturity_level(gov_score: int) -> int:
    """Map governance score to 0-4 maturity level."""
    if gov_score >= 80: return 0   # Uncontrolled
    if gov_score >= 60: return 1   # Documented but not enforced
    if gov_score >= 40: return 2   # Enforced baseline
    if gov_score >= 20: return 3   # Operationally governed
    return 4                       # Continuously assured


# ── CRITICAL BLOCKER DETECTION ─────────────────────────────────────────────────

def detect_critical_blockers(intake: dict, scores: dict) -> list[str]:
    blockers = []

    # 1. Execution with zero oversight
    if (intake.get("action_execution") and
            intake.get("approval_model") == "None" and
            not intake.get("kill_switch")):
        blockers.append("Autonomous execution with no oversight and no kill switch.")

    # 2. Financial authority without approval gates
    if (intake.get("financial_authority") and
            intake.get("approval_model") == "None"):
        blockers.append("Financial execution authority with no human approval requirement.")

    # 3. High consequence + poor oversight
    if scores["consequence"] >= 65 and scores["oversight"] >= 60:
        blockers.append("High operational consequence severity with insufficient human oversight.")

    # 4. Unbounded authority expansion
    if intake.get("authority_can_expand") and not intake.get("authority_limits_enforced"):
        blockers.append("Authority can expand dynamically with no enforced limits — unbounded scope risk.")

    # 5. Clinical workflows without pre-action governance
    if (intake.get("clinical_workflows") and
            intake.get("approval_model") not in ["Pre-action approval"]):
        blockers.append("Clinical or patient-impacting workflows without pre-action human approval.")

    # 6. No kill switch with significant consequence
    if not intake.get("kill_switch") and scores["consequence"] >= 55:
        blockers.append("No kill switch or emergency stop for a system with material consequence exposure.")

    # 7. Completely uncontrolled governance
    if scores["governance"] >= 80:
        blockers.append("Governance posture is effectively uncontrolled — no audit, escalation, or intervention capability.")

    # 8. No audit trail with execution capability
    if not intake.get("audit_logging") and intake.get("action_execution"):
        blockers.append("Execution authority with no audit trail — forensic reconstruction of incidents is impossible.")

    return blockers


# ── VERDICT ENGINE ─────────────────────────────────────────────────────────────

def compute_verdict(scores: dict, blockers: list, industry: str) -> tuple[str, str, str]:
    """Returns (verdict_label, color_hex, rationale_text)."""
    weights = INDUSTRY_WEIGHTS.get(industry, INDUSTRY_WEIGHTS["Other"])

    weighted = sum(
        scores[dim] * weights[dim] * DIMENSION_BASE_WEIGHTS[dim]
        for dim in DIMENSION_BASE_WEIGHTS
    )
    # Normalize by weight sum
    weight_sum = sum(weights[dim] * DIMENSION_BASE_WEIGHTS[dim] for dim in DIMENSION_BASE_WEIGHTS)
    composite = int(weighted / weight_sum)

    if blockers:
        return (
            "DANGER — DO NOT DEPLOY",
            "#dc2626",
            "The autonomous system does not currently meet operational trust requirements for the declared scope. "
            "Gate identified critical control gaps that must be remediated before any production deployment. "
            "Deployment should be paused pending resolution of all identified blockers."
        )

    if composite < 28:
        return (
            "SAFE TO DEPLOY",
            "#16a34a",
            "The autonomous system appears operationally deployable under the declared scope. "
            "Authority boundaries, intervention pathways, and audit readiness appear sufficient for controlled deployment. "
            "Continuous monitoring is recommended as trust conditions may evolve after deployment."
        )

    if composite < 65:
        return (
            "SAFE WITH EXCEPTIONS",
            "#f59e0b",
            "The autonomous system may proceed only under limited deployment conditions. "
            "Gate identified control gaps that require remediation or compensating controls before full production scope. "
            "Deployment should remain scoped and monitored until all exceptions are resolved."
        )

    return (
        "DANGER — DO NOT DEPLOY",
        "#dc2626",
        "Operational trust capacity is insufficient for the declared deployment scope. "
        "The risk profile across authority, oversight, and consequence dimensions exceeds acceptable thresholds. "
        "Deployment should be paused pending governance remediation."
    )


# ── EXCEPTION GENERATOR ────────────────────────────────────────────────────────

def generate_exceptions(intake: dict, scores: dict) -> list[dict]:
    exceptions = []

    if scores["authority"] >= 60:
        exceptions.append({
            "dimension": "Authority Boundary Integrity",
            "severity": "CRITICAL",
            "finding": "Autonomous authority scope is broad. Explicit machine-enforced boundaries and delegation limits are required before production deployment.",
        })
    elif scores["authority"] >= 35:
        exceptions.append({
            "dimension": "Authority Boundary Integrity",
            "severity": "HIGH",
            "finding": "Authority scope requires documented constraints and approval gates before expanding to full production volume.",
        })

    if scores["oversight"] >= 60:
        exceptions.append({
            "dimension": "Human Intervention Capacity",
            "severity": "CRITICAL",
            "finding": "Human governance controls are inadequate. Kill switch, escalation pathway, and trained reviewers are required for production operation.",
        })
    elif scores["oversight"] >= 35:
        exceptions.append({
            "dimension": "Human Intervention Capacity",
            "severity": "HIGH",
            "finding": "Intervention readiness should be strengthened. Escalation paths and fallback modes must be operationally tested.",
        })

    if scores["consequence"] >= 55:
        exceptions.append({
            "dimension": "Consequence Severity",
            "severity": "HIGH",
            "finding": "Operational consequence exposure is material. Governance maturity and oversight controls must match the consequence profile.",
        })

    if scores["ecosystem"] >= 50:
        exceptions.append({
            "dimension": "Ecosystem Trust Exposure",
            "severity": "HIGH",
            "finding": "Connected-system blast radius is elevated. Third-party trust verification and API dependency scoping are required.",
        })
    elif scores["ecosystem"] >= 30:
        exceptions.append({
            "dimension": "Ecosystem Trust Exposure",
            "severity": "MODERATE",
            "finding": "External dependencies should be audited and trust boundaries formally defined before production.",
        })

    if scores["governance"] >= 60:
        exceptions.append({
            "dimension": "Governance Maturity",
            "severity": "CRITICAL",
            "finding": "Governance posture is insufficient. Audit trails, incident ownership, and policy versioning must be established.",
        })
    elif scores["governance"] >= 35:
        exceptions.append({
            "dimension": "Governance Maturity",
            "severity": "MODERATE",
            "finding": "Governance controls exist but require strengthening. Ensure audit completeness and incident response procedures are documented.",
        })

    if not exceptions:
        exceptions.append({
            "dimension": "Deployment Conditions",
            "severity": "LOW",
            "finding": "Operational trust controls appear sufficient. Activate Treasurety Monitor for continuous assurance post-deployment.",
        })

    return exceptions[:4]  # Top 4 only


# ── CERTIFICATE GENERATOR ──────────────────────────────────────────────────────

def generate_certificate(intake: dict, verdict: str, exceptions: list) -> dict:
    cert_id = f"TGC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    issued  = datetime.utcnow()
    expiry  = issued + timedelta(days=30)

    status = {
        "SAFE TO DEPLOY":        "Issued",
        "SAFE WITH EXCEPTIONS":  "Issued with Exceptions",
        "DANGER — DO NOT DEPLOY": "Withheld",
    }.get(verdict, "Under Review")

    return {
        "certificate_id":    cert_id,
        "issued_date":       issued.strftime("%Y-%m-%d"),
        "expiry_date":       expiry.strftime("%Y-%m-%d"),
        "industry":          intake.get("industry", "—"),
        "system_type":       intake.get("system_type", "—"),
        "system_name":       intake.get("system_name", "Assessed System"),
        "deployment_stage":  intake.get("deployment_stage", "—"),
        "verdict":           verdict,
        "certificate_status": status,
        "scope_summary":     _build_scope_summary(intake),
        "exceptions_count":  len([e for e in exceptions if e["severity"] in ("CRITICAL", "HIGH")]),
        "assessment_method": "Provisional Self-Assessment",
        "evidence_tier":     "Tier 1 — Self-Declared",
        "validity_days":     30,
    }


def _build_scope_summary(intake: dict) -> str:
    parts = []
    if intake.get("system_type"):
        parts.append(intake["system_type"])
    if intake.get("industry"):
        parts.append(f"operating in {intake['industry']}")
    if intake.get("deployment_stage"):
        parts.append(f"at {intake['deployment_stage'].lower()} stage")
    return " — ".join(parts) if parts else "Autonomous system deployment scope"


# ── MAIN EVALUATION ENTRY POINT ────────────────────────────────────────────────

def evaluate_system(intake: dict) -> dict:
    scores = {
        "authority":   evaluate_authority(intake),
        "oversight":   evaluate_oversight(intake),
        "consequence": evaluate_consequence(intake),
        "ecosystem":   evaluate_ecosystem(intake),
        "governance":  evaluate_governance(intake),
    }

    blockers   = detect_critical_blockers(intake, scores)
    verdict, color, rationale = compute_verdict(scores, blockers, intake.get("industry", "Other"))
    exceptions = generate_exceptions(intake, scores)
    certificate = generate_certificate(intake, verdict, exceptions)

    return {
        "scores":      scores,
        "blockers":    blockers,
        "verdict":     verdict,
        "color":       color,
        "rationale":   rationale,
        "exceptions":  exceptions,
        "certificate": certificate,
    }
