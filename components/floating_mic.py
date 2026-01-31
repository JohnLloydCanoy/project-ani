# ============================================
# FLOATING MIC BUTTON (Always visible!)
# ============================================
from time import time
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from core.history_management import add_ai_message, add_user_message
from core.voice_handler import handle_global_voice

def render_floating_mic():
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                padding: 15px 20px; border-radius: 15px; text-align: center; margin-top: 10px;'>
        <p style='color: white; font-size: 16px; margin: 0 0 10px 0;'>
            🎤 <strong>Pindutin at Magsalita</strong> - Pwede ring mag-command!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # The actual mic recorder
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        audio_data = mic_recorder(
            start_prompt="🎤 MAGSALITA", 
            stop_prompt="⏹️ TAPOS NA", 
            just_once=True, 
            key='global_mic',
            use_container_width=True
        )

    # Process voice input - ONLY ONCE per recording!
    if audio_data and audio_data['bytes']:
        # Create unique ID for this audio
        audio_id = hash(audio_data['bytes'][:100])  # Hash first 100 bytes as ID
        
        # Only process if this is a NEW audio (not already processed)
        if st.session_state.last_audio_id != audio_id:
            st.session_state.last_audio_id = audio_id
            
            with st.spinner("🧠 Iniisip ni A.N.I..."):
                response_text, response_audio, command, detected_lang = handle_global_voice(audio_data['bytes'])
            
            # Save response to session state
            st.session_state.last_voice_response = {
                "text": response_text,
                "audio": response_audio,
                "command": command
            }
            
            # Save to history
            add_user_message("🎤 Voice message")
            add_ai_message(response_text)
            
            # Rerun if command was executed
            if command:
                time.sleep(1)
                st.rerun()
        
        # Display the response (from session state to avoid re-processing)
        if st.session_state.last_voice_response:
            resp = st.session_state.last_voice_response
            with st.chat_message("assistant", avatar="🌱"):
                st.markdown(f"**{resp['text']}**")
                if resp['audio']:
                    st.audio(resp['audio'], format="audio/wav", autoplay=True)