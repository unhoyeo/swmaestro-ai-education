# 계약문서 위험조항 분석 Agent

계약서를 업로드하면 AI Agent가 위험 조항을 탐지·요약·설명하는 서비스입니다.

## 기술 스택

- Frontend: Streamlit
- Backend: FastAPI + LangChain + Upstage Document Parse
- 인프라: Docker Compose

## 실행 방법

```bash
cp .env.example .env
# .env 파일에 API 키 입력 후 실행
docker compose up --build
```

## 접속 주소

| 서비스 | 주소 |
|--------|------|
| Backend API 문서 | http://localhost:8000/docs |
| Frontend | http://localhost:8501 |
