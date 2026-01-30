import io
import wave
import struct
import re
import streamlit as st
from google import genai
from google.genai import types
from config.settings import get_api_key, SYSTEM_PROMPT
from services.db_service import fetch_all_plants

# Gemini Client
client = genai.Client(api_key=get_api_key())

# Command patterns (Tagalog, Bisaya, English)
COMMAND_PATTERNS = {
    "GO_SCANNER": [
        r"(pumunta|punta|go|open|buksan|click|i-?click).*(scanner|camera|kamera)",
        r"(scanner|camera|kamera).*(pumunta|punta|go|open|buksan|click)",
        r"^scanner$", r"^camera$",
    ],
    "TAKE_PHOTO": [
        # Direct commands to take photo/scan
        r"(mag-?scan|scan|i-?scan)",
        r"(kumuha|kunan|take|capture).*(litrato|picture|photo|pic)",
        r"(litrato|picture|photo).*(kumuha|take|capture)",
        r"^scan$", r"^picture$", r"^litrato$", r"^photo$",
        r"(check|tingnan|suriin).*(halaman|plant|tanim|dahon|leaf)",
        r"(ano|what).*(sakit|disease|problem).*(halaman|plant|tanim|ito|nito|yan)",
        r"(anong|what).*(halaman|plant|tanim).*(ito|yan|this)",
        r"i-?check.*(ito|yan|this)",
    ],
    "GO_VOICE": [
        r"(pumunta|punta|go|open|buksan|click).*(chat|voice|kausap|usap)",
        r"(chat|voice|kausap|usap).*(pumunta|punta|go|open|buksan)",
        r"^chat$", r"^voice$",
        r"gusto.*(mag-?usap|kausap|chat)",
    ],
    "GO_HISTORY": [
        r"(pumunta|punta|go|open|buksan|show|ipakita|tingnan).*(history|record|lista|list|registry)",
        r"(history|record|lista|list|registry).*(pumunta|show|ipakita|tingnan)",
        r"^history$", r"^records?$", r"^lista$",
        r"(ano|what).*(na-?scan|ni-?scan|scanned)",
        r"mga.*(halaman|plant|tanim).*(ko|namin|natin)",
    ],
    "CLEAR_CHAT": [
        r"(burahin|clear|delete|tanggalin|linisin).*(chat|usapan|conversation|history)",
        r"(chat|usapan|conversation).*(burahin|clear|delete|tanggalin)",
        r"^clear$", r"^burahin$",
        r"(fresh|bago|bagong).*(usapan|chat|start)",
    ],
}

def detect_command(text):
    """Detect if the text contains a voice command."""
    text_lower = text.lower().strip()
    
    for command, patterns in COMMAND_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return command
    return None


def detect_language(text):
    """
    Detect if text is Tagalog, Bisaya/Cebuano, or English.
    Returns: 'tagalog', 'bisaya', or 'english'
    """
    text_lower = text.lower()
    
    # Bisaya/Cebuano keywords
    bisaya_words = [
        "unsa", "asa", "kinsa", "kanus-a", "ngano", "pila", "unsaon",
        "dili", "wala", "naa", "adto", "diri", "didto", "kanang", "kini",
        "ako", "ikaw", "siya", "kita", "kami", "sila", "nimo", "niya",
        "maayo", "dako", "gamay", "taas", "mubo", "bag-o", "daan",
        "kaon", "inom", "tulog", "lakaw", "dagan", "lingkod", "barog",
        "salamat", "oo", "ayaw", "palihug", "bitaw", "mao", "lagi",
        "gi-", "na-", "mag-", "nag-", "mo-", "mi-", "ma-",
        "tanom", "halaman", "sakit", "liso", "dahon",
        "unsay", "kiniy", "kana", "ato", "atong", "imong", "iyang"
    ]
    
    # Tagalog keywords  
    tagalog_words = [
        "ano", "saan", "sino", "kailan", "bakit", "magkano", "paano",
        "hindi", "wala", "may", "meron", "dito", "doon", "ito", "iyan", "iyon",
        "ako", "ikaw", "siya", "tayo", "kami", "sila", "mo", "ko", "niya",
        "mabuti", "malaki", "maliit", "mataas", "mababa", "bago", "luma",
        "kain", "inom", "tulog", "lakad", "takbo", "upo", "tayo",
        "salamat", "opo", "huwag", "paki", "talaga", "nga", "ba",
        "nag-", "mag-", "na-", "ma-", "i-", "um-", "-in",
        "halaman", "sakit", "dahon", "prutas", "gulay",
        "gusto", "kailangan", "puwede", "dapat"
    ]
    
    # Count matches
    bisaya_count = sum(1 for word in bisaya_words if word in text_lower)
    tagalog_count = sum(1 for word in tagalog_words if word in text_lower)
    
    # Bisaya-specific patterns (more unique)
    if re.search(r"\b(unsa|naa|dili|mao|bitaw|lagi|gi-|atong|imong)\b", text_lower):
        bisaya_count += 3
    
    # Tagalog-specific patterns
    if re.search(r"\b(ano|hindi|meron|talaga|paki|gusto|kailangan)\b", text_lower):
        tagalog_count += 3
    
    # Determine language
    if bisaya_count > tagalog_count and bisaya_count >= 2:
        return "bisaya"
    elif tagalog_count >= 2:
        return "tagalog"
    else:
        return "tagalog"  # Default to Tagalog

