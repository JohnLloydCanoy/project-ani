import streamlit as st
from dotenv import load_dotenv
from core.agent import ask_gemini
from core.history_management import (initialize_session_state, add_user_message, add_ai_message, get_chat_history)
from components.camera.picture.take_picture import take_picture

from PIL import Image


def process():
    # Function to process image or video input And analyze it  
    take_picture()
