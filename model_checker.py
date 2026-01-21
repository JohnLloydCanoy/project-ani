from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

try:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    print("✅ Successfully connected with API Key.\n")
    print("🔍 Listing available models for you:")
    print("-" * 40)
    for m in client.models.list():
        print(f" • {m.name}")
    print("-" * 40)
    print("👉 Look for 'gemini-3.0-flash-preview' or 'gemini-3.0-pro-exp' above.")
except Exception as e:
    print(f"❌ Error: {e}")