def generate_natural_voice(text):
    """
    Generate natural-sounding voice using Gemini TTS.
    Much better than robotic gTTS!
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"  # Friendly female voice
                        )
                    )
                )
            )
        )
        
        # Extract audio data
        audio_data = response.candidates[0].content.parts[0].inline_data.data
        
        # Convert to WAV format
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(audio_data)
        
        wav_buffer.seek(0)
        return wav_buffer.read()
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

def get_voice_and_text(audio_bytes, history):
    """
    Process voice input and return text + natural voice response.
    """
    try:
        # 1. Get context from database
        plants = fetch_all_plants()
        latest = plants[0] if plants else None
        
        current_context = "Ang mag-uuma naa sa dashboard."
        if latest:
            current_context = (
                f"Ang pinakabag-o nga gi-scan mao ang {latest['plant_name']} "
                f"nga naay health status nga {latest['health_status']}."
            )

        # 2. Get AI response from Gemini 3!
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                f"{SYSTEM_PROMPT}\n\nKAHIMTANG KARON: {current_context}", 
                *history, 
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ]
        )
        
        response_text = response.text
        
        # 3. Generate natural voice
        response_audio = generate_natural_voice(response_text)
        
        return response_text, response_audio
        
    except Exception as e:
        return f"Pasensya, may error: {e}", None

def process_voice_command(audio_bytes, history):
    """
    Process voice input, detect commands, and return response.
    Returns: (response_text, response_audio, command_or_none, detected_language)
    """
    try:
        # 1. Get context from database
        plants = fetch_all_plants()
        latest = plants[0] if plants else None
        
        current_context = "Ang farmer ay nasa dashboard."
        if latest:
            current_context = (
                f"Ang pinakabagong na-scan ay {latest['plant_name']} "
                f"na may health status na {latest['health_status']}."
            )

        # 2. Enhanced system prompt for command detection
        enhanced_prompt = f"""{SYSTEM_PROMPT}

KASALUKUYANG SITWASYON: {current_context}

MAHALAGA - VOICE COMMANDS:
Kung ang farmer ay nagbigay ng command (hindi tanong), sumagot ng maikli at friendly:

- Kung gusto MAG-SCAN o KUMUHA NG LITRATO: Sabihin "Sige, buksan ko ang camera! I-tap mo lang ang button para mag-scan!"
- Kung gusto pumunta sa SCANNER: Sabihin "Sige, pupunta tayo sa scanner!" 
- Kung gusto pumunta sa HISTORY: Sabihin "Okay, ipapakita ko ang mga record mo!"
- Kung gusto pumunta sa CHAT/VOICE: Sabihin "Sige, dito lang ako para makausap!"
- Kung gusto CLEAR/BURAHIN ang chat: Sabihin "Okay, binubura ko na ang usapan!"

Para sa mga TANONG tungkol sa halaman, sumagot ng helpful at maikli lang (2-3 sentences max).
Gumamit ng simple Tagalog na madaling maintindihan ng farmer.

