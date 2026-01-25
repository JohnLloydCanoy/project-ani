import os
from dotenv import load_dotenv

load_dotenv()

# 1. Define the System Prompt (The AI's Persona)
SYSTEM_PROMPT = """
You are ANI, an expert AI Agronomist 
dedicated to helping farmers in the Philippines. 
You provide clear, practical advice on crop diseases, soil health, and pest control.
Always be encouraging, professional, and concise.
"""

# 2. Define the Key Fetcher
def get_api_key():
    """
    Safely retrieves the API key from the .env file.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("❌ GEMINI_API_KEY not found in .env file!")
    return key