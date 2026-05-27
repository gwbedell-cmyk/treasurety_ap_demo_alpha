import json
from datetime import datetime
from pathlib import Path

AUDIT_FILE = Path("data/audit_log.json")


def load_audit_log():
    if not AUDIT_FILE.exists():
        return []

    with open(AUDIT_FILE, "r") as f:
        return json.load(f)


def save_audit_log(log):
    with open(AUDIT_FILE, "w") as f:
        json.dump(log, f, indent=2)


def record_decision(action, evaluation):
    log = load_audit_log()

    existing = next(
        (item for item in log if item["action_id"] == action["id"]),
        None
    )

    if existing:
        return

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "action_id": action["id"],
        "agent_id": action["agent_id"],
        "counterparty": action.get("counterparty", action.get("vendor_name", "—")),
        "decision": evaluation["decision"],
        "risk_score": evaluation["risk_score"],
        "triggered_policies": evaluation["triggered_policies"],
        "findings": evaluation["explanations"]
    }

    log.append(record)
    save_audit_log(log)