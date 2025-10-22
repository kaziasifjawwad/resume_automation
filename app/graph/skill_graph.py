import os
import logging
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillGraphState(TypedDict):
    text: str
    job_skills: List[str]

class ResumeEvaluationState(TypedDict):
    resume_text: str
    job_skills: List[str]
    resume_skills: List[str]
    fit_score: float

def extract_skills(state: SkillGraphState):
    """Extract skills from job description text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

        prompt = (
            "Extract a concise list of key professional skills mentioned in this text. "
            "Return them as a comma-separated list only, no explanations.\n\n"
            f"TEXT:\n{state['text']}"
        )

        response = model.invoke(prompt)
        skills = [s.strip() for s in response.content.split(",") if s.strip()]
        logger.info(f"Extracted {len(skills)} job skills")
        return {"job_skills": skills}
    
    except Exception as e:
        logger.error(f"OpenAI API failed for job skill extraction: {e}")
        # Fallback: basic keyword extraction
        skills = extract_skills_fallback(state['text'])
        logger.info(f"Using fallback job skill extraction: {len(skills)} skills")
        return {"job_skills": skills}

def extract_resume_skills(state: ResumeEvaluationState):
    """Extract skills from resume text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

        prompt = (
            "Extract a concise list of key professional skills mentioned in this resume. "
            "Focus on technical skills, programming languages, frameworks, tools, and methodologies. "
            "Return them as a comma-separated list only, no explanations.\n\n"
            f"RESUME TEXT:\n{state['resume_text']}"
        )

        response = model.invoke(prompt)
        skills = [s.strip() for s in response.content.split(",") if s.strip()]
        logger.info(f"Extracted {len(skills)} resume skills")
        return {"resume_skills": skills}
    
    except Exception as e:
        logger.error(f"OpenAI API failed for resume skill extraction: {e}")
        # Fallback: basic keyword extraction
        skills = extract_skills_fallback(state['resume_text'])
        logger.info(f"Using fallback resume skill extraction: {len(skills)} skills")
        return {"resume_skills": skills}

def match_and_score(state: ResumeEvaluationState):
    """Compare resume skills against job skills and compute fit score."""
    job_skills = set(skill.lower().strip() for skill in state['job_skills'])
    resume_skills = set(skill.lower().strip() for skill in state['resume_skills'])
    
    if not job_skills:
        # If no job skills, return 0 score
        fit_score = 0.0
    else:
        # Calculate Jaccard similarity
        intersection = job_skills.intersection(resume_skills)
        union = job_skills.union(resume_skills)
        
        if union:
            fit_score = len(intersection) / len(union)
        else:
            fit_score = 0.0
    
    logger.info(f"Fit score calculated: {fit_score:.3f} (matched {len(intersection)}/{len(job_skills)} job skills)")
    return {"fit_score": fit_score}

def extract_skills_fallback(text: str) -> List[str]:
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
        "agile", "scrum", "devops", "linux", "bash", "powershell", "html", "css",
        "typescript", "c++", "c#", ".net", "php", "ruby", "go", "rust", "swift",
        "kotlin", "android", "ios", "xcode", "android studio", "visual studio",
        "jupyter", "tableau", "power bi", "excel", "word", "powerpoint"
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return found_skills

def build_skill_graph():
    """Build the job skill extraction graph (existing functionality)."""
    graph = StateGraph(SkillGraphState)
    graph.add_node("extract_skills", extract_skills)
    graph.set_entry_point("extract_skills")
    graph.add_edge("extract_skills", END)
    return graph.compile()

def build_resume_evaluation_graph():
    """Build the resume evaluation graph for skill extraction and matching."""
    graph = StateGraph(ResumeEvaluationState)
    
    # Add nodes
    graph.add_node("extract_resume_skills", extract_resume_skills)
    graph.add_node("match_and_score", match_and_score)
    
    # Set entry point
    graph.set_entry_point("extract_resume_skills")
    
    # Add edges
    graph.add_edge("extract_resume_skills", "match_and_score")
    graph.add_edge("match_and_score", END)
    
    return graph.compile()
