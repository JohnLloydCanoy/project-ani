import google.generativeai as genai
import streamlit as st
from PIL import Image
import json

# 'gemini-3-pro-preview' is best for deep diagnosis (Visual Reasoning)
# 'gemini-3-flash-preview' is best for fast voice/chat

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3-flash-preview")

# Core function for intereaction itself in the system 
def ani_agent(prompt):
    """
        The Brain of ANI.
        - prompt: The user's new question.
        - chat_history: The previous conversation (so it remembers context).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {e}"

# This function for image analysis
def ask_gemini(image_file):
    """
    Accepts an uploaded file object, converts it to an image,
    and asks Gemini to analyze it for plant health.
    """
    try:
        if not image_file:
            return "Error: No image provided."
        image_file.seek(0)
        image = Image.open(image_file)
        prompt = """
        You are an expert Agronomist (Project A.N.I.). 
        Analyze this plant image.
        
        Return ONLY a JSON object with this exact structure (no markdown):
        {
            "plant_name": "Common Name (Scientific Name)",
            "health_status": "Healthy" or "Name of Disease",
            "action_plan": "One short sentence on what to do.",
            "confidence": 0.95,
            "category": "Crop" or "Weed" or "Ornamental"
        }
        """
        response = model.generate_content([prompt, image])
        
        return response.text
        
    except Exception as e:
        return f"Error connecting to Gemini: {e}"
    
def ask_gemini_chat(user_question):
    """
    New function for the "Talk to ANI" page.
    Expects Text -> Returns Text.
    """
    try:
        system_instruction = """
        You are A.N.I. (Agricultural Network Intelligence), a friendly and expert farming assistant for the Philippines.
        - Answer questions about farming, crops, and pests.
        - Keep answers concise and helpful.
        - If asked about non-farming topics, politely guide them back to agriculture.
        """
        full_prompt = f"{system_instruction}\n\nUser: {user_question}\nANI:"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Sorry, I couldn't connect to the server. ({e})"
    
    