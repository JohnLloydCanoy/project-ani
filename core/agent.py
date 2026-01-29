import google.generativeai as genai
from config.settings import get_api_key, SYSTEM_PROMPT

api_key = get_api_key()
genai.configure(api_key=api_key)

api_key = get_api_key()
genai.configure(api_key=api_key)


model = genai.GenerativeModel(
    model_name="gemini-3-flash-preview",
    system_instruction=SYSTEM_PROMPT
)

def ask_gemini(chat_history):
    """
    Sends the message to Gemini.
    Note: chat_history should be a list of strings or dicts depending on your implementation.
    """
    try:
        # If chat_history is just text, we can send it directly.
        # If it's a list of previous messages, we might need to format it.
        # For a simple Q&A, we just send the latest prompt or history string.
        response = model.generate_content(chat_history)
        return response.text
        
    except Exception as e:
        return f"⚠️ Connection Error: {e}"


