HIGH_RISK_KEYWORDS = [
    "면책", "포기", "일방적", "손해배상 없음", "해지 불가", "무효",
    "전적으로", "책임지지 않", "청구 불가", "제한 없이",
]


def classify_risk(analysis: list[dict]) -> list[dict]:
    results = []
    for item in analysis:
        if not item["is_risky"]:
            risk_level = "low"
        elif any(kw in item["reason"] for kw in HIGH_RISK_KEYWORDS):
            risk_level = "high"
        else:
            risk_level = "medium"
        results.append({**item, "risk_level": risk_level})
    return results
