import streamlit as st

def view_digital_twin():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🌿 Digital Twin Registry</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Manage your digital twin records here.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    st.info("This section allows you to view and manage your digital twin records. You can see the details of each plant you've scanned and saved in your registry.")
    st.write("---")
    
    # Placeholder for digital twin registry content
    st.write("Digital Twin Registry content goes here...")

view_digital_twin()