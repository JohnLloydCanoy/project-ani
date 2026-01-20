import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

st.set_page_config(
    page_title="Project A.N.I.",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set the page configuration
st.title("HI Welcome to Project Ani 👋")
st.write("System is online and running.")
