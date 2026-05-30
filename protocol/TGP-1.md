# Treasurety Gate Protocol v1
## TGP-1 — Formal Specification

**Status:** Draft  
**Version:** 1.0.0  
**Protocol Identifier:** TGP-1  
**Issued by:** Treasurety  
**Applies to:** All implementations of Treasurety Gate  

---

## Preamble

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt).

---

## 0. Purpose and Scope

TGP-1 defines the canonical decision protocol for Treasurety Gate — the customer-facing governance intake and authorization front door for the Treasurety platform. This specification governs how any conformant implementation MUST collect governance evidence, evaluate operational trust, render a deployment verdict, surface key findings, determine ATC eligibility, and price a system review engagement.

A conformant implementation of TGP-1 MAY take any interaction form: a structured web form, a conversational AI agent, a LinkedIn chat integration, an MCP server, a CLI tool, or any other interface. The protocol is interface-agnostic. The decision logic defined herein is authoritative and MUST NOT be altered by any individual implementation.

**This protocol does not govern:**
- The internal operation of Treasurety Govern (the runtime engine)
- The continuous monitoring logic of Treasurety Monitor
- The threat analysis methodology of Treasurety Shield
- Treasurety Assess diagnostic procedures beyond what is referenced here

### Authoritative Platform Architecture

```
Treasurety Gate      Customer-facing intake; governance front door; ATC entry point
Treasurety Govern    Core runtime governance engine; heart of the platform
Treasurety Assess    Pre-deployment diagnostic layer
Treasurety Monitor   Continuous assurance and drift monitoring
Treasurety Shield    Ecosystem and threat protection
```

> **Canonical framing:** Treasurety Gate is the front door. Treasurety Govern is the engine.

---

## 1. Core Philosophy

1.1 **Trust is temporal.** Governance readiness is a point-in-time condition, not a permanent state. Any verdict produced under this protocol reflects the system's governance posture at the moment of assessment. It MUST be treated as perishable.

1.2 **Continuous assurance requires a valid ATC.** An Agentic Trust Certificate (ATC) is the machine-readable record that continuous assurance tooling can act upon. Monitor eligibility is gated on ATC issuance.

1.3 **The protocol is the decision authority for Gate-layer evaluations.** Implementations MUST NOT invent governance logic. All scoring, verdict thresholds, finding generation, and eligibility rules are defined in this document. Reference implementations are derived from this specification; this specification governs all implementations, not the reverse.

1.4 **Free verdict first.** No pricing information SHALL be presented before the free deployment verdict has been delivered to the user. Implementations MUST follow the mandated output sequence defined in Section 6.

---

## 2. Protocol State Machine

### 2.1 States

| State | Description |
|---|---|
| `IDLE` | Protocol not yet initiated |
| `COLLECTING[n]` | Actively collecting evidence for Stage n (n = 1–8) |
| `EVALUATING` | All 8 stages complete; scoring in progress |
| `VERDICT_DELIVERED` | Free verdict, three findings, and recommended next step delivered |
| `ATC_DECISION_PENDING` | Awaiting explicit user consent to proceed to ATC pricing |
| `ATC_PRICING_DELIVERED` | ATC Pricing EPC artifact generated and delivered |
| `COMPLETE` | Conversation or session closed |

### 2.2 State Transitions

```
IDLE
  └─► COLLECTING[1]           on: session initiated

COLLECTING[n]
  └─► COLLECTING[n+1]         on: all required questions for Stage n answered (n < 8)
  └─► EVALUATING              on: Stage 8 complete

EVALUATING
  └─► VERDICT_DELIVERED       on: scoring and findings generation complete

VERDICT_DELIVERED
  ├─► ATC_DECISION_PENDING    if: atc_eligible = true
  └─► COMPLETE                if: atc_eligible = false

ATC_DECISION_PENDING
  ├─► ATC_PRICING_DELIVERED   on: user confirms "yes" to ATC pricing
  └─► COMPLETE                on: user declines or session ends

ATC_PRICING_DELIVERED
  └─► COMPLETE                on: delivery confirmed
```

### 2.3 Transition Rules

- Implementations MUST NOT skip stages.
- Implementations MAY collect Stage 1–8 data non-sequentially if the interaction modality (e.g., a web form) permits simultaneous field entry, provided all required fields are collected before `EVALUATING` is entered.
- Conversational implementations MUST present stages sequentially in the order defined in Section 3.
- Back-navigation to a prior stage MUST preserve previously collected state.
- A session MAY time out and return to `IDLE`; all intermediate state MUST be discarded on timeout.

---

## 3. Protocol Stages

The protocol defines eight evidence-collection stages. Each stage produces structured state fields consumed by the scoring engine defined in Section 5.

### Stage 1 — System Identity

**Purpose:** Establish the entity being assessed.

| Field | Type | Required | Notes |
|---|---|---|---|
| `system_name` | string | REQUIRED | Human-readable name |
| `industry` | enum | REQUIRED | See Section 3.1 |
| `deployment_stage` | enum | REQUIRED | Pilot / Limited Production / Full Production |
| `system_type` | enum | REQUIRED | See Section 3.2 |
| `system_origin` | enum | REQUIRED | In-house / Vendor-provided / Hybrid |

