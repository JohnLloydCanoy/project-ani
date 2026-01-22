import streamlit as st
from dotenv import load_dotenv
from core.agent import ask_gemini
from core.history_management import (
    initialize_session_state, 
    add_user_message, 
    add_ai_message, 
    get_chat_history
)
from services.vision_service import (pic_button,)  # Importing the modified vision_service
from PIL import Image

load_dotenv()
st.set_page_config(
    page_title="Project A.N.I.",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar 
with st.sidebar:
    st.title("🌱 Project A.N.I.")
    st.caption("Agricultural Network Intelligence")
    st.markdown("---")
    st.write("System Status: **Online** 🟢")

# Main Title
st.title("Hi! Welcome to Project A.N.I. 👋")
st.write("I am your AI Agronomist. Ask me anything about your crops!")

# --- THE CHAT LOGIC STARTS HERE ---

initialize_session_state()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        

if "camera_key" not in st.session_state:
    st.session_state["camera_key"] = 0

# --- LAYOUT START ---

# 2. Camera Popover
# We use a popover to hide the large camera view until the user wants it.
# This keeps your UI clean.
camera_buffer = None
with st.popover("📸 Open Camera", use_container_width=True):
    camera_buffer = st.camera_input(
        "Take a picture of the crop/plant", 
        key=f"camera_{st.session_state['camera_key']}"
    )

# 3. Standard Chat Input
user_input = st.chat_input("Ask about this image...")

# --- LOGIC START ---

# Trigger if EITHER text is sent OR a picture was just taken
if user_input or camera_buffer:
    
    with st.chat_message("user"):
        # 4. Handle the Image
        if camera_buffer:
            # Display the captured image in the chat
            st.image(camera_buffer, caption="Captured Image", width=300)
            
            # Convert to PIL Image for your AI processing later
            # (You will need this for the Gemini API)
            pil_image = Image.open(camera_buffer)
            
        # 5. Handle the Text
        if user_input:
            st.write(user_input)
        elif camera_buffer:
            # If they took a photo but didn't type text, add default text
            user_input = "Analyze this image."
            st.write(user_input)

    # 6. Save messages to memory
    # add_user_message(user_input, image=camera_buffer)

    # 7. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing agricultural data..."):
            
            # Pass the 'camera_buffer' (or pil_image) to your function
            # response = ask_gemini(history_context, image=camera_buffer)
            
            response = "Image received! (Simulated response)"
            st.write(response)
            
    # 8. Reset the Camera
    # This ensures the camera is ready for a fresh photo next time
    st.session_state["camera_key"] += 1
    st.rerun()