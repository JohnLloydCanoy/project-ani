import streamlit as st

def initialize_session_state():
    """
    Creates the memory list if it doesn't exist yet.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_chat_history():
    """
    Returns the clean list of messages for the AI to read.
    """
    # only send the text content to the AI, not the UI objects
    return [m["content"] for m in st.session_state.messages]

def add_user_message(content):
    """
    Saves what YOU typed.
    """
    st.session_state.messages.append({"role": "user", "content": content})

def add_ai_message(content):
    """
    Saves what the AI replied.
    """
    st.session_state.messages.append({"role": "model", "content": content})