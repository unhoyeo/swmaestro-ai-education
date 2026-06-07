import re
import httpx
import os


def preprocess_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("cp949", errors="ignore")
        return preprocess_text(text)

    api_key = os.getenv("UPSTAGE_API_KEY")
    url = "https://api.upstage.ai/v1/document-ai/document-parse"

    response = httpx.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        files={"document": (filename, file_bytes)},
        data={"output_formats": '["text"]'},
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    content_text = data.get("content", {}).get("text", "")
    if content_text:
        return preprocess_text(content_text)

    pages = data.get("pages", [])
    extracted_texts = []
    for page in pages:
        page_text = page.get("text", "") or page.get("markdown", "")
        if page_text:
            extracted_texts.append(page_text)

    if not extracted_texts:
        for element in data.get("elements", []):
            element_text = element.get("text", "") or element.get("content", {}).get("text", "")
            if element_text:
                extracted_texts.append(element_text)

    combined_text = "\n".join(extracted_texts)
    return preprocess_text(combined_text)


def split_clauses(text: str) -> list[str]:
    pattern = r"(?=제\s*\d+\s*조|^\s*\d+\.\s|^\s*\(\d+\)\s)"
    parts = re.split(pattern, text, flags=re.MULTILINE)

    clauses = []
    for part in parts:
        cleaned = part.strip()
        if not re.match(r"^(제\s*\d+\s*조|\d+\.\s|\(\d+\)\s)", cleaned):
            continue
        if len(cleaned) >= 30:
            clauses.append(cleaned)

    return clauses[:20]
