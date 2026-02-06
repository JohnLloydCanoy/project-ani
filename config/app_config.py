import streamlit as st
import uuid
from core.api_key_manager import render_api_usage_sidebar

# Here we define the app_config function to set the Streamlit page configuration

def app_config():
    st.set_page_config(
        page_title="Project A.N.I.", 
        page_icon="🌱", 
        layout="wide")
    home_page = st.Page("pages/home.py", title="🏠 Home Dashboard")
    scan_page = st.Page("pages/scan.py", title="📸 Scan Plant")
    view_twin = st.Page("pages/view_digital_twin.py", title="🌿 Digital Twin")
    registry_page = st.Page("pages/registry.py", title="📋 Registry")
    pg = st.navigation({
    "Main": [home_page],
    "Tools": [scan_page, view_twin, registry_page]
    })
    # Run the navigation
    pg.run()
    
    if "user_id" not in st.session_state:
        generated_id = str(uuid.uuid4())[:8]
        st.session_state.user_id = generated_id
    with st.sidebar:
        st.markdown(f"**🔑 Device ID:** `{st.session_state.user_id}`")
        st.caption("Data is linked to this session ID.")
        
        # API Usage Monitor
        st.divider()
        render_api_usage_sidebar()