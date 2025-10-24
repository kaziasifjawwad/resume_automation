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
    """Extract skills from job description text using intelligent AI analysis."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

        prompt = f"""
You are an expert technical recruiter analyzing a job description. Extract ALL required technical and professional skills.

JOB DESCRIPTION:
{state['text']}

Instructions:
1. Extract technical skills, programming languages, frameworks, tools, databases, cloud platforms, methodologies
2. Include both explicitly mentioned skills and skills implied by requirements
3. Standardize skill names (e.g., "JS" → "JavaScript", "ML" → "Machine Learning", "AWS" → "Amazon Web Services")
4. Include soft skills and experience requirements
5. Consider experience levels and years mentioned
6. Be comprehensive but avoid duplicates
7. Focus on skills that are essential for the role

Return ONLY a comma-separated list of skills, no explanations or formatting.
Example: Python, FastAPI, PostgreSQL, Docker, AWS, Git, Agile, Team Leadership
"""

        response = model.invoke(prompt)
        skills = [s.strip() for s in response.content.split(",") if s.strip()]
        
        # Clean and deduplicate skills
        cleaned_skills = []
        seen = set()
        for skill in skills:
            skill_clean = skill.strip().title()
            if skill_clean and skill_clean not in seen:
                cleaned_skills.append(skill_clean)
                seen.add(skill_clean)
        
        logger.info(f"Extracted {len(cleaned_skills)} job skills: {', '.join(cleaned_skills[:10])}{'...' if len(cleaned_skills) > 10 else ''}")
        return {"job_skills": cleaned_skills}
    
    except Exception as e:
        logger.error(f"OpenAI API failed for job skill extraction: {e}")
        # Fallback: basic keyword extraction
        skills = extract_skills_fallback(state['text'])
        logger.info(f"Using fallback job skill extraction: {len(skills)} skills")
        return {"job_skills": skills}

def extract_resume_skills(state: ResumeEvaluationState):
    """Extract skills from resume text using intelligent AI analysis."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

    try:
        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)

        prompt = f"""
You are an expert technical recruiter analyzing a resume. Extract ALL relevant technical and professional skills.

RESUME TEXT:
{state['resume_text']}

Instructions:
1. Extract technical skills, programming languages, frameworks, tools, databases, cloud platforms, methodologies
2. Include both explicit skills and skills implied by experience (e.g., if someone worked with "React projects", include "React")
3. Standardize skill names (e.g., "JS" → "JavaScript", "ML" → "Machine Learning", "AWS" → "Amazon Web Services")
4. Include soft skills that are relevant to technical roles
5. Consider experience levels and years mentioned
6. Be comprehensive but avoid duplicates

Return ONLY a comma-separated list of skills, no explanations or formatting.
Example: Python, JavaScript, React, PostgreSQL, Docker, AWS, Git, Agile, Team Leadership
"""

        response = model.invoke(prompt)
        skills = [s.strip() for s in response.content.split(",") if s.strip()]
        
        # Clean and deduplicate skills
        cleaned_skills = []
        seen = set()
        for skill in skills:
            skill_clean = skill.strip().title()
            if skill_clean and skill_clean not in seen:
                cleaned_skills.append(skill_clean)
                seen.add(skill_clean)
        
        logger.info(f"Extracted {len(cleaned_skills)} resume skills: {', '.join(cleaned_skills[:10])}{'...' if len(cleaned_skills) > 10 else ''}")
        return {"resume_skills": cleaned_skills}
    
    except Exception as e:
        logger.error(f"OpenAI API failed for resume skill extraction: {e}")
        # Fallback: basic keyword extraction
        skills = extract_skills_fallback(state['resume_text'])
        logger.info(f"Using fallback resume skill extraction: {len(skills)} skills")
        return {"resume_skills": skills}

