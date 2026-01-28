import io
from gtts import gTTS
from google import genai
from google.genai import types
from config.settings import get_api_key

client = genai.Client(api_key=get_api_key())

def get_voice_and_text(audio_bytes, history):
    """
    Kukuha ng text mula sa Gemini at gagawing boses gamit ang gTTS.
    """
    try:
        # 1. Kunin ang sagot mula kay Gemini 3
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                *history, 
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            )
        )
        
        response_text = response.text
        
        # 2. I-convert ang text sa boses (Tagalog 'tl' ang gamit natin)
        tts = gTTS(text=response_text, lang='tl', slow=False)
        
        # I-save sa memory (BytesIO)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0) # I-reset ang pointer sa simula
        
        return response_text, audio_fp.read()
        
    except Exception as e:
        return f"Error: {e}", None