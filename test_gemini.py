import streamlit as st
import google.generativeai as genai

st.title("🔌 Gemini Connection Tester")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    st.success("✅ API Key found in secrets.toml")
except Exception as e:
    st.error(f"❌ Key Missing: {e}")
    st.stop()

try:
    genai.configure(api_key=api_key)
    

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Hello Farmer' if you can hear me.")
    
    if response.text:
        st.success(f"✅ CONNECTION SUCCESSFUL!")
        st.info(f"Gemini Replied: {response.text}")
    else:
        st.warning("⚠️ Connected, but no text returned.")
        
except Exception as e:
    st.error(f"❌ Connection Failed: {e}")