import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.entities import JobDescription
from app.utils.docx_reader import read_docx_bytes
from app.graph.skill_graph import build_skill_graph

UPLOAD_DIR = "uploads/jobs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --------------------------------------------------------------------------
# Save uploaded DOCX file
# --------------------------------------------------------------------------
def save_job_doc(file: UploadFile) -> str:
    """Save uploaded job description .docx to disk and return file path."""
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


# --------------------------------------------------------------------------
# Upload .docx → Extract skills using LangGraph → Save to DB
# --------------------------------------------------------------------------
def process_and_store_job(file: UploadFile, db: Session):
    """Extract text and skills via LangGraph when a DOCX is uploaded."""
    file_path = save_job_doc(file)
    text = read_docx_bytes(open(file_path, "rb").read())

    # Build and run LangGraph pipeline
    graph = build_skill_graph()
    result = graph.invoke({"resume_text": text, "job_text": text})

    job = JobDescription(
        title=file.filename,
        file_path=file_path,
        extracted_skills=result.get("job_skills", []),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# --------------------------------------------------------------------------
# Create a job post manually (no LangGraph call here)
# --------------------------------------------------------------------------
def create_job(title: str, description: str, db: Session):
    """Create a new job post with basic info only (no file upload)."""
    job = JobDescription(
        title=title,
        description=description,   # <-- save it
        file_path=None,
        extracted_skills=None,     # skills will be computed later if/when needed
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


# --------------------------------------------------------------------------
# CRUD helpers
# --------------------------------------------------------------------------
def get_all_jobs(db: Session):
    """Fetch all jobs (latest first)."""
    return db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()


def get_job_by_id(job_id: int, db: Session):
    """Fetch a job by ID."""
    return db.query(JobDescription).filter(JobDescription.id == job_id).first()


def delete_job(job_id: int, db: Session):
    """Delete a job post by ID."""
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if job:
        db.delete(job)
        db.commit()
        return True
    return False
