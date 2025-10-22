from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import SessionLocal
from app.models.schemas import ResumeResponse, ResumeListItem, TopResumeResponse
from app.services.resume_service import (
    process_resume, get_resumes_by_job, get_top_resumes, get_resume_by_id
)

router = APIRouter(prefix="/resumes", tags=["Resume Management"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=ResumeResponse)
def upload_resume(
    job_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a resume file for a specific job.
    
    - **job_id**: ID of the job this resume is for
    - **file**: Resume file (.docx format)
    
    Returns the processed resume with extracted skills and fit score.
    """
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    try:
        resume = process_resume(file, job_id, db)
        return resume
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


@router.get("/jobs/{job_id}", response_model=List[ResumeListItem])
def get_job_resumes(job_id: int, db: Session = Depends(get_db)):
    """
    Get all resumes for a specific job, sorted by fit score (highest first).
    
    - **job_id**: ID of the job to get resumes for
    
    Returns a list of resumes sorted by fit score in descending order.
    """
    try:
        resumes = get_resumes_by_job(job_id, db)
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resumes: {str(e)}")


@router.get("/top", response_model=List[TopResumeResponse])
def get_top_resumes_endpoint(
    job_id: int = Query(..., description="Job ID to get top resumes for"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of resumes to return"),
    db: Session = Depends(get_db)
):
    """
    Get the top N resumes with highest fit scores for a specific job.
    
    - **job_id**: ID of the job to get top resumes for
    - **limit**: Maximum number of resumes to return (1-100, default: 10)
    
    Returns the top N resumes sorted by fit score in descending order.
    """
    try:
        resumes = get_top_resumes(job_id, limit, db)
        return resumes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve top resumes: {str(e)}")


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Get a specific resume by ID.
    
    - **resume_id**: ID of the resume to retrieve
    
    Returns the complete resume details including extracted skills and fit score.
    """
    try:
        resume = get_resume_by_id(resume_id, db)
        return resume
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resume: {str(e)}")
