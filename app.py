import streamlit as st
import streamlit.components.v1 as components
import json
import time
from core.agent import ask_gemini 
from services.db_service import upload_image_to_supabase, save_plant_to_db, fetch_all_plants
from components.registry_table import render_registry_table

# Imports para sa imong Voice & Chat Service
from services.voice_service import get_voice_and_text, process_voice_command, generate_natural_voice, generate_scan_insights, detect_language
from core.history_management import (
    initialize_session_state, add_user_message, add_ai_message, get_chat_history
)
from streamlit_mic_recorder import mic_recorder
import global_style

# --- CONFIG & INITIALIZATION ---
st.set_page_config(
    page_title="A.N.I.", 
    page_icon="🌱", 
    layout="wide",
    initial_sidebar_state="collapsed"
)
initialize_session_state()

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


# --- NAVIGATION BUTTONS (Big and obvious!) ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🎤 Kausap", use_container_width=True, 
                type="primary" if st.session_state.current_page == "voice" else "secondary"):
        st.session_state.current_page = "voice"
        st.rerun()

with col2:
    if st.button("📸 Plant Scanner", use_container_width=True,
                type="primary" if st.session_state.current_page == "scanner" else "secondary"):
        st.session_state.current_page = "scanner"
        st.rerun()

with col3:
    if st.button("📋 History", use_container_width=True,
                type="primary" if st.session_state.current_page == "history" else "secondary"):
        st.session_state.current_page = "history"
        st.rerun()

st.divider()

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