MAHALAGA: Sumagot sa PAREHONG WIKA ng farmer. Kung siya ay nagsasalita ng Bisaya/Cebuano, sumagot sa Bisaya. Kung Tagalog, sumagot sa Tagalog.
"""

        # 3. Get AI response from Gemini 3 (transcribe + respond)
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[
                enhanced_prompt,
                *history, 
                types.Part.from_bytes(data=audio_bytes, mime_type='audio/wav')
            ]
        )
        
        response_text = response.text
        
        # 4. Detect command from the AI's response
        command = None
        response_lower = response_text.lower()
        
        # Check AI response for command acknowledgment - TAKE_PHOTO first (more specific)
        if any(word in response_lower for word in ["scan", "litrato", "picture", "camera", "kumuha", "i-tap", "button"]):
            if any(word in response_lower for word in ["sige", "okay", "buksan", "ready", "go"]):
                command = "TAKE_PHOTO"
        elif any(word in response_lower for word in ["scanner"]):
            if any(word in response_lower for word in ["pumunta", "punta", "sige", "okay", "go"]):
                command = "GO_SCANNER"
        elif any(word in response_lower for word in ["history", "record", "lista", "registry"]):
            if any(word in response_lower for word in ["ipakita", "show", "sige", "okay", "pumunta"]):
                command = "GO_HISTORY"
        elif any(word in response_lower for word in ["bura", "clear", "delete", "linis"]):
            command = "CLEAR_CHAT"
        elif any(word in response_lower for word in ["chat", "kausap", "usap"]):
            if any(word in response_lower for word in ["pumunta", "sige", "okay", "dito"]):
                command = "GO_VOICE"
        
        # 5. Generate natural voice
        response_audio = generate_natural_voice(response_text)
        
        # 6. Detect language from AI's response
        detected_lang = detect_language(response_text)
        
        return response_text, response_audio, command, detected_lang
        
    except Exception as e:
        error_msg = f"Pasensya, may problema: {e}"
        return error_msg, None, None, "tagalog"


def generate_scan_insights(analysis_data, language="tagalog"):
    """
    Generate voice insights about a scanned plant.
    Returns both text and audio in the user's preferred language.
    """
    try:
        plant_name = analysis_data.get("plant_name", "Hindi kilala")
        health_status = analysis_data.get("health_status", "Unknown")
        action_plan = analysis_data.get("action_plan", "Walang action plan")
        confidence = analysis_data.get("confidence", 0)
        category = analysis_data.get("category", "Plant")
        
        # Create prompt based on language
        if language.lower() in ["bisaya", "cebuano", "visayan"]:
            lang_instruction = "Pagsulti sa Bisaya/Cebuano. Gamita ang simple nga Bisaya."
        else:
            lang_instruction = "Magsalita sa Tagalog. Gumamit ng simple at madaling maintindihan na Tagalog."
        
        prompt = f"""
        {lang_instruction}
        
        Ikaw si A.N.I., ang AI farm assistant. Kakatapos lang mag-scan ng halaman ang farmer.
        
        RESULTA NG SCAN:
        - Pangalan ng Halaman: {plant_name}
        - Health Status: {health_status}
        - Action Plan: {action_plan}
        - Confidence: {int(confidence * 100)}%
        - Category: {category}
        
        Magbigay ng MAIKLI at FRIENDLY na insights (2-3 sentences lang):
        1. Sabihin kung ano ang halaman at kung healthy ba o may sakit
        2. Kung may sakit, magbigay ng mabilis na tip kung paano gamutin
        3. Maging encouraging at supportive sa farmer
        
        HUWAG gumamit ng bullet points. Magsalita na parang kausap mo ang kaibigan.
        """
        
        # Get AI response
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[prompt]
        )
        
        insights_text = response.text
        
        # Generate voice
        insights_audio = generate_natural_voice(insights_text)
        
        return insights_text, insights_audio
        
    except Exception as e:
        print(f"Scan insights error: {e}")
        # Fallback simple message
        fallback = f"Na-scan ko na ang {analysis_data.get('plant_name', 'halaman')}. {analysis_data.get('health_status', 'Tingnan mo ang results')}."
        return fallback, None