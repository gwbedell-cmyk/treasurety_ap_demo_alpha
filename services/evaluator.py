def evaluate_action(action):
    risk = 0
    explanations = []
    triggered_policies = []

    if action.get("bank_changed_days", 999) <= 7:
        risk += 30
        explanations.append("Counterparty destination details changed within trust window")
        triggered_policies.append("P-12 Counterparty Change Risk")

    if action.get("duplicate_similarity", 0) > 0.8:
        risk += 35
        explanations.append("Potential duplicate action submission detected")
        triggered_policies.append("P-27 Duplicate Submission Detection")

    if not action.get("approval_complete", True):
        risk += 20
        explanations.append("Authority chain incomplete — execution not fully delegated")
        triggered_policies.append("P-19 Authority Chain Completeness")

    if action.get("po_amount", 0) > 0:
        po_variance = (action["amount"] - action["po_amount"]) / action["po_amount"]

        if po_variance > 0.10:
            risk += 15
            explanations.append("Proposed action exceeds authorized scope boundary")
            triggered_policies.append("P-31 Policy Boundary Variance")

    if action.get("vendor_risk_score", 0) > 0.5:
        risk += 10
        explanations.append("Elevated counterparty trust signal")
        triggered_policies.append("P-42 Counterparty Risk Escalation")

    # Taxonomy: ALLOW → HOLD → ESCALATE → BLOCK
    # BLOCK is explicit denial (highest severity)
    if risk >= 90:
        decision = "BLOCK"
    elif risk >= 70:
        decision = "ESCALATE"
    elif risk >= 40:
        decision = "HOLD"
    else:
        decision = "ALLOW"

    return {
        "risk_score": risk,
        "decision": decision,
        "explanations": explanations,
        "triggered_policies": triggered_policies
    }