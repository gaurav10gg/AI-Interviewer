# backend/websocket.py

import json
from fastapi import WebSocket

from interview.resume_parser import parse_resume
from interview.question_generator import generate_questions
from speech.stt import transcribe_chunk
from evaluation.rules import run_rules
from evaluation.llm_eval import evaluate_with_llm


async def interview_socket(ws: WebSocket):
    """
    Handles ONE interview session (ONE WebSocket connection).
    All state lives inside this function.
    """

    await ws.accept()

    # -------- SESSION STATE --------
    resume_text = None
    questions = []
    current_question_index = 0

    transcript = ""   # accumulated TEXT (not audio)

    await ws.send_json({
        "type": "status",
        "message": "Interview session started"
    })

    try:
        while True:
            message = await ws.receive()

            # ==============================
            # TEXT MESSAGES (JSON)
            # ==============================
            if "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")

                # ---------- RESUME ----------
                if msg_type == "resume":
                    resume_text = data.get("text")

                    # Parse + generate questions ONCE
                    parsed_resume = parse_resume(resume_text)
                    questions = generate_questions(parsed_resume)
                    current_question_index = 0

                    await ws.send_json({
                        "type": "question",
                        "text": questions[current_question_index]
                    })

                # ---------- PROCESS ANSWER ----------
                elif msg_type == "process":
                    # RULES FIRST (non-negotiable)
                    rules_result = run_rules(transcript)

                    # LLM evaluation (local Ollama)
                    llm_result = evaluate_with_llm(
                        transcript=transcript,
                        rules=rules_result
                    )

                    # Send evaluation result
                    await ws.send_json({
                        "type": "result",
                        "data": llm_result
                    })

                    # Clear transcript AFTER evaluation
                    transcript = ""

                    # Move to next question
                    current_question_index += 1
                    if current_question_index < len(questions):
                        await ws.send_json({
                            "type": "question",
                            "text": questions[current_question_index]
                        })
                    else:
                        await ws.send_json({
                            "type": "status",
                            "message": "Interview completed"
                        })

            # ==============================
            # BINARY MESSAGES (AUDIO)
            # ==============================
            if "bytes" in message:
                audio_bytes = message["bytes"]

                # Transcribe EACH chunk independently
                # TODO: Improve WebM → PCM conversion later
                chunk_text = transcribe_chunk(audio_bytes)

                if chunk_text:
                    transcript += " " + chunk_text

                    # Send FULL accumulated transcript
                    await ws.send_json({
                        "type": "transcript",
                        "text": transcript.strip()
                    })

    except Exception as e:
        print("WebSocket closed:", e)
        await ws.close()
