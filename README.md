# 계약문서 위험조항 분석 Agent

계약서를 업로드하면 AI Agent가 위험 조항을 자동으로 탐지·분류·요약·설명하는 서비스입니다.
법률 지식이 없는 일반 사용자도 계약서의 위험 요소를 쉽게 파악할 수 있도록 돕습니다.

> ⚠️ 이 서비스의 분석 결과는 참고용이며, 법률 전문가의 자문을 대체하지 않습니다.

---

## 지원 계약 유형

| 유형 | 주요 점검 항목 |
|------|--------------|
| 근로 | 임금/급여 지급 조건, 근로시간, 수습기간, 퇴사·해지 조건, 위약금, 비밀유지·경업금지 |
| 전세 | 보증금 반환 조건, 특약사항, 계약 해지, 원상복구 범위, 임대인 책임 |
| 외주 | 대금 지급 시점·조건, 지체상금/지연배상, 저작권·산출물 귀속, 유지보수 범위 |
| 이용약관 | 자동 갱신, 과도한 위약금, 개인정보 제3자 제공, 책임 제한·면책, 일방적 해지 |
| 기타 | 자동 갱신, 과도한 위약금, 일방적 해지, 책임 제한, 개인정보 제공 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Streamlit |
| Backend | FastAPI |
| AI/LLM | Upstage Solar Pro (LangChain LCEL) |
| 문서 추출 | Upstage Document Digitization API |
| 인프라 | Docker Compose |

---

## 시스템 아키텍처

```
[사용자]
    │
    │  파일 업로드 + 계약 유형 선택
    ▼
[Frontend — Streamlit :8501]
    │
    │  POST /analyze (multipart/form-data)
    ▼
[Backend — FastAPI :8000]
    │
    ├─ extractor.py    ← Upstage Document Digitization API 호출
    ├─ analyzer.py     ← Solar Pro LLM으로 유형 감지 + 조항별 위험 분석
    ├─ classifier.py   ← 규칙 기반 위험도 분류 (high/medium/low)
    ├─ summarizer.py   ← Solar Pro LLM으로 전체 요약 생성
    └─ explainer.py    ← Solar Pro LLM으로 조항 상세 설명 생성
    │
    │  JSON 응답 반환
    ▼
[Frontend — 결과 화면]
    ├─ 전체 요약 박스
    ├─ 위험 조항 테이블 (🔴 HIGH / 🟡 MEDIUM / 🟢 LOW)
    └─ 조항별 expander → 상세 설명 보기
```

---

## 분석 파이프라인

### 전체 흐름

```
파일 업로드 (PDF / docx / txt)
    │
    ▼
① extract_text()          [extractor.py — 여운호]
    Upstage Document Digitization API로 파일에서 텍스트 추출
    │
    ▼
② split_clauses()         [extractor.py — 여운호]
    "제N조", "N.", "(N)" 패턴으로 조항 단위 분리 (최대 20개)
    │
    ▼
③ detect_contract_type()  [analyzer.py — 최종은]
    계약서 앞 2000자를 Solar Pro에 전달
    → 근로 / 전세 / 외주 / 이용약관 / 기타 중 하나 자동 판별
    ("자동 감지" 선택 시에만 실행, 직접 선택 시 생략)
    │
    ▼
④ analyze_clauses()       [analyzer.py — 최종은]
    계약 유형별 위험 점검 기준(RISK_CRITERIA)을 프롬프트에 주입
    조항마다 Solar Pro 호출 → 위험 여부(True/False) + 이유 반환
    │
    ▼
⑤ classify_risk()         [classifier.py — 김태현]
    LLM 없이 규칙 기반으로 위험도 분류
    is_risky=True + 키워드 포함 → high
    is_risky=True + 키워드 없음 → medium
    is_risky=False            → low
    │
    ▼
⑥ summarize()             [summarizer.py — 박영우]
    위험 조항(is_risky=True)만 추려 Solar Pro로 한국어 요약 2~3문장 생성
    │
    ▼
⑦ explain()               [explainer.py — 전동훈]
    사용자가 특정 조항 클릭 시 Solar Pro 호출
    ① 조항의 의미 ② 불리한 점 ③ 주의사항 3단계 설명 생성
```

### API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/` | 헬스체크 |
| POST | `/analyze` | 계약서 전체 분석 파이프라인 실행 |
| POST | `/explain` | 단일 조항 상세 설명 생성 |

#### POST /analyze 요청

```
Content-Type: multipart/form-data

file          : 계약서 파일 (PDF / docx / txt)
contract_type : "자동 감지" | "근로" | "전세" | "외주" | "이용약관" | "기타"
```

#### POST /analyze 응답

```json
{
  "contract_type": "전세",
  "detected_type": "전세",
  "clauses": [
    {
      "clause": "임차인은 계약 해지 시 위약금으로 보증금의 50%를 지급한다.",
      "is_risky": true,
      "reason": "보증금 반환 조건이 일방적으로 불리하게 설정되어 있습니다.",
      "risk_level": "high"
    }
  ],
  "summary": "이 계약서는 보증금 반환 조건과 특약사항에서 임차인에게 불리한 조항이 다수 발견됩니다..."
}
```

---

## 역할 분담

| 이름 | 담당 파일 | 역할 |
|------|-----------|------|
| 여운호 | `extractor.py` | 텍스트 추출 + 조항 분리 |
| 최종은 | `analyzer.py` | 계약 유형 확인 + 유형별 기준 로드 + LLM 조항 분석 |
| 김태현 | `classifier.py` | 위험도 분류 (high / medium / low) |
| 박영우 | `summarizer.py` | 계약서 전체 요약 생성 |
| 전동훈 | `explainer.py` | 조항별 쉬운 설명 생성 |

---

## 프로젝트 구조

```
swmaestro-ai-education/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
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

---

## 실행 방법

### 사전 준비

- Docker Desktop 설치 및 실행
- Upstage API 키 발급 (https://console.upstage.ai)

### 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일에 API 키를 입력합니다.

```
UPSTAGE_API_KEY=your_api_key_here
```

### 서비스 실행

```bash
# 처음 실행 (이미지 빌드 포함)
docker compose up --build

# 이후 실행
docker compose up

# 종료
docker compose down
```

### 접속

| 서비스 | 주소 |
|--------|------|
| Frontend (Streamlit) | http://localhost:8501 |
| Backend API 문서 (Swagger) | http://localhost:8000/docs |

---

## 브랜치 전략

GitHub Flow를 따릅니다.

| 브랜치 | 용도 |
|--------|------|
| `main` | 항상 동작하는 상태 유지 (직접 커밋 금지) |
| `feat/이슈번호-설명` | 기능 개발 |
| `fix/이슈번호-설명` | 버그 수정 |

PR 머지 전 최소 1명 리뷰 필요합니다.
