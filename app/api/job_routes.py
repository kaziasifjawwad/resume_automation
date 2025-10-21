from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.models.schemas import JobCreate, JobResponse
from app.services.job_service import (
    process_and_store_job, create_job, get_all_jobs, get_job_by_id, delete_job
)


router = APIRouter(prefix="/jobs", tags=["Job Descriptions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
def upload_job(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")

    job = process_and_store_job(file, db)
    return {
        "id": job.id,
        "title": job.title,
        "file_path": job.file_path,
        "extracted_skills": job.extracted_skills,
        "created_at": job.created_at,
    }


@router.post("/create", response_model=JobResponse)
def create_job_post(payload: JobCreate, db: Session = Depends(get_db)):
    """Create a job by title + description (no file)."""
    if not payload.description:
        raise HTTPException(status_code=400, detail="Description is required.")
    job = create_job(payload.title, payload.description, db)
    return job


@router.get("/", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    """List all job posts."""
    return get_all_jobs(db)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a job post by ID."""
    job = get_job_by_id(job_id, db)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@router.delete("/{job_id}")
def remove_job(job_id: int, db: Session = Depends(get_db)):
    """Delete a job post."""
    deleted = delete_job(job_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {"message": f"Job {job_id} deleted successfully."}
