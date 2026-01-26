import streamlit as st
import streamlit.components.v1 as components
from components.camera.picture.style_take_picture import get_picture_camera_html, get_picture_camera_styles


def open_picture_camera():
    """Opens the camera for taking pictures and manages state. Returns True if camera is active."""
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    
    # Check if user clicked close via query param
    query_params = st.query_params
    if query_params.get("close_camera") == "true":
        st.session_state.camera_active = False
        st.query_params.clear()
        st.rerun()
    
    # Check if photo was captured
    if query_params.get("photo_captured") == "true":
        st.session_state.camera_active = False
        st.session_state.photo_pending = True
        st.query_params.clear()
        st.rerun()

    if not st.session_state.camera_active:
        if st.button("📸 Take Photo"):
            st.session_state.camera_active = True
            st.rerun()
        return False
    
    return True

def take_picture():
    """Opens camera and takes a picture. Returns the captured image or None."""
    camera_is_active = open_picture_camera()
    
    if not camera_is_active:
        return None
    st.markdown(get_picture_camera_styles(), unsafe_allow_html=True)
    close_button_html = """
    <style>
        .close-camera-btn {
            position: fixed !important;
            top: 20px !important;
            left: 15px !important;
            z-index: 9999999 !important;
            background: #dc3545 !important;
            color: white !important;
            border: 3px solid white !important;
            border-radius: 50% !important;
            width: 50px !important;
            height: 50px !important;
            font-size: 26px !important;
            font-weight: bold !important;
            cursor: pointer !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
            text-decoration: none !important;
        }
        .close-camera-btn:hover {
            background: #c82333 !important;
        }
    </style>
    <a class="close-camera-btn" href="/?close_camera=true" target="_self">✕</a>
    """
    st.markdown(close_button_html, unsafe_allow_html=True)
    
    # Render the camera component
    components.html(get_picture_camera_html(), height=2000, scrolling=False)
    
    return None