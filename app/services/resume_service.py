import os
import logging
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.entities import Resume, JobDescription
from app.utils.docx_reader import read_docx_bytes, DocxReadError
from app.graph.skill_graph import build_resume_evaluation_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_resume_file(file: UploadFile) -> str:
    """Save uploaded resume .docx to disk and return file path."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds for uniqueness
    filename = f"{timestamp}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(path, "wb") as f:
            f.write(file.file.read())
        logger.info(f"Resume file saved: {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to save resume file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save resume file")


def process_resume(file: UploadFile, job_id: int, db: Session) -> Resume:
    """
    Process uploaded resume:
    1. Save file to disk
    2. Read DOCX content
    3. Fetch target job from database
    4. Extract skills and compute fit score via LangGraph
    5. Persist resume record
    """
    try:
        # Step 1: Save file
        file_path = save_resume_file(file)
        
        # Step 2: Read DOCX content
        try:
            resume_text = read_docx_bytes(open(file_path, "rb").read())
            logger.info(f"Successfully read resume content, length: {len(resume_text)}")
        except DocxReadError as e:
            logger.error(f"Failed to read DOCX: {e}")
            # Clean up saved file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Invalid DOCX file: {e}")
        
        # Step 3: Fetch target job
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            # Clean up saved file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.extracted_skills:
            logger.warning(f"Job {job_id} has no extracted skills")
            job_skills = []
        else:
            job_skills = job.extracted_skills
        
        # Step 4: Process via LangGraph workflow
        try:
            graph = build_resume_evaluation_graph()
            result = graph.invoke({
                "resume_text": resume_text,
                "job_skills": job_skills
            })
            
            extracted_skills = result.get("resume_skills", [])
            fit_score = result.get("fit_score", 0.0)
            
            logger.info(f"Resume processing completed - Skills: {len(extracted_skills)}, Fit Score: {fit_score}")
            
        except Exception as e:
            logger.error(f"LangGraph processing failed: {e}")
            # Fallback: basic skill extraction without scoring
            extracted_skills = extract_skills_fallback(resume_text)
            fit_score = 0.0
            logger.info(f"Using fallback skill extraction: {len(extracted_skills)} skills")
        
        # Step 5: Persist resume record
        resume = Resume(
            job_id=job_id,
            file_path=file_path,
            extracted_skills=extracted_skills,
            fit_score=fit_score
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        logger.info(f"Resume record created with ID: {resume.id}")
        return resume
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing resume: {e}")
        # Clean up saved file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Internal server error processing resume")


def extract_skills_fallback(resume_text: str) -> list[str]:
    """
    Fallback skill extraction using simple keyword matching.
    Used when OpenAI API fails.
    """
    # Common technical skills keywords
    skill_keywords = [
        "python", "java", "javascript", "react", "angular", "vue", "node.js",
        "sql", "postgresql", "mysql", "mongodb", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "git", "github", "gitlab", "jenkins", "ci/cd",
        "machine learning", "ai", "data science", "pandas", "numpy", "tensorflow",
        "pytorch", "scikit-learn", "fastapi", "django", "flask", "express",
        "spring", "hibernate", "rest api", "graphql", "microservices",
        "agile", "scrum", "devops", "linux", "bash", "powershell"
    ]
    
    text_lower = resume_text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return found_skills


def get_resumes_by_job(job_id: int, db: Session) -> list[Resume]:
    """Get all resumes for a specific job, sorted by fit_score descending."""
    return db.query(Resume).filter(Resume.job_id == job_id).order_by(Resume.fit_score.desc()).all()


def get_top_resumes(job_id: int, limit: int, db: Session) -> list[Resume]:
    """Get top N resumes with highest fit score for a given job."""
    return db.query(Resume).filter(Resume.job_id == job_id).order_by(Resume.fit_score.desc()).limit(limit).all()


def get_resume_by_id(resume_id: int, db: Session) -> Resume:
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
