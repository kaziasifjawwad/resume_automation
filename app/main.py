from fastapi import FastAPI

from app.api import job_routes

app = FastAPI(
    title="LangGraph Skill Matcher API",
    description="A simple workflow that compares resume vs job requirements using LangGraph.",
    version="0.1"
)

app.include_router(job_routes.router)