import streamlit as st
import streamlit.components.v1 as components
import json
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db, fetch_all_plants
from components.registry_table import render_registry_table
from services.voice_service import get_voice_and_text, process_voice_command, generate_natural_voice, generate_scan_insights, detect_language
from core.history_management import (initialize_session_state, add_user_message, add_ai_message, get_chat_history)
import global_style
from config.app_config import app_config
from core import session_manager
from components.navigation import render_app_header
from core.voice_handler import handle_global_voice
from pages.voice_page import render_voice_page
from components.floating_mic import render_floating_mic

app_config()
initialize_session_state()
render_app_header()
render_voice_page()
render_floating_mic()
