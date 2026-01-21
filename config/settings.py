from google import genai
from config.settings import get_api_key, SYSTEM_PROMPT

api_key = get_api_key()
client = genai.Client(api_key=api_key)

def ask_gemini(user_message):
    """Sends a message to Gemini 3.0 and gets the text response."""
    try:
        response = client.models.generate_content(
            model='gemini-3.0-flash-preview', # or if the code is having an error, change to this gemini-3.0-pro-exp
            contents=[SYSTEM_PROMPT, user_message]
        )
        return response.text
    except Exception as e:
        return f"Error connecting to AI: {e}"