import os
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

class SkillGraphState(TypedDict):
    text: str
    job_skills: List[str]

def extract_skills(state: SkillGraphState):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

    prompt = (
        "Extract a concise list of key professional skills mentioned in this text. "
        "Return them as a comma-separated list only, no explanations.\n\n"
        f"TEXT:\n{state['text']}"
    )

    response = model.invoke(prompt)
    skills = [s.strip() for s in response.content.split(",") if s.strip()]
    return {"job_skills": skills}

def build_skill_graph():
    graph = StateGraph(SkillGraphState)
    graph.add_node("extract_skills", extract_skills)
    graph.set_entry_point("extract_skills")
    graph.add_edge("extract_skills", END)
    return graph.compile()
