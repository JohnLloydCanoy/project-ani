import streamlit as st
from dotenv import load_dotenv
from core.agent import ask_gemini
from core.history_management import (
    initialize_session_state, 
    add_user_message, 
    add_ai_message, 
    get_chat_history
)

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

user_input = st.chat_input("Type your question here...")

if user_input:
    # Users Message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Save User Message to Memory
    add_user_message(user_input)
    
    # Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing agricultural data..."):
            # Get history -> Send to AI -> Get Answer
            history_context = get_chat_history()
            response = ask_gemini(history_context)
            
            st.write(response)
            
    # Save AI Response to Memory
    add_ai_message(response)
# --- THE CHAT LOGIC ENDS HERE ---