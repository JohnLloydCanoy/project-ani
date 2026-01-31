import streamlit as st
from config.app_config import app_config
from streamlit_float import *

app_config()
float_init()

button_container = st.container()
with button_container:
    if st.button("TALK TO ANI 🎙️", type="primary", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()
button_container.float(
    "bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; z-index: 9999;"
)
