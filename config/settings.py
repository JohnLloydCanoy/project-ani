import streamlit as st

SYSTEM_PROMPT = """
You are ANI, an expert AI Agronomist 
dedicated to helping farmers in the Philippines. 
You provide clear, practical advice on crop diseases, soil health, and pest control.
Always be encouraging, professional, and concise.
"""

def get_api_key():
    """
    Safely retrieves the API key from .streamlit/secrets.toml
    """
    try:
        return st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("❌ GEMINI_API_KEY not found in secrets.toml!")
        st.stop()
    except FileNotFoundError:
        st.error("❌ .streamlit/secrets.toml file is missing!")
        st.stop()