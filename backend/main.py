from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from services.extractor import extract_text, split_clauses
from services.analyzer import analyze_clauses, detect_contract_type
from services.classifier import classify_risk
from services.summarizer import summarize
from services.explainer import explain

app = FastAPI()


class ExplainRequest(BaseModel):
    clause: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), contract_type: str = Form(...)):
    file_bytes = await file.read()
    text = extract_text(file_bytes, file.filename)
    detected_type = detect_contract_type(text) if contract_type == "자동 감지" else None
    resolved_type = detected_type or contract_type
    clauses = split_clauses(text)
    analysis = analyze_clauses(clauses, resolved_type)
    classified = classify_risk(analysis)
    summary = summarize(classified)
    return {
        "contract_type": resolved_type,
        "detected_type": detected_type,
        "clauses": classified,
        "summary": summary,
    }


@app.post("/explain")
def explain_clause(body: ExplainRequest):
    return {"explanation": explain(body.clause)}
