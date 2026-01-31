import streamlit as st
from streamlit_float import *
from components.camera.picture.take_picture import take_picture_view

def dashboard_view():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🌱 Project A.N.I.</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Katulong Mo sa Bukid</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.info("Welcome to Project A.N.I.! This platform is designed to assist farmers in the Philippines with expert agronomic advice. Navigate through the tools using the sidebar to scan plants, talk to ANI, and manage your digital twin registry.")
    st.write("---")
    
    st.markdown("""
        <style>
            div.stButton > button {
                border-radius: 50px;    /* Extremely rounded corners */
                height: 60px;           /* Taller button */
                font-size: 20px;        /* Bigger text */
                font-weight: bold;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Initialize camera state
    if "camera_open" not in st.session_state:
        st.session_state.camera_open = False
    
    # Toggle camera when button is clicked
    if st.button("SCANNED NOW! 📸", type="primary", use_container_width=True):
        st.session_state.camera_open = True
        st.rerun()
    
    # Show camera view only when activated
    if st.session_state.camera_open:
        take_picture_view()
    
    st.write("---")
    
    float_init()
    button_container = st.container()
    with button_container:
        if st.button("TALK TO ANI 🎙️", type="primary", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    button_container.float(
        "bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 9999;"
    )

# Call the function to render the page
dashboard_view()