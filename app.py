import streamlit as st
from config.app_config import app_config
from streamlit_float import *
from streamlit_mic_recorder import mic_recorder
from services.voice_service import gemini_tts_autoplay


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
            # Your speech-to-text logic here (from voice_service.py)
            # Then: response = ani_agent(user_text)
            # Then: gemini_tts_autoplay(response)
        except Exception as e:
            st.error(f"Voice error: {e}")

button_container.float(
    "bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 9999;"
)