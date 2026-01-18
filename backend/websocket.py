# backend/websocket.py

import json
import base64
import tempfile
import os
from fastapi import WebSocket
from typing import Optional

from interview.resume_parser import parse_resume, pdf_to_text
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
    resume_text: Optional[str] = None
    questions = []
    current_question_index = 0

    transcript = ""   # accumulated TEXT (not audio)

    await ws.send_json({
        "type": "status",
        "message": "Interview session started. Please upload your resume PDF."
    })

    try:
        while True:
            message = await ws.receive()

            # ==============================
            # TEXT MESSAGES (JSON)
            # ==============================
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    msg_type = data.get("type")

                    # ---------- RESUME PDF ----------
                    if msg_type == "resume_pdf":
                        filename = data.get("filename", "resume.pdf")
                        base64_data = data.get("data", "")
                        
                        if not base64_data:
                            await ws.send_json({
                                "type": "status",
                                "message": "Error: No PDF data received"
                            })
                            continue

                        try:
                            # Decode base64 to bytes
                            pdf_bytes = base64.b64decode(base64_data)
                            
                            # Save to temporary file
                            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                                tmp_path = tmp.name
                                tmp.write(pdf_bytes)
                                tmp.flush()
                            
                            try:
                                # Extract text from PDF
                                await ws.send_json({
                                    "type": "status",
                                    "message": f"Processing {filename}..."
                                })
                                
                                resume_text = pdf_to_text(tmp_path)
                                
                                if not resume_text or len(resume_text.strip()) < 50:
                                    await ws.send_json({
                                        "type": "status",
                                        "message": "Error: Could not extract text from PDF. Please ensure it's not a scanned image."
                                    })
                                    continue
                                
                                # Parse + generate questions
                                await ws.send_json({
                                    "type": "status",
                                    "message": "Analyzing your resume..."
                                })
                                
                                parsed_resume = parse_resume(resume_text)
                                questions = generate_questions(parsed_resume)
                                current_question_index = 0

                                await ws.send_json({
                                    "type": "status",
                                    "message": f"Generated {len(questions)} questions from your resume!"
                                })

                                await ws.send_json({
                                    "type": "question",
                                    "text": questions[current_question_index]
                                })
                                
                            finally:
                                # Clean up temp file
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass
                                    
                        except Exception as e:
                            print(f"PDF processing error: {e}")
                            await ws.send_json({
                                "type": "status",
                                "message": f"Error processing PDF: {str(e)}"
                            })

                    # ---------- RESUME TEXT (fallback) ----------
                    elif msg_type == "resume":
                        resume_text = data.get("text", "").strip()
                        
                        if not resume_text:
                            await ws.send_json({
                                "type": "status",
                                "message": "Error: Resume text is empty"
                            })
                            continue

                        try:
                            # Parse + generate questions ONCE
                            parsed_resume = parse_resume(resume_text)
                            questions = generate_questions(parsed_resume)
                            current_question_index = 0

                            await ws.send_json({
                                "type": "status",
                                "message": f"Generated {len(questions)} questions from your resume"
                            })

                            await ws.send_json({
                                "type": "question",
                                "text": questions[current_question_index]
                            })
                        except Exception as e:
                            print(f"Resume parsing error: {e}")
                            await ws.send_json({
                                "type": "status",
                                "message": f"Error processing resume: {str(e)}"
                            })

                    # ---------- PROCESS ANSWER ----------
                    elif msg_type == "process":
                        if not transcript.strip():
                            await ws.send_json({
                                "type": "result",
                                "data": {
                                    "score": 0,
                                    "clarity": "low",
                                    "depth": "low",
                                    "feedback": "No answer provided. Please record your answer."
                                }
                            })
                        else:
                            try:
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
                            except Exception as e:
                                print(f"Evaluation error: {e}")
                                await ws.send_json({
                                    "type": "result",
                                    "data": {
                                        "score": 0,
                                        "clarity": "low",
                                        "depth": "low",
                                        "feedback": f"Evaluation failed: {str(e)}"
                                    }
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
                                "message": "Interview completed! Thank you."
                            })

                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    await ws.send_json({
                        "type": "status",
                        "message": "Invalid message format"
                    })

            # ==============================
            # BINARY MESSAGES (AUDIO)
            # ==============================
            elif "bytes" in message:
                audio_bytes = message["bytes"]

                try:
                    # Transcribe EACH chunk independently
                    chunk_text = transcribe_chunk(audio_bytes)

                    if chunk_text:
                        transcript += " " + chunk_text

                        # Send FULL accumulated transcript
                        await ws.send_json({
                            "type": "transcript",
                            "text": transcript.strip()
                        })
                except Exception as e:
                    print(f"Transcription error: {e}")
                    # Don't send error to client for transcription failures

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        try:
            await ws.close()
        except:
            pass