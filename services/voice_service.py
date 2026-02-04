import streamlit as st
from streamlit_mic_recorder import mic_recorder
from google import genai
from google.genai import types
import base64
import json
import time
from core.agent import ani_agent

# Initialize Client
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def gemini_tts_autoplay(text):
    """
    🎤 VOICE ENGINE: Uses Gemini 2.5 Flash
    (Because Gemini 3 cannot generate audio output yet)
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Keep this as 2.0/2.5 for Audio
            contents=f"Say this in a helpful, Filipino-accented English: {text}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"], # Force Audio Output
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Aoede"
                        )
                    )
                )
            )
        )
        audio_bytes = response.candidates[0].content.parts[0].inline_data.data
        b64 = base64.b64encode(audio_bytes).decode()
        md = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/wav;base64,{b64}" type="audio/wav">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        return len(text) / 15 

    except Exception as e:
        st.error(f"TTS Error: {e}")
        return 0

def render_floating_voice_button():
    
    
    audio = mic_recorder(
        start_prompt="🎙️ TALK TO GEMINI 3",
        stop_prompt="✋ SEND",
        key="gemini3_voice",
        format="wav"
    )

    if audio:
        st.toast("🧠 Gemini 3 is thinking...", icon="⚡")
        prompt = """
        You are the Brain of Project ANI.
        User Audio: Tagalog, Bisaya, or English.
        
        TASK:
        1. Understand the intent.
        2. Create a short spoken reply (max 10 words).
        3. Output JSON.
        
        JSON STRUCTURE:
        {"target_page": "scan", "reply": "Opening scanner now."}
        """

        try:
            logic_response = client.models.generate_content(
                model="gemini-3-flash-preview", 
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(inline_data=types.Blob(
                                mime_type="audio/wav",
                                data=audio['bytes']
                            ))
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            data = json.loads(logic_response.text)
            target = data.get("target_page")
            reply = data.get("reply")
            
            # Speak with 2.5, Think with 3.0
            st.success(f"🗣️ ANI: {reply}")
            duration = gemini_tts_autoplay(reply)
            
            if target:
                time.sleep(duration + 1)
                st.session_state.page = target
                st.rerun()

        except Exception as e:
            st.error(f"Gemini 3 Error: {e}")