import whisper
import os
import tempfile

# Loading 'small' model for better regional language accuracy
print("Loading Whisper Model...")
model = whisper.load_model("small")
print("Whisper Model Loaded Successfully!")


def transcribe_audio_file(
    file_bytes: bytes, 
    file_extension: str = ".wav", 
    language: str = "ta", 
    translate_to_english: bool = False
) -> str:
    """
    Saves incoming audio bytes to a temp file, runs Whisper AI transcription,
    and returns the transcribed text.
    """
    # Create a temporary file to hold the uploaded audio bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_audio:
        temp_audio.write(file_bytes)
        temp_file_path = temp_audio.name

    try:
        # Determine whether to return Tamil script or translate directly to English
        task_type = "translate" if translate_to_english else "transcribe"

        # Explicitly setting language='ta' forces Whisper to focus on Tamil phonetics
        result = model.transcribe(
            temp_file_path,
            language=language,
            task=task_type
        )
        
        transcribed_text = result.get("text", "").strip()
        return transcribed_text

    finally:
        # Clean up temporary audio file from disk
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)