#### 3.1 Industry Enumeration

Financial Services, Healthcare, Manufacturing, Supply Chain & Logistics, Insurance, Energy & Utilities, Government, Cybersecurity, Enterprise Operations, AI Infrastructure, Multi-Agent Orchestration, Other

#### 3.2 System Type Enumeration

Autonomous Agent, Multi-Agent System, AI-Augmented Workflow, Robotic Process Automation, Conversational AI, Decision Support System, Other

### Stage 2 — Agentic Scope

**Purpose:** Characterize the operational boundaries and interaction surface of the system.

| Field | Type | Required | Notes |
|---|---|---|---|
| `operates_autonomously` | boolean | REQUIRED | True if system acts without per-action human approval |
| `human_in_loop` | boolean | REQUIRED | True if human reviews outputs before action |
| `multi_agent` | boolean | REQUIRED | True if system orchestrates or delegates to sub-agents |
| `can_create_subagents` | boolean | REQUIRED | True if system can spawn new agents at runtime |
| `scope_defined` | boolean | REQUIRED | True if explicit operational scope boundaries are documented |

### Stage 3 — Authority Mapping

**Purpose:** Quantify the real-world authority the system can exercise.

| Field | Type | Required | Notes |
|---|---|---|---|
| `action_execution` | boolean | REQUIRED | System can execute irreversible real-world actions |
| `action_write` | boolean | REQUIRED | System can write/modify records without execution |
| `action_recommend` | boolean | REQUIRED | System produces recommendations acted on by humans |
| `financial_authority` | boolean | REQUIRED | System can initiate or approve financial transactions |
| `access_changes` | boolean | REQUIRED | System can modify access control or identity |
| `clinical_workflows` | boolean | REQUIRED | System acts in clinical or patient-impacting workflows |
| `legal_workflows` | boolean | REQUIRED | System acts in legal or regulatory-filing workflows |
| `infra_changes` | boolean | REQUIRED | System can modify production infrastructure |
| `security_actions` | boolean | REQUIRED | System can take security-affecting actions |
| `authority_limits_enforced` | boolean | REQUIRED | Machine-enforced boundaries on authority scope exist |
| `authority_can_expand` | boolean | REQUIRED | Authority scope can expand dynamically at runtime |

### Stage 4 — Financial Exposure

**Purpose:** Characterize financial and economic consequence profile.

| Field | Type | Required | Notes |
|---|---|---|---|
| `financial_exposure` | enum | REQUIRED | None / Low / Medium / High / Critical |
| `payment_rails` | boolean | REQUIRED | System touches payment processing rails |
| `budget_authority` | string | OPTIONAL | Approximate transactional authority limit |
| `reputational_damage` | boolean | REQUIRED | Failure could cause material reputational harm |

#### Financial Exposure Scale

| Level | Indicative Threshold |
|---|---|
| None | No financial authority |
| Low | < $10,000 per transaction |
| Medium | $10,000 – $100,000 |
| High | $100,000 – $1,000,000 |
| Critical | > $1,000,000 or systemic market impact |

### Stage 5 — Governance Controls

**Purpose:** Assess operational governance and human intervention capacity.

| Field | Type | Required | Notes |
|---|---|---|---|
| `approval_model` | enum | REQUIRED | See Section 3.3 |
| `kill_switch` | boolean | REQUIRED | Emergency stop mechanism exists and is operational |
| `fallback_mode` | boolean | REQUIRED | Degraded-mode fallback exists if system fails |
| `escalation_defined` | boolean | REQUIRED | Escalation pathway to human decision-maker is documented |
| `audit_logging` | boolean | REQUIRED | Complete audit trail of system actions is maintained |
| `reviewers_trained` | boolean | REQUIRED | Assigned human reviewers are trained on intervention |
| `reviewer_overload` | boolean | REQUIRED | True if reviewers are capacity-constrained |
| `critical_infrastructure` | boolean | REQUIRED | System operates in or connects to critical infrastructure |

#### 3.3 Approval Model Enumeration (priority order)

| Value | Description |
|---|---|
| `pre_action` | Human approval required before each action |
| `post_action` | Human reviews completed actions |
| `sampled` | Random sample of actions reviewed |
| `exception` | Review triggered only on flagged exceptions |
| `none` | No human approval in the action loop |

### Stage 6 — Evidence Readiness

**Purpose:** Assess the quality and availability of governance evidence available for an ATC system review.

| Field | Type | Required | Notes |
|---|---|---|---|
| `policy_docs_exist` | boolean | REQUIRED | Written AI governance policy exists |
| `policy_current` | boolean | REQUIRED | Policy updated within the last 12 months |
| `incident_process` | boolean | REQUIRED | Documented incident response process for AI failures |
| `risk_register` | boolean | REQUIRED | AI risk register or equivalent is maintained |
| `prior_assessments` | boolean | REQUIRED | Prior third-party or internal assessments available |
| `audit_logs_available` | boolean | REQUIRED | Audit logs can be produced on request |
| `technical_docs` | boolean | REQUIRED | System architecture and integration documentation exists |
| `compliance_mapped` | boolean | REQUIRED | Regulatory or framework compliance requirements are mapped |

