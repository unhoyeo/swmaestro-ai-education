import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def detect_contract_type(text: str) -> str:
    pass


def analyze_clauses(clauses: list[str], contract_type: str) -> list[dict]:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["contract_type", "clause"],
        template=(
            "당신은 법률 전문가입니다. 아래는 {contract_type} 계약서의 조항입니다.\n"
            "이 조항이 계약자에게 불리하거나 위험한지 판단하세요.\n\n"
            "조항: {clause}\n\n"
            "다음 형식으로만 답하세요:\n"
            "위험여부: (예/아니오)\n"
            "이유: (한 문장으로)"
        ),
    )
    chain = prompt | llm | StrOutputParser()
    results = []

    for clause in clauses:
        text_out = chain.invoke({"contract_type": contract_type, "clause": clause}).strip()
        is_risky = "예" in text_out.split("\n")[0]
        reason_line = next((l for l in text_out.split("\n") if l.startswith("이유:")), "이유: 해당 없음")
        reason = reason_line.replace("이유:", "").strip()
        results.append({"clause": clause, "is_risky": is_risky, "reason": reason})

    return results
