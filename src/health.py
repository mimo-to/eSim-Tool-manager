def compute(results):
    required = [r for r in results if r["required"]]
    optional = [r for r in results if not r["required"]]

    req_ok = sum(1 for r in required if r["installed"] and not r.get("conflict") and not r.get("path_issue"))
    opt_ok = sum(1 for r in optional if r["installed"] and not r.get("path_issue"))

    req_score = (req_ok / len(required) * 70) if required else 70
    opt_score = (opt_ok / len(optional) * 30) if optional else 30

    score = round(req_score + opt_score)
    score = max(0, min(100, score))

    if score == 100:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    elif score >= 40:
        status = "Partial"
    else:
        status = "Critical"

    conflicts = [r for r in results if r.get("conflict")]

    return {
        "score": score,
        "status": status,
        "required_installed": req_ok,
        "required_total": len(required),
        "optional_installed": opt_ok,
        "optional_total": len(optional),
        "conflicts": conflicts
    }
