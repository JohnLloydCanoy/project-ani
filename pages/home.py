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
