import streamlit as st

def render_app_header():
    # --- APP HEADER ---
    st.markdown("""
    <div style='text-align: center; padding: 5px 0 15px 0;'>
        <h1 style='font-size: 32px; margin: 0;'>🌱 A.N.I.</h1>
        <p style='font-size: 14px; color: #666; margin: 3px 0 0 0;'>Katulong Mo sa Bukid</p>
    </div>
    """, unsafe_allow_html=True)
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