import streamlit as st

# ============================================
# GLOBAL VOICE INPUT (Always at bottom!)
# ============================================
# This processes voice from the floating mic
def handle_global_voice(audio_bytes):
    """Process voice and handle commands."""
    history = get_chat_history()
    response_text, response_audio, command, detected_lang = process_voice_command(audio_bytes, history)
    
    # Save detected language for scan insights!
    st.session_state.user_language = detected_lang
    
    # Handle navigation commands
    if command:
        if command == "GO_SCANNER" or command == "TAKE_PHOTO":
            st.session_state.current_page = "scanner"
            st.session_state.voice_triggered_scan = True
            st.session_state.auto_click_camera = True  # Auto-click the button!
            st.toast("📸 Binubuksan ang camera...", icon="📸")
        elif command == "GO_VOICE":
            st.session_state.current_page = "voice"
            st.toast("🎤 Pupunta sa Voice Chat!", icon="🎤")
        elif command == "GO_HISTORY":
            st.session_state.current_page = "history"
            st.toast("📋 Pupunta sa History!", icon="📋")
        elif command == "CLEAR_CHAT":
            st.session_state.messages = []
            st.toast("🗑️ Na-clear na ang usapan!", icon="🗑️")
    
    return response_text, response_audio, command
