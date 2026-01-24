from google import genai
from google.genai import types
from config.settings import get_api_key

client = genai.Client(api_key=get_api_key())

def transcribe_audio(audio_bytes):
    if not audio_bytes: return None
    try:
        # Dapat mag-match ang model dito para hindi mag-error
        response = client.models.generate_content(
            model='gemini-3-flash-preview', 
            contents=[
                "Transcribe this agricultural query accurately. Keep the native language (Tagalog/Bisaya).",
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ]
        )
        return response.text
    except Exception as e:
        return f"Error sa Transcription: {e}"