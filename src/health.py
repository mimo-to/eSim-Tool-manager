def compute(results: list[dict]) -> dict:
    score = 100
    for res in results:
        if not res["installed"]:
            if res["required"]:
                score -= 30
            else:
                score -= 10
    
    score = max(0, min(100, score))
    
    if score >= 80:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 40:
        status = "Partial"
    else:
        status = "Critical"
        
    return {"score": score, "status": status}
