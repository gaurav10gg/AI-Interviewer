# speech/stt.py

"""
STT MODULE
- Transcribes EACH audio chunk independently
- No audio is stored
- Text is returned immediately
"""

import tempfile
import whisper

# Load model ONCE (important for performance)
_model = whisper.load_model("small")


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

    try:
        with tempfile.NamedTemporaryFile(suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            tmp.flush()

            result = _model.transcribe(tmp.name, fp16=False)
            return result.get("text", "").strip()

    except Exception as e:
        print("STT failed:", e)
        return ""
