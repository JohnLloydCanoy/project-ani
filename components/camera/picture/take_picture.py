import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
from style_take_picture import get_picture_camera_html, get_picture_camera_styles


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

    if not st.session_state.camera_active:
        if st.button("📸 Open Camera"):
            st.session_state.camera_active = True
            st.rerun()
        return False
    
    return True

def take_picture():
    """Opens camera and takes a picture. Returns the captured image or None."""
    camera_is_active = open_picture_camera()
    
    if not camera_is_active:
        return None
    
    # Apply styles to hide Streamlit UI
    st.markdown(get_picture_camera_styles(), unsafe_allow_html=True)
    
    # Render the camera component - use a very large height
    components.html(get_picture_camera_html(), height=2000, scrolling=False)
    
    return None