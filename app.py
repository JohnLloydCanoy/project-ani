import streamlit as st
from dotenv import load_dotenv
from core.agent import ask_gemini
from core.history_management import (initialize_session_state, add_user_message, add_ai_message, get_chat_history)
from services.vision_service import (process)  
from PIL import Image
from components.camera.picture.take_picture import take_picture
from components.camera.video.take_video import take_video

load_dotenv()
st.set_page_config(
    page_title="Project A.N.I.",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar 
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    st.caption("Agricultural Network Intelligence")
    st.markdown("---")
    st.write("System Status: **Online** 🟢")

# Main Title
st.title("Hi! Welcome to Project A.N.I. 👋")
st.write("I am your AI Agronomist. Ask me anything about your crops!")

# --- THE CHAT LOGIC STARTS HERE ---

initialize_session_state()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("📸 Take Picture", use_container_width=True):
        st.session_state.camera_active = True
        st.rerun()

# Render camera if active
if st.session_state.get("camera_active", False):
    take_picture()

