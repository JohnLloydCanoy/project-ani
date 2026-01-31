import streamlit as st
import json
import time
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db 
from components.registry_table import render_registry_table
from config.app_config import app_config

app_config()

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


st.title("🌱 Project A.N.I.")

if "last_processed_file_id" not in st.session_state:
    st.session_state.last_processed_file_id = None

img_file = st.camera_input("📸 Tap to Scan")

if img_file:

    current_file_id = f"{img_file.name}-{img_file.size}"

    if st.session_state.last_processed_file_id != current_file_id:
        
        st.session_state.last_processed_file_id = current_file_id
        
        with st.status("🚀 Processing Scan...", expanded=True) as status:
            
            st.write("☁️ Uploading...")
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
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.last_processed_file_id = None 
            else:
                st.error("Upload failed.")
                st.session_state.last_processed_file_id = None

# --- TABLE ---
render_registry_table()