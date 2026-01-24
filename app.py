import streamlit as st
from streamlit_mic_recorder import mic_recorder
from services.voice_service import transcribe_audio
from core.agent import ask_gemini
from core.history_management import (
    initialize_session_state, add_user_message, add_ai_message, get_chat_history
)

st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    st.write("Your AI Agronomist")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("Kamusta, Magsasaka! 👋")
st.write("Ako si A.N.I. Ano ang maitutulong ko sa iyong farm?")

initialize_session_state()

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input Section (Side-by-Side)
input_container = st.container()
with input_container:
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        user_input = st.chat_input("Dito i-type ang iyong tanong...")
    with col2:
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="🛑", just_once=True, key='recorder')

# Process Voice
if audio_data and audio_data['bytes']:
    with st.spinner("Nakikinig si A.N.I..."):
        user_input = transcribe_audio(audio_data['bytes'])

# Logic
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    add_user_message(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("Sinusuri ang datos..."):
            response = ask_gemini(get_chat_history())
            st.write(response)
    add_ai_message(response)