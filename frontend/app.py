import streamlit as st
import httpx
import pandas as pd

st.title("계약문서 위험조항 분석 Agent")

uploaded_file = st.file_uploader("계약서 파일을 업로드하세요", type=["pdf", "docx", "txt"])

contract_type = st.selectbox(
    "계약 유형을 선택하세요",
    ["자동 감지", "근로", "전세", "외주", "이용약관", "기타"],
)

RISK_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}

if st.button("분석 시작"):
    if not uploaded_file:
        st.warning("파일을 먼저 업로드해주세요.")
    else:
        with st.spinner("분석 중..."):
            try:
                response = httpx.post(
                    "http://backend:8000/analyze",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    data={"contract_type": contract_type},
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"분석 실패: {e}")
                st.stop()

        st.session_state["result"] = result

if "result" in st.session_state:
    result = st.session_state["result"]

    if result.get("detected_type"):
        st.caption(f"자동 감지된 계약 유형: **{result['detected_type']}**")

    st.subheader("전체 요약")
    st.info(result["summary"])

    risky_clauses = [c for c in result["clauses"] if c["is_risky"]]

    st.subheader("조항별 분석 결과")
    if risky_clauses:
        rows = [
            {
                "위험도": RISK_COLOR.get(c["risk_level"], "") + " " + c["risk_level"].upper(),
                "조항 (앞 120자)": c["clause"][:120] + ("..." if len(c["clause"]) > 120 else ""),
                "분석 이유": c["reason"],
            }
            for c in risky_clauses
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

        st.subheader("조항 상세 설명")
        for i, clause in enumerate(risky_clauses):
            label = f"{RISK_COLOR.get(clause['risk_level'], '')} [{clause['risk_level'].upper()}] {clause['clause'][:60]}..."
            with st.expander(label):
                st.markdown(f"**전체 조항**\n\n{clause['clause']}")
                if st.button("상세 설명 보기", key=f"explain_{i}"):
                    with st.spinner("설명 생성 중..."):
                        try:
                            resp = httpx.post(
                                "http://backend:8000/explain",
                                json={"clause": clause["clause"]},
                                timeout=60,
                            )
                            resp.raise_for_status()
                            st.markdown(resp.json()["explanation"])
                        except Exception as e:
                            st.error(f"설명 실패: {e}")
    else:
        st.success("위험 조항이 발견되지 않았습니다.")
