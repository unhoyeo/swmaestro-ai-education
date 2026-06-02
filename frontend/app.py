import streamlit as st
import httpx

st.title("계약문서 위험조항 분석 Agent")

uploaded_file = st.file_uploader("계약서 파일을 업로드하세요", type=["pdf", "docx", "txt"])

contract_type = st.selectbox(
    "계약 유형을 선택하세요",
    ["근로", "전세", "외주", "이용약관", "기타"],
)

if st.button("분석 시작"):
    try:
        response = httpx.get("http://backend:8000/")
        if response.status_code == 200:
            st.success("백엔드 연결 성공: " + str(response.json()))
        else:
            st.error("백엔드 응답 오류: " + str(response.status_code))
    except Exception as e:
        st.error("백엔드 연결 실패: " + str(e))
