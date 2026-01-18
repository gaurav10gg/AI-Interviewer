# speech/stt.py

"""
STT MODULE
- Transcribes EACH audio chunk independently
- No audio is stored
- Text is returned immediately
"""

import tempfile
import os
import whisper
from backend.config import WHISPER_MODEL

# Load model ONCE (important for performance)
_model = None

def get_model():
    """Lazy load the Whisper model"""
    global _model
    if _model is None:
        print(f"Loading Whisper model: {WHISPER_MODEL}")
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe_chunk(audio_bytes: bytes) -> str:
    """
    Convert a single audio chunk (WebM) to text.

    NOTE:
    - Browser sends WebM/Opus
    - Whisper expects audio file
    - We temporarily write chunk to disk

    TODO:
    - Proper WebM → PCM conversion for better accuracy
    """

    if not audio_bytes or len(audio_bytes) < 100:
        return ""

    try:
        # Create temporary file with .webm extension
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(audio_bytes)
            tmp.flush()

        try:
            model = get_model()
            
            # Transcribe with error handling
            result = model.transcribe(
                tmp_path, 
                fp16=False,
                language="en",
                task="transcribe"
            )
            
            text = result.get("text", "").strip()
            return text
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass

    except Exception as e:
        print(f"STT transcription error: {e}")
        return ""