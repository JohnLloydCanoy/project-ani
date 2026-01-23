from google import genai
from config.settings import get_api_key

# Standardize to use the new Client
api_key = get_api_key()
client = genai.Client(api_key=api_key)

def transcribe_audio(audio_bytes):
    if not audio_bytes:
        return None
    
    try:
        # Use the new client format for the audio transcription
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                "Transcribe this agricultural query. Keep Tagalog/Bisaya if used. Return only text.",
                {'mime_type': 'audio/wav', 'data': audio_bytes}
            ]
        )
        return response.text
    except Exception as e:
        return f"Error transcribing audio: {e}"