### Stage 7 — Ecosystem Exposure

**Purpose:** Characterize the blast radius of system failure or compromise through connected systems.

| Field | Type | Required | Notes |
|---|---|---|---|
| `connected_systems` | array[enum] | REQUIRED | See Section 3.4; MAY be empty |
| `third_party_tools` | boolean | REQUIRED | System invokes third-party tools or APIs |
| `external_content` | boolean | REQUIRED | System processes external/untrusted content |
| `plugin_connector_actions` | boolean | REQUIRED | System can take actions through plugins or connectors |
| `regulated_data_access` | boolean | REQUIRED | System accesses regulated data (PII, PHI, financial) |
| `sensitive_data_exposure` | boolean | REQUIRED | Data breach from this system would be material |

#### 3.4 Connected Systems Enumeration

Banking / Payments, EHR / Clinical Systems, IAM / Identity, ERP, CRM, DevOps / CI/CD, Cloud Infrastructure, Supply Chain, Customer Communications, Procurement

### Stage 8 — Monitoring Readiness

**Purpose:** Determine readiness for and eligibility for Treasurety Monitor continuous assurance.

| Field | Type | Required | Notes |
|---|---|---|---|
| `has_monitoring` | boolean | REQUIRED | Any form of AI system monitoring currently in place |
| `drift_detection` | boolean | REQUIRED | Automated detection of behavioral drift exists |
| `monitoring_team` | boolean | REQUIRED | Named team owns AI monitoring function |
| `incident_response_tested` | boolean | REQUIRED | Incident response process has been exercised |
| `sla_defined` | boolean | REQUIRED | SLAs for AI system performance are defined |
| `regulatory_reporting` | boolean | REQUIRED | Regulatory reporting obligations exist |
| `safety_impact` | boolean | REQUIRED | System failure could cause physical safety harm |
| `infrastructure_disruption` | boolean | REQUIRED | System failure could disrupt infrastructure |
| `legal_rights_impact` | boolean | REQUIRED | System could impact individual legal rights |

---

## 4. EPC Schema

The Entity-Purpose-Context (EPC) object is the canonical machine-readable record produced at the conclusion of the protocol. All conformant implementations MUST produce a valid EPC object.

### 4.1 EPC JSON Schema

```json
{
  "protocol_version": "TGP-1",
  "session_id": "GATE-AI-{YYYYMMDD}-{hex8}",
  "generated_at": "{ISO 8601 UTC}",
  "entity": {
    "system_name": "string",
    "system_type": "string",
    "industry": "string",
    "deployment_stage": "string",
    "system_origin": "string"
  },
  "purpose": {
    "operates_autonomously": "boolean",
    "human_in_loop": "boolean",
    "multi_agent": "boolean",
    "can_create_subagents": "boolean",
    "scope_defined": "boolean",
    "action_execution": "boolean",
    "action_write": "boolean",
    "action_recommend": "boolean",
    "financial_authority": "boolean",
    "access_changes": "boolean",
    "clinical_workflows": "boolean",
    "legal_workflows": "boolean",
    "infra_changes": "boolean",
    "security_actions": "boolean",
    "authority_limits_enforced": "boolean",
    "authority_can_expand": "boolean"
  },
  "context": {
    "financial_exposure": "string",
    "payment_rails": "boolean",
    "reputational_damage": "boolean",
    "approval_model": "string",
    "kill_switch": "boolean",
    "fallback_mode": "boolean",
    "escalation_defined": "boolean",
    "audit_logging": "boolean",
    "reviewers_trained": "boolean",
    "reviewer_overload": "boolean",
    "critical_infrastructure": "boolean",
    "connected_systems": ["string"],
    "third_party_tools": "boolean",
    "external_content": "boolean",
    "plugin_connector_actions": "boolean",
    "regulated_data_access": "boolean",
    "sensitive_data_exposure": "boolean",
    "safety_impact": "boolean",
    "infrastructure_disruption": "boolean",
    "legal_rights_impact": "boolean",
    "regulatory_reporting": "boolean",
    "policy_docs_exist": "boolean",
    "policy_current": "boolean",
    "incident_process": "boolean",
    "risk_register": "boolean",
    "prior_assessments": "boolean",
    "audit_logs_available": "boolean",
    "technical_docs": "boolean",
    "compliance_mapped": "boolean",
    "has_monitoring": "boolean",
    "drift_detection": "boolean",
    "monitoring_team": "boolean",
    "incident_response_tested": "boolean",
    "sla_defined": "boolean"
  },
  "scores": {
    "ARS": "integer 0–100",
    "GMS": "integer 0–100",
    "ERS": "integer 0–100",
    "EXS": "integer 0–100",
    "SRS": "integer 0–100",
    "MRS": "integer 0–100"
  },
  "verdict": {
    "deployment_verdict": "string",
    "governance_readiness": "string",
    "atc_eligible": "boolean",
    "monitor_eligible": "boolean",
    "shield_review_required": "boolean",
    "recommended_next_step": "string",
    "primary_risks": ["string"]
  },
  "findings": [
    {
      "index": "integer 1–3",
      "title": "string",
      "severity": "CRITICAL | HIGH | MODERATE | LOW",
      "body": "string"
    }
  ],
  "evidence_tier": "Tier 1 — Self-Declared",
  "validity_days": 30
}
```

