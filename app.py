import streamlit as st
import json
import time

# Imports gikan sa code sa imong migo
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db, fetch_all_plants
from components.registry_table import render_registry_table

# Imports para sa imong Voice & Chat Service
from services.voice_service import get_voice_and_text
from core.history_management import (
    initialize_session_state, add_user_message, add_ai_message, get_chat_history
)
from streamlit_mic_recorder import mic_recorder

# --- CONFIG & INITIALIZATION ---
st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")
initialize_session_state()

# CSS para sa Camera UI sa imong migo
st.markdown("""
<style>
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }
    [data-testid="stCameraInput"] { width: 100% !important; }
    [data-testid="stCameraInput"] video { width: 100% !important; border-radius: 15px !important; }
    [data-testid="stCameraInput"] button { 
        width: 100% !important; height: 60px !important; 
        background-color: #FF4B4B !important; color: white !important; 
        font-size: 20px !important; border-radius: 30px !important; 
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Ang Control Center) ---
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    # Mao ni ang switch para dili mag-conflict inyong logic
    app_mode = st.radio("Pili og Mode:", ["📸 Plant Scanner", "💬 Voice Chat & Support"])
    
    st.divider()
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- MODE 1: SCANNER (Code sa imong migo) ---
if app_mode == "📸 Plant Scanner":
    st.title("Plant Health Scanner")
    
    if "last_processed_file_id" not in st.session_state:
        st.session_state.last_processed_file_id = None

    img_file = st.camera_input("📸 Tap to Scan")

    if img_file:
        current_file_id = f"{img_file.name}-{img_file.size}"
        if st.session_state.last_processed_file_id != current_file_id:
            st.session_state.last_processed_file_id = current_file_id
            
            with st.status("🚀 Processing Scan...", expanded=True) as status:
                st.write("☁️ Uploading to Supabase...")
                image_url = upload_image_to_supabase(img_file)
                
                if image_url:
                    st.write("🧠 Analyzing...")
                    img_file.seek(0)
                    ai_response = ask_gemini(img_file)
                    
                    clean_json = ai_response.replace("```json", "").replace("```", "").strip()
                    try:
                        analysis_data = json.loads(clean_json)
                        st.write("💾 Saving...")
                        save_plant_to_db(
                            plant_name=analysis_data.get("plant_name", "Unknown"),
                            image_url=image_url,
                            json_data=analysis_data,
                            farm_name="Main Field"
                        )
                        status.update(label="✅ Done!", state="complete", expanded=False)
                        st.success(f"Identified: {analysis_data.get('plant_name')}")
                        if analysis_data.get("health_status") == "Healthy":
                            st.balloons()
                        else:
                            st.warning(f"Diagnosis: {analysis_data.get('health_status')}")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.session_state.last_processed_file_id = None 

    render_registry_table()

# --- MODE 2: VOICE CHAT (Imong Code) ---
else:
    st.title("Kamusta, Magsasaka! 👋")
    st.write("Ako si A.N.I. Pindutin ang mic para magsalita o i-type ang imong pangutana.")

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Input Section
    input_container = st.container()
    with input_container:
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            user_input = st.chat_input("Dito i-type ang tanong...")
        with col2:
            audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", just_once=True, key='recorder')

    # LOGIC PARA SA BOSES
    if audio_data and audio_data['bytes']:
        with st.chat_message("user"):
            st.write("*(Audio Query)*")
            add_user_message("Farmer sent an audio message.")
        
        with st.chat_message("assistant"):
            with st.spinner("Nakikinig si A.N.I..."):
                history = get_chat_history()
                # Ang get_voice_and_text mokuha og context sa DB ni migo
                response_text, response_audio = get_voice_and_text(audio_data['bytes'], history)
                
                if response_audio:
                    st.audio(response_audio, format="audio/mp3", autoplay=True)
                
                st.write(response_text)
                add_ai_message(response_text)

    # LOGIC PARA SA TEXT
    elif user_input:
        with st.chat_message("user"):
            st.write(user_input)
        add_user_message(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Sinusuri ang datos..."):
                # Gigamit ang ask_gemini para sa text chat history
                response = ask_gemini(get_chat_history())
                st.write(response)
                add_ai_message(response)