import streamlit as st
from core import session_manager

def app_config():
# --- CONFIG & INITIALIZATION ---
    st.set_page_config(
        page_title="A.N.I.", 
        page_icon="🌱", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    session_manager.initialize_app_state()