### 4.2 EPC Field Constraints

- `protocol_version` MUST be the string `"TGP-1"` for all v1 artifacts.
- `session_id` MUST be globally unique within a deployment.
- `generated_at` MUST be ISO 8601 UTC.
- `scores` fields MUST be integers in [0, 100].
- `findings` MUST contain exactly three entries.
- `evidence_tier` MUST be `"Tier 1 — Self-Declared"` for any self-reported assessment.
- `validity_days` MUST be `30`.

---

## 5. Scoring Engine

The scoring engine maps collected state fields to six numeric risk scores. Higher scores indicate greater risk. All scores MUST be integers clamped to [0, 100].

### 5.1 Authority Risk Score (ARS)

Measures the real-world authority scope the system can exercise.

**Action Capability Base (select one, highest applicable):**

| Condition | Points |
|---|---|
| `action_execution = true` | 45 |
| `action_write = true` | 25 |
| `action_recommend = true` | 10 |
| Read-only (none of the above) | 5 |

**Authority Type Addends:**

| Condition | Points |
|---|---|
| `financial_authority = true` | +15 |
| `access_changes = true` | +12 |
| `clinical_workflows = true` | +15 |
| `legal_workflows = true` | +12 |
| `infra_changes = true` | +15 |
| `security_actions = true` | +13 |

**Boundary Control Addends:**

| Condition | Points |
|---|---|
| `authority_limits_enforced = false` | +20 |
| `authority_can_expand = true` | +15 |
| `can_create_subagents = true` | +10 |

**ARS = min(100, sum of all applicable points)**

### 5.2 Governance Maturity Score (GMS)

Measures gaps in operational governance controls. Higher = less mature.

| Condition | Points |
|---|---|
| `audit_logging = false` | +30 |
| `kill_switch = false` | +20 |
| `escalation_defined = false` | +20 |
| `fallback_mode = false` | +15 |
| `system_origin = "Vendor-provided"` | +15 |

**GMS = min(100, sum of all applicable points)**

### 5.3 Evidence Readiness Score (ERS)

Measures the completeness of governance documentation available for a system review.

| Condition | Points |
|---|---|
| `policy_docs_exist = false` | +25 |
| `policy_current = false` | +15 |
| `incident_process = false` | +20 |
| `risk_register = false` | +15 |
| `prior_assessments = false` | +10 |
| `audit_logs_available = false` | +20 |
| `technical_docs = false` | +10 |
| `compliance_mapped = false` | +10 |

**ERS = min(100, sum of all applicable points)**

Note: ERS does not affect the deployment verdict. It governs ATC tier classification and evidence gap findings only.

### 5.4 Exposure Risk Score (EXS)

Measures the blast radius and consequence severity of system failure or compromise.

**Financial Exposure Base:**

| `financial_exposure` | Points |
|---|---|
| None | 0 |
| Low | 10 |
| Medium | 30 |
| High | 55 |
| Critical | 80 |

**Consequence Addends:**

| Condition | Points |
|---|---|
| `safety_impact = true` | +25 |
| `legal_rights_impact = true` | +20 |
| `infrastructure_disruption = true` | +20 |
| `sensitive_data_exposure = true` | +15 |
| `regulatory_reporting = true` | +10 |
| `reputational_damage = true` | +8 |

**Ecosystem Addends:**

| Connected System | Points |
|---|---|
| Banking / Payments | +20 |
| EHR / Clinical Systems | +20 |
| IAM / Identity | +15 |
| ERP | +12 |
| Cloud Infrastructure | +15 |
| DevOps / CI/CD | +10 |
| Supply Chain | +10 |
| CRM | +8 |
| Customer Communications | +10 |
| Procurement | +8 |
| Any other system | +8 |

Additional:

| Condition | Points |
|---|---|
| `third_party_tools = true` | +10 |
| `external_content = true` | +15 |
| `plugin_connector_actions = true` | +10 |
| `regulated_data_access = true` | +15 |

**EXS = min(100, sum of all applicable points)**

### 5.5 Shield Risk Score (SRS)

Measures conditions that elevate ecosystem threat and protection complexity.

| Condition | Points |
|---|---|
| `external_content = true` | +25 |
| `plugin_connector_actions = true` | +20 |
| `third_party_tools = true` | +15 |
| `can_create_subagents = true` | +15 |
| `multi_agent = true` | +10 |
| `regulated_data_access = true` | +15 |

**SRS = min(100, sum of all applicable points)**

### 5.6 Monitor Readiness Score (MRS)

Measures gaps in continuous monitoring capability. Higher = less ready.

| Condition | Points |
|---|---|
| `has_monitoring = false` | +30 |
| `drift_detection = false` | +20 |
| `monitoring_team = false` | +20 |
| `incident_response_tested = false` | +15 |
| `sla_defined = false` | +15 |

**MRS = min(100, sum of all applicable points)**

### 5.7 Oversight Score (ORS)

Used in critical blocker detection. Derived from approval model and oversight controls.

**Approval Model Base:**

