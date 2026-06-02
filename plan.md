# 계약문서 위험조항 분석 Agent - 구현 계획

## Phase 1: 프로젝트 초기 환경 세팅 [완료]

---

## Phase 2: Upstage Document Parse 연동 + 분석 파이프라인 구현

### 전체 데이터 흐름

```
[사용자] 파일 업로드 + 계약 유형 선택
    ↓
[frontend/app.py] POST /analyze 호출
    ↓
[main.py] /analyze 엔드포인트
    ↓
[extractor.py] Upstage Document Parse API → 텍스트 추출 → 조항 분리
    ↓
[analyzer.py] LangChain LLM → 각 조항 위험 분석
    ↓
[classifier.py] 위험도 분류 (high / medium / low)
    ↓
[summarizer.py] 전체 요약 생성
    ↓
[frontend/app.py] 결과 테이블 + 요약 표시
```

---

### 변경/추가 파일 목록

| 파일 | 변경 내용 |
|------|-----------|
| `backend/requirements.txt` | `langchain-community`, `openai` 추가 |
| `backend/services/extractor.py` | Upstage Document Parse API 호출로 텍스트 추출, 조항 분리 구현 |
| `backend/services/analyzer.py` | LangChain + ChatOpenAI로 조항별 위험 분석 구현 |
| `backend/services/classifier.py` | 분석 결과에서 위험도(high/medium/low) 분류 구현 |
| `backend/services/summarizer.py` | 위험 조항 목록 전체 요약 구현 |
| `backend/main.py` | `POST /analyze` 엔드포인트 추가 |
| `frontend/app.py` | 분석 결과(위험 조항 테이블 + 요약) 표시 구현 |

> `explainer.py`는 이번 Phase에서 구현하지 않음 (단일 조항 상세 설명은 별도 단계)

---

### 각 파일 상세 설계

#### backend/services/extractor.py
- `extract_text(file_bytes, filename)`:
  - Upstage Document Parse REST API(`https://api.upstage.ai/v1/document-digitization`)에 `multipart/form-data`로 파일 전송
  - 응답 JSON의 `content.text` 필드에서 전체 텍스트 반환
- `split_clauses(text)`:
  - 조항 번호 패턴(`제X조`, `X.`, `(X)` 등) 기준으로 텍스트를 조항 리스트로 분리
  - 최소 길이(30자) 미만 조각은 제외

#### backend/services/analyzer.py
- `detect_contract_type(text)` — 이번 Phase에서는 프론트에서 선택한 값을 그대로 받으므로 패스
- `analyze_clauses(clauses, contract_type)`:
  - `ChatOpenAI(model="gpt-4o-mini")` 사용
  - 각 조항에 대해 LangChain `PromptTemplate` + `LLMChain`으로 위험 여부·이유 분석
  - 반환 형식: `list[dict]` — `{clause, is_risky: bool, reason: str}`
  - 조항이 많을 경우 상위 20개만 처리 (비용 제한)

#### backend/services/classifier.py
- `classify_risk(analysis)`:
  - `analyze_clauses` 결과를 받아 각 항목에 `risk_level` 필드 추가
  - LLM 없이 규칙 기반: `is_risky=True`이면 reason 길이/키워드로 `high` / `medium` 분류, `False`이면 `low`
  - 반환 형식: `list[dict]` — `{clause, is_risky, reason, risk_level}`

#### backend/services/summarizer.py
- `summarize(classified_results)`:
  - `ChatOpenAI(model="gpt-4o-mini")` 사용
  - 위험 조항(`is_risky=True`)만 추려 한국어 요약 2~3문장 생성

#### backend/main.py — POST /analyze
```
Request: multipart/form-data
  - file: UploadFile
  - contract_type: str (Form)

Response: JSON
  {
    "contract_type": str,
    "clauses": [{ clause, is_risky, reason, risk_level }],
    "summary": str
  }
```

#### frontend/app.py
- 분석 버튼 클릭 시 `POST /analyze`에 파일 + 계약 유형 전송
- 응답 수신 후:
  - 요약(summary) 텍스트 박스 표시
  - 위험 조항 테이블(`st.dataframe`): 조항 텍스트, 위험도, 이유
  - 위험도별 색상 구분 (high=빨강, medium=노랑, low=초록)

---

### 작업 단계

1. plan.md 작성 → 승인 대기
2. `backend/requirements.txt` 업데이트
3. `backend/services/extractor.py` 구현
4. `backend/services/analyzer.py` 구현
5. `backend/services/classifier.py` 구현
6. `backend/services/summarizer.py` 구현
7. `backend/main.py` `/analyze` 엔드포인트 추가
8. `frontend/app.py` 결과 표시 구현
9. `docker compose up --build` 재검증
10. `feat/2-analysis-pipeline` 브랜치 커밋
