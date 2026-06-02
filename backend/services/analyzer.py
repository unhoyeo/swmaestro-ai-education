import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

VALID_TYPES = ["근로", "전세", "외주", "이용약관", "기타"]

RISK_CRITERIA = {
    "근로": "임금/급여 지급 조건, 근로시간, 수습기간, 퇴사·해지 조건, 위약금, 비밀유지·경업금지",
    "전세": "보증금 반환 조건, 특약사항, 계약 해지, 원상복구 범위, 임대인 책임",
    "외주": "대금 지급 시점·조건, 지체상금/지연배상, 저작권·산출물 귀속, 유지보수 범위",
    "이용약관": "자동 갱신, 과도한 위약금, 개인정보 제3자 제공, 책임 제한·면책, 일방적 해지",
    "기타": "자동 갱신, 과도한 위약금, 일방적 해지, 책임 제한, 개인정보 제공",
}


def detect_contract_type(text: str) -> str:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "아래 계약서 내용을 읽고 계약 유형을 판단하세요.\n\n"
            "{text}\n\n"
            "다음 중 하나로만 답하세요 (다른 말 없이 정확히 한 단어):\n"
            "근로 / 전세 / 외주 / 이용약관 / 기타"
        ),
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"text": text[:2000]}).strip()
    return result if result in VALID_TYPES else "기타"


def analyze_clauses(clauses: list[str], contract_type: str) -> list[dict]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    criteria = RISK_CRITERIA.get(contract_type, RISK_CRITERIA["기타"])
    prompt = PromptTemplate(
        input_variables=["contract_type", "criteria", "clause"],
        template=(
            "당신은 법률 전문가입니다. 아래는 {contract_type} 계약서의 조항입니다.\n"
            "이 조항이 계약자에게 불리하거나 위험한지 판단하세요.\n\n"
            "다음 항목들을 특히 중점적으로 점검하세요: {criteria}\n\n"
            "조항: {clause}\n\n"
            "다음 형식으로만 답하세요:\n"
            "위험여부: (예/아니오)\n"
            "이유: (한 문장으로)"
        ),
    )
    chain = prompt | llm | StrOutputParser()
    results = []

    for clause in clauses:
        text_out = chain.invoke({"contract_type": contract_type, "criteria": criteria, "clause": clause}).strip()
        is_risky = "예" in text_out.split("\n")[0]
        reason_line = next((l for l in text_out.split("\n") if l.startswith("이유:")), "이유: 해당 없음")
        reason = reason_line.replace("이유:", "").strip()
        results.append({"clause": clause, "is_risky": is_risky, "reason": reason})

    return results