| `approval_model` | Points |
|---|---|
| `pre_action` | 5 |
| `post_action` | 15 |
| `sampled` | 25 |
| `exception` | 35 |
| `none` | 50 |

**Oversight Gap Addends:**

| Condition | Points |
|---|---|
| `kill_switch = false` | +20 |
| `fallback_mode = false` | +15 |
| `escalation_defined = false` | +15 |
| `reviewers_trained = false` | +10 |
| `reviewer_overload = true` | +8 |

**ORS = min(100, sum of all applicable points)**

---

## 6. Decision Logic

### 6.1 Critical Blocker Detection

Critical blockers are hard-stop conditions. If any blocker is present, the verdict MUST be `DANGER — DO NOT DEPLOY` regardless of composite score.

Blockers are evaluated in order. Multiple blockers MAY be present simultaneously.

| ID | Condition | Blocker Message |
|---|---|---|
| BLK-01 | `action_execution = true` AND `approval_model = none` AND `kill_switch = false` | Autonomous execution with no oversight and no kill switch. |
| BLK-02 | `financial_authority = true` AND `approval_model = none` | Financial execution authority with no human approval requirement. |
| BLK-03 | EXS ≥ 65 AND ORS ≥ 60 | High operational consequence severity with insufficient human oversight. |
| BLK-04 | `authority_can_expand = true` AND `authority_limits_enforced = false` | Authority can expand dynamically with no enforced limits — unbounded scope risk. |
| BLK-05 | `clinical_workflows = true` AND `approval_model ≠ pre_action` | Clinical or patient-impacting workflows without pre-action human approval. |
| BLK-06 | `kill_switch = false` AND EXS ≥ 55 | No kill switch or emergency stop for a system with material consequence exposure. |
| BLK-07 | GMS ≥ 80 | Governance posture is effectively uncontrolled — no audit, escalation, or intervention capability. |
| BLK-08 | `audit_logging = false` AND `action_execution = true` | Execution authority with no audit trail — forensic reconstruction of incidents is impossible. |

### 6.2 Composite Score Calculation

If no critical blockers are present, compute the composite risk score.

**Step 1 — Apply industry weights.**

Industry dimension weights adjust the relative contribution of each score dimension to composite. See Appendix A for the full industry weight table.

**Step 2 — Weighted sum.**

```
composite = Σ( score[dim] × industry_weight[dim] × base_weight[dim] )
            ─────────────────────────────────────────────────────────
              Σ( industry_weight[dim] × base_weight[dim] )
```

**Base weights:**

| Dimension | Base Weight |
|---|---|
| ARS (authority) | 0.25 |
| ORS (oversight) | 0.25 |
| EXS (consequence) | 0.20 |
| Ecosystem component of EXS | 0.15 |
| GMS (governance) | 0.15 |

Note: implementations that use a unified EXS score SHOULD apply the 0.20 weight to EXS and the 0.15 weight to GMS as the closest approximation.

**Step 3 — Normalize to integer [0, 100].**

### 6.3 Verdict Logic

Evaluated in priority order. First matching condition wins.

| Priority | Condition | Verdict |
|---|---|---|
| 1 | Any critical blocker present | `DANGER — DO NOT DEPLOY` |
| 2 | composite < 28 | `SAFE TO DEPLOY` |
| 3 | composite < 65 | `SAFE WITH EXCEPTIONS` |
| 4 | composite ≥ 65 | `DANGER — DO NOT DEPLOY` |

#### Verdict Rationale Strings

These exact strings MUST be used in the rationale field of any verdict output. Implementations MAY add supplemental context after the canonical string.

**SAFE TO DEPLOY:**
> The autonomous system appears operationally deployable under the declared scope. Authority boundaries, intervention pathways, and audit readiness appear sufficient for controlled deployment. Continuous monitoring is recommended as trust conditions may evolve after deployment.

**SAFE WITH EXCEPTIONS:**
> The autonomous system may proceed only under limited deployment conditions. Gate identified control gaps that require remediation or compensating controls before full production scope. Deployment should remain scoped and monitored until all exceptions are resolved.

**DANGER — DO NOT DEPLOY (blocker):**
> The autonomous system does not currently meet operational trust requirements for the declared scope. Gate identified critical control gaps that must be remediated before any production deployment. Deployment should be paused pending resolution of all identified blockers.

**DANGER — DO NOT DEPLOY (composite):**
> Operational trust capacity is insufficient for the declared deployment scope. The risk profile across authority, oversight, and consequence dimensions exceeds acceptable thresholds. Deployment should be paused pending governance remediation.

---

## 7. Mandated Output Sequence

Implementations MUST deliver outputs in this exact order. No output MAY be omitted or reordered.

```
Step 1   FREE DEPLOYMENT VERDICT
         ├─ Verdict label
         ├─ Verdict rationale (canonical string)
         └─ Active critical blockers (if any)

Step 2   THREE KEY FINDINGS
         ├─ Finding 1: Authority & Governance
         ├─ Finding 2: Evidence Readiness
         └─ Finding 3: Continuous Assurance

Step 3   RECOMMENDED NEXT STEP
         └─ One concrete, actionable recommendation

Step 4   ATC DECISION PROMPT (if atc_eligible = true)
         └─ Offer to generate ATC Pricing EPC
         └─ AWAIT explicit user confirmation before proceeding

Step 5   ATC PRICING EPC (if user consents)
         ├─ ATC tier classification
         ├─ Fee range
         ├─ Scope line items
         └─ Surcharge itemization

Step 6   CLOSE
```

