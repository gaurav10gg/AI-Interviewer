# evaluation/rules.py

"""
RULE-BASED EVALUATION
Runs BEFORE LLM.
Deterministic and fast.
"""

def run_rules(transcript: str) -> dict:
    words = transcript.strip().split()

    word_count = len(words)

    return {
        "word_count": word_count,
        "empty_answer": word_count == 0,
        "too_short": word_count < 20,
        "too_long": word_count > 500,
        "has_structure": word_count >= 40
    }
