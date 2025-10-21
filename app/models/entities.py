from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, ARRAY, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    description = Column(String, nullable=True)       # <-- add this
    extracted_skills = Column(ARRAY(String), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    resumes = relationship("Resume", back_populates="job")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"))
    file_path = Column(String, nullable=False)
    extracted_skills = Column(ARRAY(String), nullable=True)
    fit_score = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    job = relationship("JobDescription", back_populates="resumes")
