# interview/question_generator.py

"""
RESPONSIBILITY:
- Convert parsed resume data into interview questions
- Rule-based, deterministic
- NO LLM
"""

from typing import List, Dict


def generate_questions(parsed_resume: Dict) -> List[str]:
    """
    Generate interview questions from parsed resume.
    """

    questions: List[str] = []

    # ------------------------
    # 1. PROJECT QUESTIONS
    # ------------------------
    projects = parsed_resume.get("projects", [])
    for project in projects:
        questions.extend(generate_project_questions(project))

    # ------------------------
    # 2. SKILL QUESTIONS
    # ------------------------
    skills = parsed_resume.get("skills", [])
    for skill in skills:
        questions.extend(generate_skill_questions(skill))

    # ------------------------
    # 3. EXPERIENCE QUESTIONS
    # ------------------------
    experience = parsed_resume.get("experience", [])
    for exp in experience:
        questions.append(
            f"Can you describe your experience related to: {exp}?"
        )

    # ------------------------
    # 4. FALLBACK QUESTIONS
    # ------------------------
    if not questions:
        questions = [
            "Tell me about yourself.",
            "What are your strengths as an engineer?",
            "What kind of problems do you enjoy solving?"
        ]

    return questions


# =================================
# QUESTION BUILDERS
# =================================

def generate_project_questions(project: str) -> List[str]:
    """
    Generate a sequence of questions for a single project.
    """
    return [
        f"Can you explain this project in detail: {project}?",
        "What problem were you trying to solve in this project?",
        "What was your individual contribution to this project?",
        "What technical challenges did you face and how did you solve them?",
        "If you had more time, how would you improve this project?"
    ]


def generate_skill_questions(skill: str) -> List[str]:
    """
    Generate depth-based questions for a skill.
    """
    return [
        f"What is your experience with {skill}?",
        f"Can you explain a real-world scenario where you used {skill}?",
        f"What are some limitations or challenges you faced while using {skill}?"
    ]
