import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


def explain(clause: str) -> str:
    llm = ChatOpenAI(model="solar-pro", temperature=0, api_key=os.getenv("UPSTAGE_API_KEY"), base_url="https://api.upstage.ai/v1")
    prompt = PromptTemplate(
        input_variables=["clause"],
        template=(
            "당신은 법률 전문가입니다. 아래 계약서 조항을 일반인이 이해할 수 있도록 설명해주세요.\n\n"
            "조항: {clause}\n\n"
            "다음 항목을 순서대로 답하세요:\n"
            "1. 이 조항의 의미: (2~3문장)\n"
            "2. 계약자에게 불리한 점: (있으면 구체적으로, 없으면 '없음')\n"
            "3. 주의해야 할 점: (실용적인 조언 1~2가지)"
        ),
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"clause": clause}).strip()