def match_and_score(state: ResumeEvaluationState):
    """Intelligently compare resume skills against job skills using OpenAI."""
    job_skills = state['job_skills']
    resume_skills = state['resume_skills']
    
    if not job_skills:
        logger.info("No job skills provided, returning 0 fit score")
        return {"fit_score": 0.0}
    
    if not resume_skills:
        logger.info("No resume skills provided, returning 0 fit score")
        return {"fit_score": 0.0}
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Missing OPENAI_API_KEY environment variable")
        return {"fit_score": 0.0}
    
    try:
        model = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key)
        
        # Create a detailed prompt for intelligent skill matching
        prompt = f"""
You are an expert HR analyst tasked with evaluating how well a candidate's skills match job requirements.

JOB SKILLS REQUIRED:
{', '.join(job_skills)}

CANDIDATE SKILLS:
{', '.join(resume_skills)}

Your task:
1. For each job skill, determine if the candidate has a matching or equivalent skill
2. Consider variations, synonyms, and related technologies (e.g., "React" matches "ReactJS", "JavaScript" matches "JS", "Python" matches "Python3")
3. Consider skill levels and experience (e.g., "Machine Learning" matches "ML", "Data Science", "AI")
4. Be intelligent about technology stacks (e.g., "Frontend Development" matches "React", "Vue", "Angular")

Provide your analysis in this exact JSON format:
{{
    "matched_skills": [
        {{
            "job_skill": "skill name",
            "resume_skill": "matching skill name",
            "match_confidence": 0.95,
            "match_type": "exact|synonym|related|equivalent"
        }}
    ],
    "unmatched_job_skills": ["skill1", "skill2"],
    "overall_fit_score": 0.85,
    "reasoning": "Brief explanation of the matching logic"
}}

Return ONLY the JSON, no other text.
"""

        response = model.invoke(prompt)
        
        # Parse the JSON response
        import json
        try:
            result = json.loads(response.content.strip())
            
            matched_skills = result.get('matched_skills', [])
            unmatched_skills = result.get('unmatched_job_skills', [])
            fit_score = result.get('overall_fit_score', 0.0)
            reasoning = result.get('reasoning', '')
            
            # Validate fit score is between 0 and 1
            fit_score = max(0.0, min(1.0, float(fit_score)))
            
            logger.info(f"AI-powered fit score: {fit_score:.3f}")
            logger.info(f"Matched {len(matched_skills)}/{len(job_skills)} job skills")
            logger.info(f"Reasoning: {reasoning}")
            
            # Log detailed matching results
            for match in matched_skills:
                logger.info(f"  ✓ {match['job_skill']} → {match['resume_skill']} ({match['match_type']}, confidence: {match['match_confidence']})")
            
            for unmatched in unmatched_skills:
                logger.info(f"  ✗ {unmatched} (no match found)")
            
            return {"fit_score": fit_score}
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response.content}")
            # Fallback to basic matching
            return fallback_skill_matching(job_skills, resume_skills)
    
    except Exception as e:
        logger.error(f"OpenAI API failed for skill matching: {e}")
        # Fallback to basic matching
        return fallback_skill_matching(job_skills, resume_skills)


def fallback_skill_matching(job_skills, resume_skills):
    """Fallback skill matching using fuzzy string matching."""
    from difflib import SequenceMatcher
    
    job_skills_lower = [skill.lower().strip() for skill in job_skills]
    resume_skills_lower = [skill.lower().strip() for skill in resume_skills]
    
    matched_count = 0
    total_job_skills = len(job_skills)
    
    for job_skill in job_skills_lower:
        best_match_score = 0
        best_match = None
        
        for resume_skill in resume_skills_lower:
            # Calculate similarity score
            similarity = SequenceMatcher(None, job_skill, resume_skill).ratio()
            
            # Also check for partial matches (e.g., "python" in "python3")
            if job_skill in resume_skill or resume_skill in job_skill:
                similarity = max(similarity, 0.8)
            
            if similarity > best_match_score and similarity > 0.6:  # 60% similarity threshold
                best_match_score = similarity
                best_match = resume_skill
        
        if best_match:
            matched_count += 1
            logger.info(f"Fallback match: {job_skill} → {best_match} (score: {best_match_score:.2f})")
    
    fit_score = matched_count / total_job_skills if total_job_skills > 0 else 0.0
    logger.info(f"Fallback fit score: {fit_score:.3f} ({matched_count}/{total_job_skills} matched)")
    
    return {"fit_score": fit_score}

