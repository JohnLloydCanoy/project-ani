import streamlit as st

def render_app_header():
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
        # --- APP HEADER ---
    st.title("🌱 A.N.I.")
    st.caption("Katulong Mo sa Bukid, 24/7 Agronomy Assistant")