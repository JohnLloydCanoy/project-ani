import streamlit as st
import json
import time

# --- IMPORTS ---
# Make sure you have services/agent.py (for ask_gemini) 
# AND services/db_services.py (for database)
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db 
from components.registry_table import render_registry_table

# 1. Page Config
st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")

# 2. CSS HACK (Makes the native camera look like a full-screen app)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    [data-testid="stCameraInput"] {
        width: 100% !important;
    }
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: auto !important;
        object-fit: cover !important;
        border-radius: 15px !important;
    }
    [data-testid="stCameraInput"] button {
        width: 100% !important;
        height: 60px !important;
        background-color: #FF4B4B !important;
        color: white !important;
        font-size: 20px !important;
        border-radius: 30px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🌱 Project A.N.I.")

# --- CAMERA SECTION ---
img_file = st.camera_input("📸 Tap to Scan")

if img_file:
    with st.status("🚀 Processing Scan...", expanded=True) as status:
        
        st.write("☁️ Uploading...")
        image_url = upload_image_to_supabase(img_file)
        
        if image_url:
            st.write("🧠 Analyzing...")
            ai_response = ask_gemini(img_file)
            
            # Clean JSON
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
                
                # Result
                st.success(f"Identified: {analysis_data.get('plant_name')}")
                if analysis_data.get("health_status") == "Healthy":
                    st.balloons()
                else:
                    st.warning(f"Diagnosis: {analysis_data.get('health_status')}")
                    
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Upload failed.")

# --- TABLE ---
render_registry_table()