**Critical constraint:** Implementations MUST NOT present any pricing information before Step 4. Implementations MUST NOT advance to Step 5 without explicit user consent at Step 4.

---

## 8. Three Findings Engine

Exactly three findings MUST be generated. Findings are numbered 1–3 and cover the three canonical areas defined below. The content MUST be derived from the specific scores and state fields of the assessed system; findings MUST NOT be generic.

**Severity Enumeration.** Each finding MUST carry exactly one severity value from the following set, in descending order of criticality:

| Value | Meaning |
|---|---|
| `CRITICAL` | Immediate remediation required; finding blocks deployment or ATC eligibility |
| `HIGH` | Material gap; remediation required before production scope or ATC progression |
| `MODERATE` | Notable gap; remediation recommended before full deployment |
| `LOW` | Minor or informational; no blocking condition present |

No other severity values are permitted in TGP-1 artifacts.

### Finding 1 — Authority and Governance Posture

**Derived from:** ARS, GMS, Stage 3, Stage 5.

**Logic:**
- If ARS ≥ 60 AND GMS ≥ 60: Finding severity = CRITICAL. Surface both authority breadth and governance gap.
- If ARS ≥ 60 AND GMS < 60: Finding severity = HIGH. Authority scope is the primary concern.
- If ARS < 60 AND GMS ≥ 60: Finding severity = HIGH. Governance gap is the primary concern.
- If ARS < 60 AND GMS < 60: Finding severity = MODERATE or LOW. Characterize what controls are adequate.

The finding MUST reference specific authority types present (e.g., financial authority, clinical workflows) and specific governance gaps (e.g., no kill switch, no audit trail).

### Finding 2 — Evidence Readiness

**Derived from:** ERS, Stage 6 fields.

**Logic:**
- If ERS ≥ 60: Finding severity = CRITICAL. System is not ready for a system review. List the most material missing evidence items.
- If ERS 30–59: Finding severity = HIGH. Evidence gaps will affect ATC tier and timeline. List gaps.
- If ERS < 30: Finding severity = LOW. Evidence posture is adequate. Note any missing items.

The finding MUST name specific missing documents or capabilities (e.g., "no incident response process", "no compliance mapping").

### Finding 3 — Continuous Assurance Readiness

**Derived from:** MRS, ATC eligibility, Stage 8 fields.

**Logic:**
- If `atc_eligible = false`: Finding MUST state that continuous assurance enrollment is not yet available and why.
- If `atc_eligible = true` AND MRS ≥ 50: Finding severity = HIGH. ATC eligible but Monitor readiness gaps exist.
- If `atc_eligible = true` AND MRS < 50: Finding severity = LOW. Note Monitor pathway is available post-ATC.

The finding MUST reference the "trust is temporal" principle and connect Monitor enrollment to the ATC lifecycle.

---

## 9. ATC Eligibility Engine

The Agentic Trust Certificate is issued only after a system review engagement is completed. This protocol determines eligibility for that engagement, not certificate issuance.

### 9.1 Eligibility Rules

A system is ATC-eligible if and only if ALL of the following conditions are true:

| Rule | Condition |
|---|---|
| ATC-E1 | `action_execution = true` OR `action_write = true` |
| ATC-E2 | `audit_logging = true` |
| ATC-E3 | `kill_switch = true` OR `fallback_mode = true` |
| ATC-E4 | `escalation_defined = true` |
| ATC-E5 | ERS < 80 |
| ATC-E6 | Verdict is NOT `DANGER — DO NOT DEPLOY` |

If any rule fails, `atc_eligible = false`. The system MUST remediate the failing conditions before re-assessment.

### 9.2 ATC Tier Classification

If eligible, the system is classified into one of three ATC tiers based on the risk profile.

| Tier | Criteria |
|---|---|
| Standard | ARS < 35 AND EXS < 30 AND no critical blockers |
| Advanced | (ARS 35–59 OR EXS 30–54) AND no critical blockers |
| Enterprise | ARS ≥ 60 OR EXS ≥ 55 OR `critical_infrastructure = true` OR `clinical_workflows = true` |

If multiple tier conditions match, the highest tier MUST be applied.

---

## 10. Monitor Eligibility Engine

### 10.1 Absolute Prerequisite

**Monitor eligibility requires a valid, unexpired ATC.**

Implementations MUST NOT enroll a system in Treasurety Monitor before an ATC has been issued for that system. This rule has no exceptions.

TGP-1 operates at assessment time — before any ATC has been issued. The `monitor_eligible` field in the EPC therefore represents a conditional eligibility signal, not an active enrollment status:

`monitor_eligible = atc_eligible`  *(assessment-time signal)*

