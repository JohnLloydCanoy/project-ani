import streamlit as st

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_chat_history(limit=10):
    formatted_history = []
    # Kukuha lang ng huling 10 messages para iwas sa Rate Limit
    recent_messages = st.session_state.messages[-limit:]
    
    for m in recent_messages:
        formatted_history.append({
            "role": m["role"],
            "parts": [{"text": m["content"]}]
        })
    return formatted_history

def add_user_message(content):
    st.session_state.messages.append({"role": "user", "content": content})

def add_ai_message(content):
    st.session_state.messages.append({"role": "model", "content": content})