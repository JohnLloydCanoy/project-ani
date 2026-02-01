import streamlit as st
from streamlit_float import *
import streamlit.components.v1 as components # <--- 1. IMPORT THIS
from components.camera.picture.take_picture import take_picture_view
import datetime
from components.registry_table import render_registry_table

def dashboard_view():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: -50px;'>🌱 Project A.N.I.</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Katulong Mo sa Bukid</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.info("Welcome to Project A.N.I.! This platform is designed to assist farmers in the Philippines with expert agronomic advice.")
    st.write("---")
    
    st.markdown("""
        <style>
            div.stButton > button {
                border-radius: 50px;
                height: 60px;
                font-size: 20px;
                font-weight: bold;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            }
        </style>
        """, unsafe_allow_html=True)
    
    if "camera_open" not in st.session_state:
        st.session_state.camera_open = False
    if st.button("SCAN NOW! 📸", type="primary", use_container_width=True):
        st.session_state.camera_open = True
        st.rerun()
        
    if st.session_state.camera_open:
        st.markdown('<div id="camera-section"></div>', unsafe_allow_html=True)
        take_picture_view()
        components.html(
            """
            <script>
                window.parent.location.href = '#camera-section';
            </script>
            """,
            height=0,
            width=0
        )

    render_registry_table()
    
    st.write("---")

dashboard_view()