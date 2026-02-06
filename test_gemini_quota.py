"""
🧪 GEMINI MODEL & QUOTA TESTER
Tests available models, quota limits, and capabilities
"""

import streamlit as st
from google import genai
from google.genai import types
import json
from datetime import datetime

def test_gemini_quota():
    """Test Gemini API quota and available models"""
    
    st.title("🧪 Gemini Model & Quota Tester")
    st.write("---")
    
    # Initialize client
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ GEMINI_API_KEY not found in secrets!")
        return
    
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("✅ API Key loaded successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize client: {e}")
        return
    
    # Test 1: List Available Models
    st.header("📋 Available Models")
    try:
        models = client.models.list()
        st.success(f"✅ Found {len(models.models)} available models")
        
        model_data = []
        for model in models.models:
            model_info = {
                "Model Name": model.name,
                "Display Name": getattr(model, 'display_name', 'N/A'),
                "Description": getattr(model, 'description', 'N/A')[:100] + "..." if hasattr(model, 'description') and len(getattr(model, 'description', '')) > 100 else getattr(model, 'description', 'N/A'),
                "Supported Generation Methods": ', '.join(getattr(model, 'supported_generation_methods', [])) if hasattr(model, 'supported_generation_methods') else 'N/A'
            }
            model_data.append(model_info)
        
        st.dataframe(model_data)
        
        # Show audio-capable models
        st.subheader("🎵 Audio-Capable Models")
        audio_models = []
        for model in models.models:
            name = model.name
            if any(keyword in name.lower() for keyword in ['flash', 'pro', '2.0', '2.5']):
                audio_models.append(name)
        
        if audio_models:
            st.success("These models likely support audio:")
            for model in audio_models:
                st.write(f"• {model}")
        else:
            st.warning("No obvious audio-capable models found")
            
    except Exception as e:
        st.error(f"❌ Failed to list models: {e}")
    
    # Test 2: Test Text Generation
    st.header("💬 Text Generation Test")
    test_models = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro", 
        "models/gemini-2.0-flash-exp",
        "models/gemini-3.0-flash",
        "models/gemini-pro"
    ]
    
    for model_name in test_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Say hello in Filipino English"
            )
            st.success(f"✅ {model_name}: {response.text[:100]}...")
            break
        except Exception as e:
            st.warning(f"❌ {model_name}: {str(e)[:100]}...")
    
    # Test 3: Test Audio Capabilities
    st.header("🎵 Audio Generation Test")
    audio_test_models = [
        "models/gemini-2.0-flash-exp",
        "models/gemini-2.0-flash",
        "models/gemini-1.5-flash",
        "models/gemini-flash"
    ]
    
    for model_name in audio_test_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Say hello world",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Aoede"
                            )
                        )
                    )
                )
            )
            st.success(f"✅ {model_name}: Audio generation works!")
            break
        except Exception as e:
            st.warning(f"❌ {model_name}: {str(e)[:150]}...")
    
    # Test 4: Quota Information
    st.header("📊 Quota Information")
    st.info("Note: Quota info may not be directly accessible via API")
    
    # Test 5: Recommended Configuration
    st.header("⚙️ Recommended Configuration")
    st.code("""
# For your voice_service.py, try these models in order:

# For Text-to-Speech (TTS):
models_to_try_tts = [
    "models/gemini-1.5-flash",    # Most stable
    "models/gemini-1.5-pro",      # Higher quality
    "models/gemini-flash",        # Simple name
]

# For Speech-to-Text (STT):
models_to_try_stt = [
    "models/gemini-1.5-flash",    # Most stable
    "models/gemini-1.5-pro",      # Higher quality  
    "models/gemini-flash",        # Simple name
]
""")

if __name__ == "__main__":
    test_gemini_quota()