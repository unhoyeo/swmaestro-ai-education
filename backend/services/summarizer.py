import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def summarize(classified_results: list[dict]) -> str:
    risky = [r for r in classified_results if r["is_risky"]]
    if not risky:
        return "위험 조항이 발견되지 않았습니다."

    clause_summary = "\n".join(
        f"- [{r['risk_level'].upper()}] {r['reason']}" for r in risky
    )
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables=["clauses"],
        template=(
            "아래는 계약서에서 발견된 위험 조항 목록입니다.\n"
            "{clauses}\n\n"
            "이 계약서의 전체적인 위험도를 2~3문장으로 한국어로 요약해주세요."
        ),
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"clauses": clause_summary}).strip()