This indicates whether the system will qualify for Monitor enrollment upon successful ATC issuance. Whether a valid, unexpired ATC exists is a runtime prerequisite evaluated outside TGP-1 scope — at the time the system attempts Monitor enrollment. Implementations managing ATC lifecycle MAY enforce this prerequisite at enrollment time; TGP-1 assessment implementations MUST NOT assume an ATC exists and MUST NOT set `monitor_eligible = true` for a system where `atc_eligible = false`.

### 10.2 Monitor Readiness Signal

MRS indicates how much preparatory work is needed before Monitor enrollment will be productive.

| MRS | Readiness Signal |
|---|---|
| < 20 | Highly ready — minimal setup required |
| 20–49 | Moderate gaps — address monitoring team and SLA gaps before enrollment |
| 50–74 | Significant gaps — drift detection and incident response must be established |
| ≥ 75 | Not ready — foundational monitoring infrastructure required first |

---

## 11. Shield Escalation Logic

Treasurety Shield reviews are triggered when ecosystem threat exposure exceeds thresholds that Govern and Monitor cannot address alone.

### 11.1 Shield Escalation Triggers

| ID | Condition | Escalation |
|---|---|---|
| SHD-1 | SRS ≥ 60 | Shield review REQUIRED before Monitor enrollment |
| SHD-2 | `critical_infrastructure = true` | Shield review RECOMMENDED at any SRS level |
| SHD-3 | `payment_rails = true` AND ARS ≥ 30 | Shield review REQUIRED |

`shield_review_required = (SRS ≥ 60) OR (payment_rails = true AND ARS ≥ 30)`

`shield_review_recommended = (critical_infrastructure = true AND NOT shield_review_required)`

### 11.2 Shield Review Ordering

If `shield_review_required = true`, the recommended next step MUST reference Shield review as a prerequisite to Monitor enrollment. Implementations MUST NOT present Monitor as immediately available when a Shield trigger is active.

---

## 12. ATC Pricing EPC Module

The Pricing EPC is produced only after explicit user consent (Step 4–5 of the mandated output sequence). It is a separate artifact from the main EPC.

### 12.1 Base Fee Schedule

| Tier | Base Fee | Fee Range |
|---|---|---|
| Standard | $4,500 | $4,500 – $7,500 |
| Advanced | $8,500 | $8,500 – $14,500 |
| Enterprise | $16,500 | $16,500 – $28,500 |

### 12.2 Surcharge Components

Surcharges are additive to the base fee range.

| Surcharge | Trigger Condition | Amount |
|---|---|---|
| Multi-agent complexity | `multi_agent = true` OR `can_create_subagents = true` | +$2,500 |
| Critical infrastructure | `critical_infrastructure = true` | +$3,500 |
| Clinical / patient workflows | `clinical_workflows = true` | +$4,000 |
| High evidence gap | ERS ≥ 60 | +$2,000 |
| Regulated data | `regulated_data_access = true` | +$1,500 |
| External content processing | `external_content = true` | +$1,000 |
| Payment rails | `payment_rails = true` | +$2,000 |
| Shield review required | `shield_review_required = true` | +$3,000 |

Implementations MUST itemize each applicable surcharge separately. The total quoted range MUST be base range + sum of applicable surcharges.

### 12.3 ATC Pricing EPC Schema

```json
{
  "protocol_version": "TGP-1",
  "artifact_type": "ATC_PRICING_EPC",
  "session_id": "string",
  "generated_at": "ISO 8601 UTC",
  "atc_tier": "Standard | Advanced | Enterprise",
  "base_fee": "integer",
  "fee_range": {
    "low": "integer",
    "high": "integer"
  },
  "surcharges": [
    {
      "label": "string",
      "amount": "integer"
    }
  ],
  "scope_items": ["string"],
  "total_range": {
    "low": "integer",
    "high": "integer"
  },
  "validity_days": 30,
  "notes": "string"
}
```

### 12.4 Scope Line Items

All ATC system reviews include:

- Governance evidence review (up to 8 documentation categories)
- Authority boundary assessment
- Oversight and intervention capacity review
- Consequence and ecosystem exposure analysis
- ATC issuance (digital artifact, 30-day validity)
- Executive governance summary report

Enterprise tier additionally includes:

- Regulatory alignment mapping
- Multi-stakeholder governance interview (up to 3 sessions)
- Shield integration assessment

---

## 13. Implementation Compliance

### 13.1 Required Behaviors

Conformant implementations MUST:

1. Collect all REQUIRED fields defined in Sections 3.1–3.9 before entering `EVALUATING` state.
2. Apply the scoring logic defined in Section 5 without modification.
3. Apply the critical blocker detection logic defined in Section 6.1 before computing composite score.
4. Deliver outputs in the sequence defined in Section 7.
5. Generate exactly three findings per the engine defined in Section 8.
6. Evaluate ATC eligibility per Section 9.1 exactly.
7. Apply Monitor eligibility rule per Section 10.1 exactly.
8. Apply Shield escalation triggers per Section 11.1 exactly.
9. Set `protocol_version = "TGP-1"` in all produced EPC artifacts.
10. Set `validity_days = 30` in all produced EPC artifacts.
11. Set `evidence_tier = "Tier 1 — Self-Declared"` for all self-reported assessments.

### 13.2 Prohibited Behaviors

