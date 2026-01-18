# interview/resume_parser.py

"""
RESPONSIBILITY:
- Convert PDF → TEXT
- Clean text
- Extract skills, projects, experience using NLP + rules
NO AI, NO LLM, NO CLOUD
"""

import re
from typing import Dict, List
from pdfminer.high_level import extract_text
import spacy

# Load lightweight NLP model
nlp = spacy.load("en_core_web_sm")


# ---------------------------
# PDF → TEXT
# ---------------------------

def pdf_to_text(pdf_path: str) -> str:
    """
    Extract text from a normal (non-scanned) PDF resume.
    """
    try:
        text = extract_text(pdf_path)
        return clean_text(text)
    except Exception as e:
        print("PDF extraction failed:", e)
        return ""


def clean_text(text: str) -> str:
    """
    Normalize whitespace and remove junk characters.
    """
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------
# NLP + RULE-BASED EXTRACTION
# ---------------------------

SKILL_KEYWORDS = {
    "python", "java", "javascript", "c++", "c",
    "fastapi", "django", "flask",
    "sql", "mysql", "postgresql", "mongodb",
    "docker", "kubernetes", "linux",
    "git", "github",
    "machine learning", "deep learning", "ai",
    "react", "node", "express"
}

SECTION_HEADERS = {
    "projects": ["project", "projects"],
    "experience": ["experience", "work experience", "internship", "intern"],
    "skills": ["skills", "technical skills"]
}


def parse_resume(resume_text: str) -> Dict[str, List[str]]:
    """
    Convert raw resume text into structured data.
    """

    doc = nlp(resume_text.lower())

    skills = extract_skills(doc)
    projects = extract_section(resume_text, "projects")
    experience = extract_section(resume_text, "experience")

    return {
        "skills": skills[:6],
        "projects": projects[:3],
        "experience": experience[:3]
    }


# ---------------------------
# HELPERS
# ---------------------------

def extract_skills(doc) -> List[str]:
    """
    NLP token-based skill extraction.
    """
    found = set()

    for token in doc:
        if token.text in SKILL_KEYWORDS:
            found.add(token.text)

    # multi-word skills (ML, deep learning)
    text = doc.text
    for skill in SKILL_KEYWORDS:
        if " " in skill and skill in text:
            found.add(skill)

    return sorted(found)


def extract_section(text: str, section_name: str) -> List[str]:
    """
    Extract bullet / sentence lines under a section header.
    """
    lines = text.splitlines()
    section_lines = []

    headers = SECTION_HEADERS.get(section_name, [])
    capture = False

    for line in lines:
        line_clean = line.strip()

        if not line_clean:
            continue

        # Check if this line is a section header
        if any(h in line_clean.lower() for h in headers):
            capture = True
            continue

        # Stop if we hit another section
        if capture and is_new_section(line_clean):
            break

        if capture:
            section_lines.append(line_clean)

    return section_lines


def is_new_section(line: str) -> bool:
    """
    Heuristic: new section headers are usually short & uppercase-ish
    """
    if len(line) < 25 and line.isupper():
        return True
    return False
