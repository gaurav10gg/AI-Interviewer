# evaluation/llm_eval.py

"""
LLM EVALUATION USING OLLAMA (LOCAL)
STRICT JSON OUTPUT
"""

import json
import requests
from typing import Dict

from backend.config import OLLAMA_URL, OLLAMA_MODEL


def evaluate_with_llm(transcript: str, rules: dict) -> dict:
    """
    Evaluates the user's answer using local LLM.
    RULES are injected to guide evaluation.
    """

    # Check for empty or very short answers
    if rules.get("empty_answer"):
        return {
            "score": 0,
            "clarity": "low",
            "depth": "low",
            "feedback": "No answer provided. Please speak your response."
        }
    
    if rules.get("too_short"):
        return {
            "score": 2,
            "clarity": "low",
            "depth": "low",
            "feedback": "Answer is too brief. Please provide more detail and explanation."
        }

    prompt = f"""You are a strict technical interviewer evaluating a candidate's answer.

Candidate's Answer:
\"\"\"{transcript}\"\"\"

Analysis:
- Word count: {rules.get('word_count', 0)}
- Too long: {rules.get('too_long', False)}
- Has structure: {rules.get('has_structure', False)}

Evaluate this answer and return ONLY valid JSON in this EXACT format (no other text):
{{
  "score": <number 0-10>,
  "clarity": "<low/medium/high>",
  "depth": "<low/medium/high>",
  "feedback": "<2-3 sentence constructive feedback>"
}}"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 300
                }
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"Ollama API error: {response.status_code}")
            return fallback_evaluation(transcript, rules)

        raw = response.json().get("response", "")

        # Defensive JSON extraction
        # Find JSON object in response
        start = raw.find("{")
        end = raw.rfind("}") + 1

        if start == -1 or end == 0:
            print(f"No JSON found in response: {raw[:200]}")
            return fallback_evaluation(transcript, rules)

        json_str = raw[start:end]
        result = json.loads(json_str)

        # Validate required fields
        required_fields = ["score", "clarity", "depth", "feedback"]
        if not all(field in result for field in required_fields):
            print(f"Missing required fields in LLM response")
            return fallback_evaluation(transcript, rules)

        # Validate field types and values
        if not isinstance(result["score"], (int, float)) or not (0 <= result["score"] <= 10):
            result["score"] = 5
        
        if result["clarity"] not in ["low", "medium", "high"]:
            result["clarity"] = "medium"
        
        if result["depth"] not in ["low", "medium", "high"]:
            result["depth"] = "medium"

        return result

    except requests.exceptions.Timeout:
        print("Ollama request timeout")
        return fallback_evaluation(transcript, rules)
    
    except requests.exceptions.ConnectionError:
        print("Cannot connect to Ollama. Is it running?")
        return {
            "score": 5,
            "clarity": "medium",
            "depth": "medium",
            "feedback": "Evaluation service unavailable. Please ensure Ollama is running with: ollama serve"
        }
    
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return fallback_evaluation(transcript, rules)
    
    except Exception as e:
        print(f"LLM evaluation error: {e}")
        return fallback_evaluation(transcript, rules)


def fallback_evaluation(transcript: str, rules: Dict) -> dict:
    """
    Simple rule-based fallback when LLM fails
    """
    word_count = rules.get("word_count", 0)
    
    if word_count < 20:
        score = 2
        clarity = "low"
        depth = "low"
        feedback = "Very brief answer. Provide more details and examples."
    elif word_count < 50:
        score = 4
        clarity = "medium"
        depth = "low"
        feedback = "Good start, but expand on your answer with more context."
    elif word_count > 500:
        score = 6
        clarity = "medium"
        depth = "high"
        feedback = "Very detailed answer. Try to be more concise while maintaining key points."
    else:
        score = 7
        clarity = "medium"
        depth = "medium"
        feedback = "Reasonable answer. Consider adding specific examples to strengthen your response."
    
    return {
        "score": score,
        "clarity": clarity,
        "depth": depth,
        "feedback": feedback
    }