Conformant implementations MUST NOT:

1. Present ATC pricing before the free verdict has been delivered.
2. Advance to ATC pricing without explicit user consent.
3. Omit any critical blocker from the verdict output when blockers are present.
4. Apply verdict thresholds other than those defined in Section 6.3.
5. Generate fewer or more than three findings.
6. Enroll a system in Monitor without a valid ATC.
7. Classify a system as ATC-eligible if any rule in Section 9.1 fails.
8. Modify industry weights or base weights defined in Appendix A.
9. Omit `protocol_version` from any EPC artifact.
10. Present the recommended next step before the three findings.

### 13.3 Self-Declared Assessment Limitations

All assessments produced under this protocol from user-provided inputs are Tier 1 — Self-Declared. Implementations MUST make this limitation visible to the user. The ATC system review process upgrades evidence to Tier 2 — Verified upon completion of independent review.

---

## 14. Reserved Extension Points

The following protocol elements are reserved for future versions and MUST NOT be used in TGP-1 implementations:

- `evidence_tier` values beyond `"Tier 1 — Self-Declared"` (Tier 2–4 are reserved for verified assessment tiers)
- `protocol_version` values other than `"TGP-1"` (TGP-2 is reserved)
- Stage 9+ collection stages
- ATC tier values beyond Standard / Advanced / Enterprise
- `artifact_type` values beyond `EPC` and `ATC_PRICING_EPC`

---

## Appendix A — Industry Dimension Weights

These weights MUST be applied during composite score calculation (Section 6.2). They represent industry-specific sensitivity to each governance dimension.

| Industry | Authority | Oversight | Consequence | Ecosystem | Governance |
|---|---|---|---|---|---|
| Financial Services | 1.4 | 1.2 | 1.3 | 1.0 | 1.3 |
| Healthcare | 1.2 | 1.4 | 1.5 | 1.0 | 1.2 |
| Manufacturing | 1.0 | 1.2 | 1.3 | 0.9 | 1.1 |
| Supply Chain & Logistics | 1.1 | 1.0 | 1.1 | 1.2 | 1.0 |
| Insurance | 1.2 | 1.2 | 1.3 | 1.0 | 1.3 |
| Energy & Utilities | 1.3 | 1.3 | 1.5 | 1.0 | 1.2 |
| Government | 1.2 | 1.3 | 1.3 | 1.0 | 1.4 |
| Cybersecurity | 1.5 | 1.2 | 1.2 | 1.1 | 1.1 |
| Enterprise Operations | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| AI Infrastructure | 1.3 | 1.1 | 1.1 | 1.2 | 1.0 |
| Multi-Agent Orchestration | 1.4 | 1.2 | 1.0 | 1.3 | 1.1 |
| Other | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

---

## Appendix B — Canonical Terminology

Implementations MUST use these terms consistently in all user-facing output.

| Term | Definition |
|---|---|
| Agentic Trust Certificate (ATC) | Point-in-time deployment authorization artifact issued after a completed system review |
| ATC system review | The independent evidence review engagement that produces an ATC |
| Continuous assurance | Ongoing post-deployment monitoring of governance posture drift |
| Deployment verdict | The Gate evaluation outcome: SAFE TO DEPLOY, SAFE WITH EXCEPTIONS, or DANGER — DO NOT DEPLOY |
| EPC | Entity-Purpose-Context — the canonical machine-readable governance record |
| Governance posture | The aggregate state of an organization's controls over an autonomous system |
| System review | See: ATC system review |
| Trust is temporal | Core principle: governance readiness is point-in-time, not permanent |
| Treasurety Gate | Customer-facing governance intake and ATC entry point |
| Treasurety Govern | Core runtime governance engine |

**Prohibited substitutions:** Implementations MUST NOT use "evidence review" in place of "system review". Implementations MUST NOT use "certificate" alone — always "Agentic Trust Certificate" or "ATC" on first reference.

---

## Appendix C — Recommended Next Step Logic

The recommended next step in Section 7 Step 3 MUST be derived from the following priority table:

| Priority | Condition | Recommended Next Step |
|---|---|---|
| 1 | Any BLK-01 through BLK-08 active | Remediate all critical blockers before any deployment activity. |
| 2 | Verdict = DANGER (composite) | Commission a governance remediation review targeting authority boundaries and oversight controls. |
| 3 | `atc_eligible = true` AND `shield_review_required = true` | Initiate a Treasurety Shield review before progressing to ATC system review. |
| 4 | `atc_eligible = true` AND `shield_review_required = false` | Proceed to an ATC system review to formalize deployment authorization. |
| 5 | `atc_eligible = false` AND ERS ≥ 60 | Build governance documentation foundation before pursuing ATC eligibility. |
| 6 | `atc_eligible = false` AND ERS < 60 | Address ATC eligibility gaps: establish kill switch, escalation pathway, or audit capability. |
| 7 | Verdict = SAFE TO DEPLOY | Activate Treasurety Monitor post-deployment for continuous assurance. |

---

*Treasurety Gate Protocol v1 — TGP-1*  
*Canonical specification for all Treasurety Gate implementations.*  
*"Trust is temporal. Continuous assurance requires a valid ATC."*
