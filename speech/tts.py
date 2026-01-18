# speech/tts.py

"""
TTS MODULE
- Uses Edge TTS locally
- Converts question text → spoken audio
"""

import subprocess
import tempfile
import os


def speak(text: str):
    """
    Speak the given text aloud using Edge TTS.
    Blocking call (acceptable for MVP).
    """

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            audio_path = tmp.name

        subprocess.run([
            "edge-tts",
            "--voice", "en-US-AriaNeural",
            "--text", text,
            "--write-media", audio_path
        ], check=True)

        # Play audio (platform dependent)
        if os.name == "nt":  # Windows
            os.system(f'start {audio_path}')
        else:  # Linux / Mac
            os.system(f'afplay {audio_path}')

    except Exception as e:
        print("TTS failed:", e)
