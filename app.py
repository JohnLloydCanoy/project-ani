import streamlit as st
import json
import time

# Imports gikan sa code sa imong migo
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db, fetch_all_plants
from components.registry_table import render_registry_table

# Imports para sa imong Voice Service
from services.voice_service import get_voice_and_text
from core.history_management import (
    initialize_session_state, add_user_message, add_ai_message, get_chat_history
)

# --- CONFIG & UI ---
st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")
initialize_session_state() # Siguraduhon nga naay chat memory

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

# --- VOICE ASSISTANT DIALOG ---
@st.dialog("Project A.N.I. Voice Support")
def open_voice_assistant():
    st.write("Kumusta, mag-uuma! Unsay ikatabang nako nimo karon?")
    
    # Audio input para sa boses
    audio_file = st.audio_input("Pinduta ang mic para mosulti")
    
    if audio_file:
        with st.spinner("Naghunahuna si A.N.I..."):
            history = get_chat_history()
            # Mo-generate og tubag base sa audio ug context
            response_text, response_audio = get_voice_and_text(audio_file.read(), history)
            
            if response_audio:
                st.audio(response_audio, format="audio/mp3", autoplay=True)
            
            st.info(response_text)
            
            if st.button("Save sa Chat History"):
                add_user_message("Voice Query")
                add_ai_message(response_text)
                st.success("Saved!")
                time.sleep(1)
                st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌱 A.N.I. Menu")
    st.markdown("Expert Agronomist in your pocket.")
    if st.button("🎙️ Ask A.N.I. (Voice)", use_container_width=True):
        open_voice_assistant()
    
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN SCANNER INTERFACE ---
st.title("🌱 Project A.N.I.")

if "last_processed_file_id" not in st.session_state:
    st.session_state.last_processed_file_id = None

img_file = st.camera_input("📸 Tap to Scan")

if img_file:
    current_file_id = f"{img_file.name}-{img_file.size}"

    if st.session_state.last_processed_file_id != current_file_id:
        st.session_state.last_processed_file_id = current_file_id
        
        with st.status("🚀 Processing Scan...", expanded=True) as status:
            st.write("☁️ Uploading to Supabase...")
            image_url = upload_image_to_supabase(img_file) #
            
            if image_url:
                st.write("🧠 Gemini 3 Analyzing...")
                img_file.seek(0)
                ai_response = ask_gemini(img_file) #
                
                clean_json = ai_response.replace("```json", "").replace("```", "").strip()
                
                try:
                    analysis_data = json.loads(clean_json)
                    st.write("💾 Saving to Registry...")
                    save_plant_to_db(
                        plant_name=analysis_data.get("plant_name", "Unknown"),
                        image_url=image_url,
                        json_data=analysis_data,
                        farm_name="Main Field"
                    ) #
                    
                    status.update(label="✅ Done!", state="complete", expanded=False)
                    st.success(f"Identified: {analysis_data.get('plant_name')}")
                    
                    if analysis_data.get("health_status") == "Healthy":
                        st.balloons()
                    else:
                        st.warning(f"Diagnosis: {analysis_data.get('health_status')}")
                    
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error parsing AI response: {e}")
                    st.session_state.last_processed_file_id = None 
            else:
                st.error("Upload failed.")
                st.session_state.last_processed_file_id = None

# --- REGISTRY TABLE ---
render_registry_table() # I-display ang listahan gikan sa Supabase