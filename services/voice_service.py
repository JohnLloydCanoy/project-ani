import io
import streamlit as st
from gtts import gTTS
from google import genai
from google.genai import types
from config.settings import get_api_key, SYSTEM_PROMPT
from services.db_service import fetch_all_plants

# Gigamit ang get_api_key() gikan sa imong settings nga naay load_dotenv()
client = genai.Client(api_key=get_api_key())

def get_voice_and_text(audio_bytes, history):
    """
    Mokuha og tubag gikan sa Gemini 3 Flash (Multimodal) base sa tingog 
    ug context gikan sa Supabase.
    """
    try:
        # 1. Context Retrieval: Unsa ang pinakabag-o nga gi-scan sa farmer?
        plants = fetch_all_plants()
        latest = plants[0] if plants else None
        
        # Himoong dynamic ang context para mahibalo si A.N.I.
        current_context = "Ang mag-uuma naa sa dashboard."
        if latest:
            current_context = (
                f"Ang pinakabag-o nga gi-scan mao ang {latest['plant_name']} "
                f"nga naay health status nga {latest['health_status']}."
            )

        # 2. Gemini 3 Flash Generation
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                # Gi-combine ang SYSTEM_PROMPT (Personality) ug ang Context (Data)
                f"{SYSTEM_PROMPT}\n\nKAHIMTANG KARON: {current_context}", 
                *history, 
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ],
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="low")
            )
        )
        
        response_text = response.text
        
        # 3. Text-to-Speech gamit ang gTTS (Tagalog 'tl' accent)
        tts = gTTS(text=response_text, lang='tl', slow=False)
        
        # I-save sa memory para paspas ang playback
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        return response_text, audio_fp.read()
        
    except Exception as e:
        return f"Nasugamak sa sayop: {e}", None