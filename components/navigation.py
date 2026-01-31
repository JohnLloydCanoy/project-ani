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
        if st.button("📋 Registered Plants", use_container_width=True,
                    type="primary" if st.session_state.current_page == "history" else "secondary"):
            st.session_state.current_page = "history"
            st.rerun()
    st.divider()
    # --- DYNAMIC APP HEADER BASED ON CURRENT PAGE ---
    if st.session_state.current_page == "voice":
        st.title("🌱 A.N.I. - Voice Chat")
        st.caption("Kausapin si A.N.I. tungkol sa halaman")
    elif st.session_state.current_page == "scanner":
        st.title("🌱 A.N.I. - Plant Scanner")
        st.caption("I-scan ang halaman para malaman ang sakit")
    elif st.session_state.current_page == "history":
        st.title("🌱 A.N.I. - History")
        st.caption("Mga na-scan na halaman")
    else:
        st.title("🌱 A.N.I.")
        st.caption("Katulong Mo sa Bukid, 24/7 Agronomy Assistant")