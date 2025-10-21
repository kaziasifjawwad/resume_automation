from langgraph.graph import StateGraph, END


# --- Simple skill extractor using keyword heuristic for now ---
def extract_skills_node(state):
    text = (state.get("resume_text") or "") + " " + (state.get("job_text") or "")
    common_skills = [
        "python", "java", "spring", "fastapi", "docker",
        "postgresql", "mysql", "kubernetes", "react", "aws", "git"
    ]
    found = [s for s in common_skills if s.lower() in text.lower()]
    return {"job_skills": found, "resume_skills": found}


def compute_fit_score_node(state):
    job_skills = set(state.get("job_skills", []))
    resume_skills = set(state.get("resume_skills", []))
    if not job_skills:
        score = 0.0
    else:
        matched = len(job_skills & resume_skills)
        score = round((matched / len(job_skills)) * 100, 2)
    return {"fit_score": score}


def build_skill_graph():
    """Build and compile the LangGraph skill extraction + scoring graph."""
    workflow = StateGraph()

    # Define nodes
    workflow.add_node("extract_skills", extract_skills_node)
    workflow.add_node("compute_fit_score", compute_fit_score_node)

    # Define flow
    workflow.set_entry_point("extract_skills")
    workflow.add_edge("extract_skills", "compute_fit_score")
    workflow.add_edge("compute_fit_score", END)

    # Compile to runnable graph
    return workflow.compile()
