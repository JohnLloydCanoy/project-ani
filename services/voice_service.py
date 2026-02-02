import streamlit as st
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai
import io
import json

def render_floating_voice_button():
    """
    Renders a recording button styled like a Primary Action button.
    Handles recording -> Gemini -> Navigation.
    """
    st.markdown("""
    <style>
        /* Target the button created by streamlit-mic-recorder */
        button[kind="secondary"] {
            background-color: #FF4B4B !important; /* Streamlit Red */
            color: white !important;
            border: none !important;
            border-radius: 50px !important; /* Pill shape */
            padding: 15px 20px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            width: 100% !important; /* Full width of container */
            box-shadow: 0px 4px 6px rgba(0,0,0,0.2) !important;
            transition: all 0.2s ease;
        }
        button[kind="secondary"]:hover {
            background-color: #FF2B2B !important;
            transform: scale(1.02);
        }
        button[kind="secondary"]:active {
            background-color: #BF3B3B !important;
        }
    </style>
    """, unsafe_allow_html=True)

    audio = mic_recorder(
        start_prompt="🎙️ TALK TO ANI (Hold)",
        stop_prompt="✋ Release to Send",
        key="global_voice_btn",
        format="wav"
    )