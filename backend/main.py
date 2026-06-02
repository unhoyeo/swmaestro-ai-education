from fastapi import FastAPI, UploadFile, File, Form
from services.extractor import extract_text, split_clauses
from services.analyzer import analyze_clauses
from services.classifier import classify_risk
from services.summarizer import summarize

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), contract_type: str = Form(...)):
    file_bytes = await file.read()
    text = extract_text(file_bytes, file.filename)
    clauses = split_clauses(text)
    analysis = analyze_clauses(clauses, contract_type)
    classified = classify_risk(analysis)
    summary = summarize(classified)
    return {
        "contract_type": contract_type,
        "clauses": classified,
        "summary": summary,
    }
