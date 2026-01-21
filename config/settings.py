from google import genai
from config.settings import get_api_key, SYSTEM_PROMPT

api_key = get_api_key()
client = genai.Client(api_key=api_key)