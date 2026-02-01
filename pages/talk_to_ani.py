import streamlit as st
import time
from core.agent import ask_gemini 

def talk_to_ani_view():
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🎙️ Talk to A.N.I.</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Get expert agronomic advice from A.N.I.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am A.N.I. How can I help you with your farm today?"}
        ]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Type your question for A.N.I. here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("A.N.I. is thinking..."):
                response = ask_gemini(prompt)
                time.sleep(1)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
talk_to_ani_view()