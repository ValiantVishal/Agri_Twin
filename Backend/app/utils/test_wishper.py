import whisper

print("Testing Whisper AI locally...")
model = whisper.load_model("base")

# Replace with path to any test audio file on your PC (.mp3, .wav, etc.)
audio_path = "sample.wav" 

try:
    result = model.transcribe(audio_path)
    print("\n--- Transcription Result ---")
    print(result["text"])
except Exception as e:
    print(f"Test failed: {e}")