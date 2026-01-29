import streamlit as st
import google.generativeai as genai

st.title("🔌 Gemini Connection & Model Tester")


try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    st.success("✅ Successfully connected with API Key.")
except Exception as e:
    st.error(f"❌ Key Error: {e}")
    st.stop()

st.subheader("🔍 Listing Available Models")
st.write("Fetching list from Google...")

try:

    models = list(genai.list_models())
    chat_models = [m for m in models if 'generateContent' in m.supported_generation_methods]

    if chat_models:
        st.markdown("### 🤖 Chat & Vision Models:")
        for m in chat_models:
            st.code(f"{m.name}")
            
        st.caption(f"Total models found: {len(models)}")
    else:
        st.warning("Connected, but no models found with 'generateContent' capability.")

except Exception as e:
    st.error(f"❌ Error fetching models: {e}")