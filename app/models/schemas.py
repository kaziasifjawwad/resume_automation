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
        orm_mode = True
