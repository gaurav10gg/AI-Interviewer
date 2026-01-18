# evaluation/llm_eval.py

"""
LLM EVALUATION USING OLLAMA (LOCAL)
STRICT JSON OUTPUT
"""

import json
import requests

from backend.config import OLLAMA_URL, OLLAMA_MODEL


def evaluate_with_llm(transcript: str, rules: dict) -> dict:
    """
    Evaluates the user's answer using local LLM.
    RULES are injected to guide evaluation.
    """

    prompt = f"""
You are a strict technical interviewer.

Evaluate the candidate's answer below.

Answer:
\"\"\"{transcript}\"\"\"

Rule signals:
{rules}

Return ONLY valid JSON in this exact format:
{{
  "score": 0-10,
  "clarity": "low|medium|high",
  "depth": "low|medium|high",
  "feedback": "short constructive feedback"
}}

Do not add any extra text.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        raw = response.json().get("response", "")

        # Defensive JSON extraction
        start = raw.find("{")
        end = raw.rfind("}") + 1

        return json.loads(raw[start:end])

    except Exception as e:
        print("LLM evaluation failed:", e)
        return {
            "score": 0,
            "clarity": "low",
            "depth": "low",
            "feedback": "Evaluation failed"
        }
