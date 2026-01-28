import streamlit as st
from streamlit_mic_recorder import mic_recorder
from services.voice_service import get_voice_and_text
from core.agent import ask_gemini
from core.history_management import (
    initialize_session_state, add_user_message, add_ai_message, get_chat_history
)

st.set_page_config(page_title="Project A.N.I.", page_icon="🌱", layout="wide")

# Sidebar
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    st.write("Your AI Agronomist (Voice Mode)")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

st.title("Kamusta, Magsasaka! 👋")
st.write("Ako si A.N.I. Pindutin ang mic para magsalita.")

initialize_session_state()

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
        with st.spinner("Nakikinig at nag-iisip si A.N.I..."):
            history = get_chat_history()
            # Dito tinatawag ang bagong service
            response_text, response_audio = get_voice_and_text(audio_data['bytes'], history)
            
            if response_audio:
                # Eto ang magpapatunog sa boses ni A.N.I.
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
            response = ask_gemini(get_chat_history())
            st.write(response)
            # (Optional) Kung gusto mo rin may boses ang text input, 
            # pwede nating gawan ng hiwalay na function.
    add_ai_message(response)