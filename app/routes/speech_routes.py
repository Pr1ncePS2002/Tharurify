from fastapi import APIRouter, UploadFile, File, HTTPException
import asyncio
import shutil
import os
from app.services.whisper_service import transcribe_audio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25MB size limit

@router.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        # Validate file type
        if not file.filename.lower().endswith((".wav", ".mp3", ".m4a")):
            raise HTTPException(status_code=400, detail="Only WAV, MP3, and M4A files are allowed")

        temp_file_path = f"temp_{file.filename}"
        
        # Async file handling
        size = 0
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > MAX_AUDIO_BYTES:
                    buffer.close()
                    os.remove(temp_file_path)
                    raise HTTPException(status_code=413, detail="Audio file too large (limit 25MB)")
                buffer.write(chunk)

        logger.info(f"Processing file: {file.filename}")
        # Offload CPU-bound transcription to thread pool
        result = await asyncio.to_thread(transcribe_audio, temp_file_path)

        # Cleanup
        os.remove(temp_file_path)
        
        return {"status": "success", "transcript": result}

    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))