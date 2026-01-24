import time
import random
from google import genai
from google.genai import types
from config.settings import get_api_key, SYSTEM_PROMPT

client = genai.Client(api_key=get_api_key())

def ask_gemini(chat_history):
    attempt = 0
    while True: # Infinite loop hanggang mag-success
        try:
            response = client.models.generate_content(
                model='gemini-3-flash-preview', 
                contents=chat_history,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    thinking_config=types.ThinkingConfig(
                        thinking_level="low"
                    )
                )
            )
            return response.text # Kapag nag-success, lalabas na siya sa loop
            
        except Exception as e:
            error_msg = str(e)
            attempt += 1
            
            # Check kung 429 (Rate Limit) o 500+ (Server Overloaded)
            if "429" in error_msg or "500" in error_msg or "503" in error_msg:
                # Exponential backoff: naghihintay ng mas matagal bawat fail
                # 2s, 4s, 8s, 16s... hanggang max 30 seconds
                wait_time = min(2 ** attempt + random.uniform(0, 1), 30)
                
                # Visual feedback sa terminal/console para alam mong gumagana pa
                print(f"🔄 A.N.I. is retrying (Attempt {attempt}). Waiting {wait_time:.1f}s...")
                
                time.sleep(wait_time)
                continue # Balik sa taas ng loop para itry ulit
            
            # Kung ibang klaseng error (halimbawa: Connection Error), return error na lang
            return f"⚠️ Connection Error: {error_msg}. Pakicheck po ang internet."