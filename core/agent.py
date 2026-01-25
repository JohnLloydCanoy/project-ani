from google import genai
from google.genai import types
from config.settings import get_api_key, SYSTEM_PROMPT


api_key = get_api_key()
client = genai.Client(api_key=api_key)

def ask_gemini(chat_history):
    """
    Sends the message history to Gemini.
    """
    try:
        full_context = [SYSTEM_PROMPT] + chat_history
        
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=full_context
        )
        return response.text
    except Exception as e:
        return f"⚠️ Connection Error: {e}"


