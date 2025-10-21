import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.entities import JobDescription
from app.utils.docx_reader import read_docx_bytes
from app.graph.skill_graph import build_skill_graph

UPLOAD_DIR = "uploads/jobs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_job_doc(file: UploadFile) -> str:
    """Save uploaded job description .docx to disk and return file path (not stored in DB)."""
    filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path


def process_and_store_job(file: UploadFile, db: Session):
    """
    Upload .docx → read text → extract skills via LangGraph → save JobDescription.
    We DO NOT store file_path in DB per schema; only title/description/extracted_skills.
    """
    file_path = save_job_doc(file)  # we still keep a copy on disk for auditing if needed
    text = read_docx_bytes(open(file_path, "rb").read())

    graph = build_skill_graph()
    result = graph.invoke({"text": text})

    job = JobDescription(
        title=file.filename,
        description=text,
        extracted_skills=result.get("job_skills", []),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def create_job(title: str, description: str, db: Session):
    """
    Create a job post from raw text → extract skills via LangGraph → save.
    No file_path field in DB.
    """
    graph = build_skill_graph()
    result = graph.invoke({"text": description})

    job = JobDescription(
        title=title,
        description=description,
        extracted_skills=result.get("job_skills", []),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_all_jobs(db: Session):
    return db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()


def get_job_by_id(job_id: int, db: Session):
    return db.query(JobDescription).filter(JobDescription.id == job_id).first()


def delete_job(job_id: int, db: Session):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if job:
        db.delete(job)
        db.commit()
        return True
    return False
