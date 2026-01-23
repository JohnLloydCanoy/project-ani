from google import genai
from config.settings import get_api_key, SYSTEM_PROMPT

api_key = get_api_key()
client = genai.Client(api_key=api_key)

def ask_gemini(chat_history):
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Use the stable 2.0 version
            contents=chat_history,
            config={
                'system_instruction': SYSTEM_PROMPT,
                'temperature': 0.7,
            }
        )
        return response.text
    except Exception as e:
        # Better error handling for the 429 quota issue
        if "429" in str(e):
            return "⚠️ A.N.I. is busy (Rate Limit). Please wait 10 seconds."
        return f"⚠️ Connection Error: {e}"