# ============================================
# PAGE: VOICE CHAT
# ============================================
if st.session_state.current_page == "voice":
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>💬 Kausapin si A.N.I.</p>
        <p class='page-subtitle'>Magtanong tungkol sa halaman</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Voice command hints
    with st.expander("🗣️ Mga pwedeng sabihin", expanded=False):
        st.markdown("""
        **Mga Tanong:**
        - "Ano ang sakit ng tanim ko?"
        - "Paano gamutin ang yellow leaves?"
        - "Kailan dapat diligan?"
        
        **Mga Command:**
        - "Pumunta sa scanner" / "Open scanner"
        - "Ipakita ang history" / "Show history"
        - "Burahin ang chat" / "Clear chat"
        """)
    
    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.info("👇 Pindutin ang **🎤 MIC** sa ibaba para magsimula!")
        else:
            for msg in st.session_state.messages[-10:]:  # Show last 10 messages
                if msg["role"] == "user":
                    with st.chat_message("user", avatar="🧑‍🌾"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant", avatar="🌱"):
                        st.write(msg["content"])
    
    if st.button("🗑️ Burahin Usapan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================
# PAGE: SCANNER
# ============================================
elif st.session_state.current_page == "scanner":
    
    # JavaScript to force BACK CAMERA on mobile! 📷
    components.html("""
    <script>
        try {
            const parent = window.parent;
            // Override getUserMedia to force back camera
            const originalGetUserMedia = parent.navigator.mediaDevices.getUserMedia.bind(parent.navigator.mediaDevices);
            parent.navigator.mediaDevices.getUserMedia = async (constraints) => {
                if (constraints && constraints.video) {
                    if (typeof constraints.video === 'boolean') {
                        constraints.video = { facingMode: { ideal: 'environment' } };
                    } else if (typeof constraints.video === 'object') {
                        constraints.video.facingMode = { ideal: 'environment' };
                    }
                }
                return originalGetUserMedia(constraints);
            };
            console.log('📷 Back camera mode enabled!');
        } catch(e) {
            console.log('Camera override error:', e);
        }
    </script>
    """, height=0)
    
    # Check if this was triggered by voice command
    if st.session_state.voice_triggered_scan:
        # Big flashing prompt!
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); 
                    padding: 25px; border-radius: 20px; text-align: center; 
                    margin-bottom: 20px; animation: pulse 1s infinite;'>
            <p style='font-size: 28px; color: white; margin: 0; font-weight: bold;'>
                � Kina-click ni A.N.I. ang camera...
            </p>
            <p style='font-size: 16px; color: rgba(255,255,255,0.9); margin: 10px 0 0 0;'>
                Sandali lang!
            </p>
        </div>
        <style>
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.02); }
            }
        </style>
        """, unsafe_allow_html=True)
        # Reset flag after showing
        st.session_state.voice_triggered_scan = False
    else:
        st.markdown("""
        <div class='page-header'>
            <p class='page-title'>📸 I-scan ang Halaman</p>
            <p class='page-subtitle'>Itutok sa dahon na may problema</p>
        </div>
        """, unsafe_allow_html=True)
    
    if "last_processed_file_id" not in st.session_state:
        st.session_state.last_processed_file_id = None

    img_file = st.camera_input("Pindutin para kumuha ng litrato")
    
    # Auto-click camera button using JavaScript! 🤖
    if st.session_state.auto_click_camera:
        st.session_state.auto_click_camera = False  # Reset flag
        
        # Use components.html to execute JavaScript (st.markdown doesn't run JS)
        components.html("""
        <script>
            // Access parent document (Streamlit's iframe parent)
            function clickCameraButton() {
                try {
                    // Get parent window
                    const parent = window.parent.document;
                    
                    // Find camera button
                    const cameraBtn = parent.querySelector('[data-testid="stCameraInput"] button');
                    
                    if (cameraBtn) {
                        console.log('Found camera button, clicking...');
                        cameraBtn.click();
                        
                        // Wait for camera to open, then click capture
                        setTimeout(() => {
                            const allButtons = parent.querySelectorAll('[data-testid="stCameraInput"] button');
                            allButtons.forEach(btn => {
                                // Click the capture/take photo button
                                if (btn.innerText.toLowerCase().includes('take') || 
                                    btn.querySelector('svg') ||
                                    btn.getAttribute('kind') === 'primary') {
                                    console.log('Clicking capture button...');
                                    btn.click();
                                }
                            });
                        }, 2500);
                    } else {
                        console.log('Camera button not found, retrying...');
                        setTimeout(clickCameraButton, 500);
                    }
                } catch(e) {
                    console.log('Error:', e);
                }
            }
            
            // Start after page loads
            setTimeout(clickCameraButton, 1500);
        </script>
        <p style="text-align:center; color: #22c55e; font-size: 14px;">
            🤖 A.N.I. is clicking the camera...
        </p>
        """, height=30)
    if img_file:
        current_file_id = f"{img_file.name}-{img_file.size}"
        if st.session_state.last_processed_file_id != current_file_id:
            st.session_state.last_processed_file_id = current_file_id
            
            with st.status("🔍 Sinusuri...", expanded=True) as status:
                st.write("☁️ Ina-upload...")
                image_url = upload_image_to_supabase(img_file)
                
                if image_url:
                    st.write("🧠 Pinag-aaralan ni A.N.I...")
                    img_file.seek(0)
                    ai_response = ask_gemini(img_file)
                    
                    # Debug: show raw response if there's an issue
                    if not ai_response or ai_response.startswith("Nasugamak") or ai_response.startswith("Error"):
                        st.error(f"AI Response Error: {ai_response}")
                        st.session_state.last_processed_file_id = None
                        status.update(label="❌ May problema", state="error", expanded=True)
                    else:
                        # Clean the JSON response
                        clean_json = ai_response.replace("```json", "").replace("```", "").strip()
                        
                        # Try to extract JSON if there's extra text
                        if "{" in clean_json:
                            start = clean_json.find("{")
                            end = clean_json.rfind("}") + 1
                            clean_json = clean_json[start:end]
                        
                        try:
                            analysis_data = json.loads(clean_json)
                            st.write("💾 Sine-save...")
                            save_plant_to_db(
                                plant_name=analysis_data.get("plant_name", "Unknown"),
                                image_url=image_url,
                                json_data=analysis_data,
                                farm_name="Main Field"
                            )
                            status.update(label="✅ Tapos na!", state="complete", expanded=False)
                            
                            plant_name = analysis_data.get('plant_name', 'Hindi kilala')
                            health = analysis_data.get('health_status', 'Unknown')
                            
                            if health == "Healthy":
                                st.success(f"🌿 **{plant_name}** - Malusog!")
                                st.balloons()
                            else:
                                st.warning(f"⚠️ **{plant_name}** - {health}")
                            
                            # 🎤 AUTO VOICE INSIGHTS! 
                            st.write("🎤 Generating voice insights...")
                            insights_text, insights_audio = generate_scan_insights(
                                analysis_data, 
                                st.session_state.user_language
                            )
                            
                            # Show the insights
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                                        padding: 20px; border-radius: 15px; margin: 15px 0;'>
                                <p style='color: white; font-size: 18px; margin: 0;'>
                                    🌱 <strong>A.N.I. says:</strong>
                                </p>
                                <p style='color: rgba(255,255,255,0.95); font-size: 16px; margin: 10px 0 0 0;'>
                                    {insights_text}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Auto-play voice!
                            if insights_audio:
                                st.audio(insights_audio, format="audio/wav", autoplay=True)
                            
                            # No rerun - prevent re-scanning!
                        except json.JSONDecodeError as e:
                            st.error(f"JSON Parse Error: {e}")
                            st.code(clean_json[:500], language="text")  # Show what we received
                            st.session_state.last_processed_file_id = None
                else:
                    st.error("Hindi na-upload ang image. Subukan ulit.")
                    st.session_state.last_processed_file_id = None

# ============================================
# PAGE: HISTORY
# ============================================
elif st.session_state.current_page == "history":
    st.markdown("""
    <div class='page-header'>
        <p class='page-title'>📋 Mga Na-scan na Halaman</p>
        <p class='page-subtitle'>Lahat ng record mo</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_registry_table()
    
    st.divider()
    st.info("💡 Sabihin: 'Pumunta sa scanner' para mag-scan ulit!")

# ============================================
# FLOATING MIC BUTTON (Always visible!)
# ============================================
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
            response_text, response_audio, command = handle_global_voice(audio_data['bytes'])
        
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