import streamlit as st

def initialize_app_state():
# Initialize app state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "voice"  # Default to voice chat
    if "show_history" not in st.session_state:
        st.session_state.show_history = False
    # Track processed audio to prevent duplicate API calls
    if "last_audio_id" not in st.session_state:
        st.session_state.last_audio_id = None
    if "last_voice_response" not in st.session_state:
        st.session_state.last_voice_response = None
    # Flag for voice-triggered scan
    if "voice_triggered_scan" not in st.session_state:
        st.session_state.voice_triggered_scan = False
    # Flag to auto-click camera button
    if "auto_click_camera" not in st.session_state:
        st.session_state.auto_click_camera = False
    # User language preference (detected from voice)
    if "user_language" not in st.session_state:
        st.session_state.user_language = "tagalog"  # Default
    # Store scan result for voice insights
    if "pending_scan_insights" not in st.session_state:
        st.session_state.pending_scan_insights = None