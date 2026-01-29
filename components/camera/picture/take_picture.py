import streamlit as st
import json
import time
from core.agent import ask_gemini
from services.db_service import upload_image_to_supabase, save_plant_to_db 
from components.registry_table import render_registry_table

st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")


st.markdown("""
<style>
    /* 1. Remove top padding to maximize space */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* 2. Force the Camera Input to be Full Width */
    [data-testid="stCameraInput"] {
        width: 100% !important;
    }
    
    /* 3. Make the video element fill the container */
    [data-testid="stCameraInput"] video {
        width: 100% !important;
        height: auto !important;
        object-fit: cover !important;
        border-radius: 15px !important;
    }
    
    /* 4. Make the "Take Photo" button big and clickable */
    [data-testid="stCameraInput"] button {
        width: 100% !important;
        height: 60px !important;
        background-color: #FF4B4B !important; /* Streamlit Red */
        color: white !important;
        font-size: 20px !important;
        border-radius: 30px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("🌱 Project A.N.I.")
st.caption("Agricultural Network Intelligence")


img_file = st.camera_input("📸 Tap to Scan")

if img_file:
    with st.status("🚀 Processing Scan...", expanded=True) as status:
        
        st.write("☁️ Uploading...")
        image_url = upload_image_to_supabase(img_file)
        
        if image_url:
            st.write("🧠 Analyzing...")
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
                if analysis_data.get("health_status") != "Healthy":
                    st.warning(f"Diagnosis: {analysis_data.get('health_status')}")
                    st.info(f"Rx: {analysis_data.get('action_plan')}")
                else:
                    st.balloons()
                    
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

render_registry_table()