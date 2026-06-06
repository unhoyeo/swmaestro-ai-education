RISK_KEYWORDS_BY_TYPE = {
    "근로": [
        "임금 삭감", "급여 미지급", "지급하지 않", "지급 거부",
        "수습기간 무급", "시급 미달",
        "즉시 해고", "사전 통지 없이 해고", "위약금", "손해배상 청구",
        "경업금지", "퇴직 후 경업", "동종업계 취업 금지",
        "비밀유지 위반 시 손해배상",
        "추가 수당 없음", "연장근로 미지급",
    ],
    "전세": [
        "보증금 반환 거절", "보증금 공제", "보증금 미반환",
        "보증금을 돌려주지", "반환하지 않",
        "임대인 책임 없음", "하자 책임 없음",
        "원상복구 비용 전액", "수리비 전액 부담",
        "계약 위반 시 보증금 몰수", "보증금 몰취",
    ],
    "외주": [
        "대금 미지급", "지급 거절", "지체상금", "지연배상",
        "검수 불합격 시 미지급",
        "저작권 귀속", "산출물 귀속", "모든 권리 양도",
        "2차 저작물 권리",
        "무상 유지보수", "무기한 유지보수", "기간 제한 없이",
        "계약금 이상 배상", "실손해 초과 배상",
    ],
    "이용약관": [
        "자동 갱신", "자동으로 연장", "자동 결제",
        "개인정보 제3자 제공", "개인정보 판매", "동의 없이 제공",
        "약관 일방 변경", "사전 공지 없이 변경", "서비스 중단 면책",
        "위약금", "해지 위약금", "환불 불가",
        "서비스 장애 면책", "데이터 손실 면책",
    ],
    "기타": [
        "자동 갱신", "위약금", "일방적 해지",
        "책임 제한", "개인정보 제공", "환불 불가",
    ],
}

COMMON_HIGH_RISK_KEYWORDS = [
    "면책", "책임지지 않", "책임을 지지", "배상하지 않", "배상 책임 없",
    "손해배상 없음", "손해를 배상하지",
    "일방적", "일방적으로", "사전 통보 없이", "사전 동의 없이",
    "청구 불가", "청구할 수 없", "청구권 포기",
    "해지 불가", "해지할 수 없", "취소 불가",
    "포기", "권리 포기", "무효", "전적으로",
    "제한 없이", "제한 없는",
]


def _get_keywords(contract_type: str) -> list[str]:
    type_kw = RISK_KEYWORDS_BY_TYPE.get(contract_type, RISK_KEYWORDS_BY_TYPE["기타"])
    return COMMON_HIGH_RISK_KEYWORDS + type_kw


def _is_high_risk(item: dict, keywords: list[str]) -> bool:
    targets = [item.get("reason", ""), item.get("clause", "")]
    return any(kw in target for kw in keywords for target in targets)


def classify_risk(analysis: list[dict], contract_type: str = "기타") -> list[dict]:
    keywords = _get_keywords(contract_type)
    results = []
    for item in analysis:
        if not item["is_risky"]:
            risk_level = "low"
        elif _is_high_risk(item, keywords):
            risk_level = "high"
        else:
            risk_level = "medium"
        results.append({**item, "risk_level": risk_level})
    return results
