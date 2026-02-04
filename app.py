import streamlit as st
from config.app_config import app_config
from streamlit_float import *


app_config()
float_init()


button_container = st.container()
with button_container:
    # Replace button with voice recorder
    audio = mic_recorder(
        start_prompt="🎙️ TALK TO ANI",
        stop_prompt="✋ PROCESSING...",
        key="ani_voice_assistant",
        format="wav"
    )
    
    if audio:
        st.toast("🧠 A.N.I. is thinking...", icon="⚡")
        
        # Convert speech to text and process with ani_agent
        try:
            from core.agent import ani_agent
            from services.voice_service import gemini_tts_autoplay
            from google import genai
            from google.genai import types
            
            if "GEMINI_API_KEY" in st.secrets:
                client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Convert speech to text
            speech_to_text_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text="Convert this audio to text:"),
                            types.Part(inline_data=types.Blob(
                                mime_type="audio/wav",
                                data=audio['bytes']
                            ))
                        ]
                    )
                ]
            )
            
            user_text = speech_to_text_response.text
            st.success(f"🗣️ You said: {user_text}")
            
            # Process with ani_agent
            response = ani_agent(user_text)
            
            # Speak the response
            gemini_tts_autoplay(response)
            
        except Exception as e:
            st.error(f"Voice error: {e}")
button_container.float(
    "bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 9999;"
)