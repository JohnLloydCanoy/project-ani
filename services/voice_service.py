from time import time
import streamlit as st
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import io
import json

def render_floating_voice_button():
    """
    Renders a recording button styled like a Primary Action button.
    Handles recording -> Gemini -> Navigation.
    """
    st.markdown("""
    <style>
        /* Target the button created by streamlit-mic-recorder */
        button[kind="secondary"] {
            background-color: #FF4B4B !important; /* Streamlit Red */
            color: white !important;
            border: none !important;
            border-radius: 50px !important; /* Pill shape */
            padding: 15px 20px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            width: 100% !important; /* Full width of container */
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2) !important;
            transition: all 0.2s ease;
        }
        button[kind="secondary"]:hover {
            background-color: #FF2B2B !important;
            transform: scale(1.02);
        }
        button[kind="secondary"]:active {
            background-color: #BF3B3B !important;
        }
    </style>
    """, unsafe_allow_html=True)

    audio = mic_recorder(
        start_prompt="🎙️ TALK TO ANI (Hold)",
        stop_prompt="✋ Release to Send",
        key="global_voice_btn",
        format="wav"
    )
    if audio:
        # Shpeck: Show thinking toast
        st.toast("🧠 ANI is thinking...", icon="🤔")
        
        audio_bytes = audio['bytes']
        prompt = """
        You are the navigation controller for "Project ANI".
        Listen to the user (English/Tagalog/Bisaya) and map to JSON:
        - {"target_page": "dashboard"} (Home, Balik, Menu)
        - {"target_page": "scan"} (Camera, Picture, Litrato, Scan)
        - {"target_page": "chat"} (Talk, Usap, Question, Advice)
        - {"target_page": "registry"} (List, Records, Database)
        
        Return ONLY JSON.
        """
        try:
            model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
            response = model.generate_content([
                prompt,
                {"mime_type": "audio/wav", "data": audio_bytes}
            ])
            
            text = response.text.replace("```json", "").replace("```", "").strip()
            s = text.find("{")
            e = text.rfind("}") + 1
            if s != -1 and e != -1:
                intent = json.loads(text[s:e])
                target = intent.get("target_page")
                
                if target:
                    st.success(f"Going to {target}...")
                    time.sleep(0.5)
                    st.session_state.page = target
                    st.rerun()
            else:
                st.warning("I didn't catch that command.")

        except Exception as e:
            st.error(f"Error: {e}")