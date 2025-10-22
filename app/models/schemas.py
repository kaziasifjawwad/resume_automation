from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    description: Optional[str] = None

class JobResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    extracted_skills: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeResponse(BaseModel):
    """Detailed resume response including all fields."""
    id: int
    job_id: int
    file_path: str
    extracted_skills: Optional[List[str]]
    fit_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class ResumeListItem(BaseModel):
    """Summarized resume for listings."""
    id: int
    job_id: int
    file_path: str
    fit_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class TopResumeResponse(BaseModel):
    """Structured response for top-scoring resumes per job."""
    id: int
    job_id: int
    file_path: str
    extracted_skills: Optional[List[str]]
    fit_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
