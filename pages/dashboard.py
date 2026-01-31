import streamlit as st

def dashboard_view():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🌱 Project A.N.I.</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Katulong Mo sa Bukid</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.button("Home", on_click=lambda: st.session_state.update(page="dashboard"))
    st.button("talk to ANI", on_click=lambda: st.session_state.update(page="chat"))
    st.button("Go to Scan", on_click=lambda: st.session_state.update(page="scan"))
    st.button("View Registry", on_click=lambda: st.session_state.update(page="registry"))