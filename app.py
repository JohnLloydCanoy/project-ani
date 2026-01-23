import streamlit as st
from dotenv import load_dotenv
from core.agent import ask_gemini
from core.history_management import (
    initialize_session_state, 
    add_user_message, 
    add_ai_message, 
    get_chat_history
)
from services.voice_service import transcribe_audio
from streamlit_mic_recorder import mic_recorder
from PIL import Image

load_dotenv()
st.set_page_config(
    page_title="Project A.N.I.",
    page_icon="🌱",
    layout="wide"
)

# Sidebar 
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    st.caption("Agricultural Network Intelligence")
    st.markdown("---")
    enable_voice = st.toggle("Enable Voice Mode (Beta)", value=False)
    if enable_voice:
        st.info("A.N.I. is listening... Speak your question.")

st.title("Hi! Welcome to Project A.N.I. 👋")
st.write("I am your AI Agronomist. Ask me anything about your crops!")

initialize_session_state()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# UI for Input
col1, col2 = st.columns([0.9, 0.1])
with col1:
    user_input = st.chat_input("Type your question here...")

with col2:
    if enable_voice:
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", just_once=True, key='recorder')
    else:
        audio_data = None

# Process Voice Input
if audio_data and audio_data['bytes']:
    with st.spinner("Translating voice..."):
        user_input = transcribe_audio(audio_data['bytes'])

# Main Logic
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    add_user_message(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing agricultural data..."):
            history_context = get_chat_history()
            response = ask_gemini(history_context)
            st.write(response)
    add_ai_message(response)