def decision_color(decision):
    colors = {
        "ALLOW": "#16a34a",
        "HOLD": "#f59e0b",
        "ESCALATE": "#ea580c",
        "BLOCK": "#dc2626",
    }

    return colors.get(decision, "#64748b")