from docx import Document
from io import BytesIO

class DocxReadError(ValueError):
    """Custom error for DOCX parsing issues."""
    pass

def read_docx_bytes(data: bytes) -> str:
    """
    Read .docx text from raw bytes and return as a single string.
    Raises DocxReadError on invalid/empty input.
    """
    if not data or len(data) < 10:
        raise DocxReadError("Empty or invalid DOCX content.")
    try:
        doc = Document(BytesIO(data))
    except Exception as e:
        raise DocxReadError(f"Failed to read DOCX: {e}") from e

    lines = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    text = "\n".join(lines).strip()
    if not text:
        raise DocxReadError("DOCX has no readable text.")
    return text
