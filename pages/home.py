import streamlit as st

def dashboard_view():
    st.set_page_config(
        page_title="Project A.N.I.",
        page_icon="🌱",
        layout="wide"
    )
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🌱 Project A.N.I.</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Katulong Mo sa Bukid</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    # Create 4 equal columns
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.button("Home", on_click=lambda: st.session_state.update(page="dashboard"), use_container_width=True)
    with c2:
        st.button("Talk to ANI", on_click=lambda: st.session_state.update(page="chat"), use_container_width=True)
    with c3:
        st.button("Go to Scan", on_click=lambda: st.session_state.update(page="scan"), use_container_width=True)
    with c4:
        st.button("Registry", on_click=lambda: st.session_state.update(page="registry"), use_container_width=True)