COMMON_HIGH_RISK_KEYWORDS = [
    "면책", "책임지지 않", "책임을 지지", "배상하지 않", "배상 책임 없",
    "손해배상 없음", "손해를 배상하지",
    "일방적", "일방적으로", "사전 통보 없이", "사전 동의 없이",
    "청구 불가", "청구할 수 없", "청구권 포기",
    "해지 불가", "해지할 수 없", "취소 불가",
    "포기", "권리 포기", "무효", "전적으로",
    "제한 없이", "제한 없는",
]


def classify_risk(analysis: list[dict]) -> list[dict]:
    results = []
    for item in analysis:
        if not item["is_risky"]:
            risk_level = "low"
        elif any(kw in item["reason"] for kw in COMMON_HIGH_RISK_KEYWORDS):
            risk_level = "high"
        else:
            risk_level = "medium"
        results.append({**item, "risk_level": risk_level})
    return results
