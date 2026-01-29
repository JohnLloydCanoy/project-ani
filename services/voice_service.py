import io
import streamlit as st
from gtts import gTTS
from google import genai
from google.genai import types
from config.settings import get_api_key, SYSTEM_PROMPT
from services.db_service import fetch_all_plants

client = genai.Client(api_key=get_api_key())

def get_voice_and_text(audio_bytes, history):
    try:
        # Kuhaon ang pinakabag-o nga scan gikan sa DB sa imong migo
        plants = fetch_all_plants()
        latest = plants[0] if plants else None
        
        context = f"User is viewing the dashboard."
        if latest:
            context = f"The last plant scanned was {latest['plant_name']} with status {latest['health_status']}."

        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                f"{SYSTEM_PROMPT}\n\nCONTEXT: {context}", #
                *history, 
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ],
            config=types.GenerateContentConfig(thinking_config={"thinking_level": "low"})
        )
        
        txt = response.text
        tts = gTTS(text=txt, lang='tl', slow=False) #
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        return txt, audio_fp.read()
    except Exception as e:
        return f"Error: {e}", None