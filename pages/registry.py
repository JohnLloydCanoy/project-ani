import streamlit as st
import json
import time
from core.agent import ask_gemini
from services.db_service import upload_image_to_supabase, save_plant_to_db 
from components.registry_table import render_registry_table

def registry_view():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>📋 Registry</h2>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.info("This section allows you to view and manage your plant records. You can see the details of each plant you've scanned and saved in your registry.")
    st.write("---")
    render_registry_table()
    
registry_view()