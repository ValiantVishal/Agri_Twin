from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.utils.whisper_model import transcribe_audio_file
import os

router = APIRouter(
    prefix="/voice",
    tags=["Voice Recognition"]
)

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}


@router.post("/transcribe")
async def transcribe_voice(file: UploadFile = File(...)):
    """
    Receives an audio file from Postman, mobile app, or browser UI
    and returns the transcribed text using Whisper AI.
    """
    # 1. Validate file extension
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    try:
        # 2. Read audio content as bytes
        audio_bytes = await file.read()

        # 3. Process transcription
        text_output = transcribe_audio_file(audio_bytes, file_extension=ext)

        return {
            "status": "success",
            "filename": file.filename,
            "transcription": text_output
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {str(e)}"
        )