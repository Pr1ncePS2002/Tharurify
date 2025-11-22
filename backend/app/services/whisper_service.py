import whisper
import os
from functools import lru_cache
from app.core.settings import settings

_model = None

def _get_model():
    global _model
    if _model is None:
        size = settings.whisper_model_size
        _model = whisper.load_model(size)
    return _model



def transcribe_audio(file_path: str) -> dict:
    """
    Transcribe audio using Whisper Medium model.
    :param file_path: Path to the uploaded audio file
    :return: Dictionary with transcription result
    """
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    model = _get_model()
    result = model.transcribe(file_path)
    return {"text": result["text"]}
