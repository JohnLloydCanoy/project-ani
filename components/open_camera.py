import streamlit as st
from PIL import Image
import streamlit.components.v1 as components


def pic_button():
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    
    # Check if user clicked close via query param hack
    query_params = st.query_params
    if query_params.get("close_camera") == "true":
        st.session_state.camera_active = False
        st.query_params.clear()
        st.rerun()

    if not st.session_state.camera_active:
        if st.button("📸 Open Camera"):
            st.session_state.camera_active = True
            st.rerun()
        return None
    
    if st.session_state.camera_active:
        st.markdown("""
            <style>
                /* RESET: Hide ALL Streamlit UI */
                header, footer, [data-testid="stSidebar"], 
                [data-testid="stHeader"], [data-testid="stToolbar"],
                .stDeployButton, #MainMenu {
                    display: none !important;
                    visibility: hidden !important;
                }
                
                /* RESET: Remove ALL margins/padding */
                html, body, [data-testid="stAppViewContainer"], 
                [data-testid="stMain"], .main, .block-container,
                [data-testid="stVerticalBlock"] {
                    padding: 0 !important;
                    margin: 0 !important;
                    max-width: 100vw !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    overflow: hidden !important;
                }
                
                /* CAMERA CONTAINER: Fixed Fullscreen */
                [data-testid="stCameraInput"] {
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    right: 0 !important;
                    bottom: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    z-index: 99999 !important;
                    background: #000 !important;
                    display: flex !important;
                    flex-direction: column !important;
                }
                
                /* VIDEO: Stretch to fill screen */
                [data-testid="stCameraInput"] > div {
                    flex: 1 !important;
                    display: flex !important;
                    flex-direction: column !important;
                    height: 100% !important;
                }
                
                [data-testid="stCameraInput"] video {
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100vw !important;
                    height: 100vh !important;
                    object-fit: cover !important;
                    z-index: 1 !important;
                }
                
                /* TAKE PHOTO BUTTON: Bottom of screen */
                [data-testid="stCameraInput"] button {
                    position: fixed !important;
                    bottom: 30px !important;
                    left: 50% !important;
                    transform: translateX(-50%) !important;
                    z-index: 100001 !important;
                    padding: 15px 40px !important;
                    font-size: 18px !important;
                    border-radius: 30px !important;
                    background: rgba(255,255,255,0.9) !important;
                    color: #000 !important;
                    border: none !important;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
                }
                
                /* Hide Streamlit's default button styling container */
                [data-testid="stCameraInput"] img {
                    display: none !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # --- INJECT CLOSE BUTTON DIRECTLY INTO PARENT DOCUMENT ---
        st.markdown("""
            <style>
                #custom-close-btn {
                    position: fixed !important;
                    top: 20px !important;
                    left: 20px !important;
                    z-index: 999999999 !important;
                    background: #dc3545 !important;
                    color: white !important;
                    border: 3px solid white !important;
                    border-radius: 50% !important;
                    width: 60px !important;
                    height: 60px !important;
                    font-size: 32px !important;
                    font-weight: bold !important;
                    cursor: pointer !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
                    -webkit-tap-highlight-color: transparent !important;
                }
                #custom-close-btn:active {
                    background: #a71d2a !important;
                    transform: scale(0.9) !important;
                }
            </style>
            <a id="custom-close-btn" href="?close_camera=true" target="_self">✕</a>
        """, unsafe_allow_html=True)

        # --- THE CAMERA INPUT ---
        img_file_buffer = st.camera_input("Take a picture", label_visibility="collapsed")
        
        if img_file_buffer is not None:
            image = Image.open(img_file_buffer)
            st.session_state.camera_active = False
            st.rerun()
            return image
            
    return None