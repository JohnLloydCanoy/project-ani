import google.generativeai as genai
import streamlit as st
from PIL import Image
# 
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3-flash-preview")

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