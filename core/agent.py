import google.generativeai as genai
import streamlit as st
from PIL import Image
from config.settings import get_api_key

# 1. I-configure ang Gemini gamit ang key gikan sa secrets.toml
api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)

# Gigamit ang Gemini 3 Flash para sa Hackathon 3.0!
model = genai.GenerativeModel("gemini-3-pro-preview")

def ask_gemini(input_data):
    """
    Kini nga function mo-handle og duha ka butang:
    1. Image analysis para sa scanner.
    2. Text chat history para sa AI Support.
    """
    try:
        # Check kon ang input kay listahan (Chat History)
        if isinstance(input_data, list):
            response = model.generate_content(input_data)
            return response.text

        # Check kon image file (Scanner Mode)
        if input_data:
            input_data.seek(0)
            image = Image.open(input_data)
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
            
        return "Error: No valid input provided."
        
    except Exception as e:
        return f"Nasugamak sa sayop sa Gemini: {e}"