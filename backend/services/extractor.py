import re
import httpx
import os


def extract_text(file_bytes: bytes, filename: str) -> str:
    api_key = os.getenv("UPSTAGE_API_KEY")
    response = httpx.post(
        "https://api.upstage.ai/v1/document-digitization",
        headers={"Authorization": f"Bearer {api_key}"},
        files={"document": (filename, file_bytes)},
        data={"output_formats": '["text"]'},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["content"]["text"]


def split_clauses(text: str) -> list[str]:
    pattern = r"(?=제\s*\d+\s*조|^\d+\.\s|^\(\d+\)\s)"
    parts = re.split(pattern, text, flags=re.MULTILINE)
    return [p.strip() for p in parts if len(p.strip()) >= 30][:20]