def extract_skills_fallback(text: str) -> List[str]:
    """
    Enhanced fallback skill extraction using comprehensive keyword matching.
    Used when OpenAI API fails.
    """
    # Comprehensive technical skills database
    skill_keywords = {
        # Programming Languages
        "python": "Python", "python3": "Python", "py": "Python",
        "java": "Java", "javascript": "JavaScript", "js": "JavaScript", "typescript": "TypeScript", "ts": "TypeScript",
        "c++": "C++", "cpp": "C++", "c#": "C#", "csharp": "C#",
        "php": "PHP", "ruby": "Ruby", "go": "Go", "golang": "Go", "rust": "Rust", "swift": "Swift",
        "kotlin": "Kotlin", "scala": "Scala", "r": "R", "matlab": "MATLAB",
        
        # Web Frameworks
        "react": "React", "reactjs": "React", "react.js": "React", "angular": "Angular", "vue": "Vue.js", "vuejs": "Vue.js",
        "node.js": "Node.js", "nodejs": "Node.js", "express": "Express.js", "next.js": "Next.js", "nuxt": "Nuxt.js",
        "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "spring": "Spring", "spring boot": "Spring Boot",
        "laravel": "Laravel", "rails": "Ruby on Rails", "asp.net": "ASP.NET", "dotnet": ".NET",
        
        # Databases
        "sql": "SQL", "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "mysql": "MySQL", "mariadb": "MariaDB",
        "mongodb": "MongoDB", "mongo": "MongoDB", "redis": "Redis", "elasticsearch": "Elasticsearch",
        "oracle": "Oracle", "sqlite": "SQLite", "cassandra": "Cassandra", "dynamodb": "DynamoDB",
        
        # Cloud & DevOps
        "aws": "Amazon Web Services", "amazon web services": "Amazon Web Services", "azure": "Microsoft Azure",
        "gcp": "Google Cloud Platform", "google cloud": "Google Cloud Platform", "docker": "Docker",
        "kubernetes": "Kubernetes", "k8s": "Kubernetes", "jenkins": "Jenkins", "gitlab": "GitLab",
        "github": "GitHub", "git": "Git", "terraform": "Terraform", "ansible": "Ansible",
        "ci/cd": "CI/CD", "continuous integration": "CI/CD", "continuous deployment": "CI/CD",
        
        # Data Science & AI
        "machine learning": "Machine Learning", "ml": "Machine Learning", "artificial intelligence": "AI", "ai": "AI",
        "data science": "Data Science", "deep learning": "Deep Learning", "neural networks": "Neural Networks",
        "pandas": "Pandas", "numpy": "NumPy", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
        "scikit-learn": "Scikit-learn", "keras": "Keras", "opencv": "OpenCV", "jupyter": "Jupyter",
        
        # Tools & Technologies
        "html": "HTML", "css": "CSS", "sass": "Sass", "scss": "Sass", "bootstrap": "Bootstrap",
        "webpack": "Webpack", "babel": "Babel", "npm": "npm", "yarn": "Yarn", "pip": "pip",
        "linux": "Linux", "ubuntu": "Ubuntu", "centos": "CentOS", "bash": "Bash", "powershell": "PowerShell",
        "vim": "Vim", "emacs": "Emacs", "sublime": "Sublime Text", "vscode": "Visual Studio Code",
        "intellij": "IntelliJ IDEA", "eclipse": "Eclipse", "android studio": "Android Studio",
        
        # Methodologies
        "agile": "Agile", "scrum": "Scrum", "kanban": "Kanban", "devops": "DevOps",
        "microservices": "Microservices", "rest api": "REST API", "graphql": "GraphQL",
        "soap": "SOAP", "json": "JSON", "xml": "XML", "yaml": "YAML",
        
        # Soft Skills
        "leadership": "Leadership", "team management": "Team Management", "project management": "Project Management",
        "communication": "Communication", "problem solving": "Problem Solving", "analytical": "Analytical Skills",
        "collaboration": "Collaboration", "mentoring": "Mentoring", "training": "Training"
    }
    
    text_lower = text.lower()
    found_skills = []
    seen_skills = set()
    
    # Check for exact matches and variations
    for keyword, skill_name in skill_keywords.items():
        if keyword in text_lower and skill_name not in seen_skills:
            found_skills.append(skill_name)
            seen_skills.add(skill_name)
    
    # Additional pattern matching for common variations
    import re
    
    # Look for version numbers (e.g., "Python 3.8", "React 18")
    version_patterns = [
        (r'python\s*3?\.?\d*', "Python"),
        (r'javascript\s*es\d*', "JavaScript"),
        (r'react\s*\d*', "React"),
        (r'node\s*\.?\s*js\s*\d*', "Node.js"),
        (r'angular\s*\d*', "Angular"),
        (r'vue\s*\d*', "Vue.js"),
    ]
    
    for pattern, skill_name in version_patterns:
        if re.search(pattern, text_lower) and skill_name not in seen_skills:
            found_skills.append(skill_name)
            seen_skills.add(skill_name)
    
    # Look for common abbreviations and their expansions
    abbreviations = {
        "api": "API", "ui": "UI", "ux": "UX", "db": "Database", "dbms": "Database Management System",
        "os": "Operating System", "gui": "GUI", "cli": "CLI", "ide": "IDE", "sdk": "SDK",
        "http": "HTTP", "https": "HTTPS", "tcp": "TCP", "udp": "UDP", "dns": "DNS",
        "ssl": "SSL", "tls": "TLS", "oauth": "OAuth", "jwt": "JWT", "cors": "CORS"
    }
    
    for abbr, expansion in abbreviations.items():
        if abbr in text_lower and expansion not in seen_skills:
            found_skills.append(expansion)
            seen_skills.add(expansion)
    
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
