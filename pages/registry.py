import streamlit as st
import json
import time
from core.agent import ask_gemini
from services.db_service import upload_image_to_supabase, save_plant_to_db 
from components.registry_table import render_registry_table

render_registry_table()