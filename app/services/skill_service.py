def extract_skills(text: str):
    """
    Extract basic technical skills using keyword lookup.
    Later this can be replaced with an LLM node.
    """
    common_skills = [
        "python", "java", "spring", "docker", "kubernetes", "sql",
        "fastapi", "flask", "react", "javascript", "git", "linux",
        "aws", "azure", "pandas", "tensorflow", "node", "html", "css"
    ]
    text_lower = text.lower()
    return [skill for skill in common_skills if skill in text_lower]


def compute_fit_score(resume_skills, job_skills):
    """Compute skill match percentage and return matched skills."""
    if not job_skills:
        return {"fit_score": 0, "matched_skills": []}
    matched = [s for s in resume_skills if s in job_skills]
    score = (len(matched) / len(job_skills)) * 100
    return {"fit_score": round(score, 2), "matched_skills": matched}
