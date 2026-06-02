# 계약문서 위험조항 분석 Agent - 프로젝트 세팅 계획

## 생성할 파일 목록

| 파일 | 내용 요약 |
|------|-----------|
| `docker-compose.yml` | backend(8000), frontend(8501) 두 서비스 정의. .env 로드, 볼륨 마운트, depends_on |
| `.env.example` | OPENAI_API_KEY, UPSTAGE_API_KEY 빈 값 템플릿 |
| `.gitignore` | .env, __pycache__/, *.pyc, .DS_Store |
| `README.md` | 프로젝트 설명, docker compose up --build 실행법, 접속 주소 (기존 파일 덮어쓰기) |
| `backend/Dockerfile` | python:3.11-slim, requirements 설치 후 소스 복사, uvicorn 실행 |
| `backend/requirements.txt` | fastapi, uvicorn, python-multipart, langchain, langchain-openai, python-dotenv, httpx |
| `backend/main.py` | FastAPI 앱, GET / 헬스체크 엔드포인트 |
| `backend/services/extractor.py` | extract_text(file), split_clauses(text) 스텁 |
| `backend/services/analyzer.py` | detect_contract_type(text), analyze_clauses(clauses, contract_type) 스텁 |
| `backend/services/classifier.py` | classify_risk(analysis) 스텁 |
| `backend/services/summarizer.py` | summarize(text) 스텁 |
| `backend/services/explainer.py` | explain(clause) 스텁 |
| `frontend/Dockerfile` | python:3.11-slim, requirements 설치 후 소스 복사, streamlit 실행 |
| `frontend/requirements.txt` | streamlit, httpx, python-dotenv |
| `frontend/app.py` | Streamlit 페이지: 제목, 파일 업로더, 계약 유형 셀렉트박스, 분석 버튼(backend 헬스체크만) |

## 최종 디렉토리 구조

```
swmaestro-ai-education/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md           ← 기존 파일 덮어쓰기
├── plan.md             ← 이 파일
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── services/
│       ├── extractor.py
│       ├── analyzer.py
│       ├── classifier.py
│       ├── summarizer.py
│       └── explainer.py
└── frontend/
    ├── Dockerfile
    ├── requirements.txt
    └── app.py
```

## 작업 단계

1. **[완료]** 레포 클론
2. **[완료]** plan.md 작성 → 승인 대기
3. 루트 파일 4개 생성: docker-compose.yml, .env.example, .gitignore, README.md
4. backend/ 디렉토리 파일 생성: Dockerfile, requirements.txt, main.py
5. backend/services/ 디렉토리 스텁 파일 5개 생성
6. frontend/ 디렉토리 파일 생성: Dockerfile, requirements.txt, app.py
7. `docker compose up --build` 실행하여 두 컨테이너 정상 기동 검증
8. `feat/1-project-setup` 브랜치 생성 후 커밋

## 제약 확인

- API 키 하드코딩 없음 → .env에서만 로드
- 분석 로직 미구현 → 함수 스텁(pass)만 작성
- 주석 없음
- 요청된 파일 외 추가 없음
