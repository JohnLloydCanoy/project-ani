import google.generativeai as genai
import streamlit as st
from google import genai as genai_client
from google.genai import types
from PIL import Image
import json
import base64
from io import BytesIO
from typing import Optional

# 'gemini-3-pro-preview' is best for deep diagnosis (Visual Reasoning)
# 'gemini-3-flash-preview' is best for fast voice/chat

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])


# Gemini model with tool functions
model = genai.GenerativeModel(
    "gemini-3-flash-preview",
)


# This function for image analysis
def ask_gemini(image_file):
    """
    Accepts an uploaded file object, converts it to an image,
    and asks Gemini to analyze it for plant health.
    """
    try:
        if not image_file:
            return "Error: No image provided."
        image_file.seek(0)
        image = Image.open(image_file)
        prompt = """
        You are an expert Agronomist (Project A.N.I.). 
        Analyze this plant image.
        
        Return ONLY a JSON object with this exact structure (no markdown):
        {
            "plant_name": "Common Name (Scientific Name)",
            "health_status": "Healthy" or "Name of Disease",
            "action_plan": "One short sentence on what to do.",
            "confidence": 0.95,
            "category": "Crop" or "Weed" or "Ornamental"
        }
        """
        response = model.generate_content([prompt, image])
        
        return response.text
        
    except Exception as e:
        return f"Error connecting to Gemini: {e}"


def ani_agent(user_question: str) -> str:
    """
    Main agent function for text-based chat with ANI.
    Expects Text -> Returns Text.
    """
    try:
        system_instruction = """
        You are A.N.I. (Agricultural Network Intelligence), a friendly and expert farming assistant for the Philippines.
        - Answer questions about farming, crops, and pests.
        - Keep answers concise and helpful.
        - If asked about non-farming topics, politely guide them back to agriculture.
        - You can help users navigate the app:
            * "Scan" -> Takes a photo to diagnose plants.
            * "Registry" -> View saved plant data.
            * "Digital Twin" -> Simulate crop conditions.
        """
        full_prompt = f"{system_instruction}\n\nUser: {user_question}\nANI:"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"Sorry, I couldn't connect to the server. ({e})"


def generate_texture_from_upload(image_file) -> Optional[str]:
    """
    Convert uploaded crop image directly to a Base64 texture for 3D rendering.
    Uses the original image as the texture (no Imagen needed).
    
    Args:
        image_file: Uploaded image file object from st.file_uploader
        
    Returns:
        Base64 Data URI string of the texture, or None if failed
    """
    try:
        if not image_file:
            return None
        
        # Read the uploaded image directly and convert to base64
        image_file.seek(0)
        image = Image.open(image_file)
        
        # Resize to a reasonable texture size (512x512 for performance)
        image = image.convert("RGB")
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        data_uri = f"data:image/png;base64,{base64_encoded}"
        
        return data_uri
            
    except Exception as e:
        st.error(f"Texture generation error: {e}")
        return None


def analyze_plant_structure(image_file) -> Optional[dict]:
    """
    Use Gemini's advanced vision + botanical knowledge to create a complete 3D mental model.
    Gemini will analyze visible parts AND infer hidden structures based on plant anatomy.
    
    Args:
        image_file: Uploaded image file object
        
    Returns:
        Dictionary with comprehensive 3D modeling parameters
    """
    try:
        if not image_file:
            return None
            
        image_file.seek(0)
        image = Image.open(image_file)
        
        prompt = """
        You are a 3D botanical modeler with expert knowledge of plant anatomy.
        
        CRITICAL TASK: Analyze this plant image to create a COMPLETE 3D model.
        
        STEP 1 - IDENTIFY THE PLANT:
        Use your extensive botanical knowledge to identify exactly what plant this is.
        Consider: leaf shape, growth pattern, stem structure, any flowers/fruits/heads visible.
        
        STEP 2 - THINK IN 3D:
        Even though you only see one angle, use your knowledge of this plant species to:
        - Infer what the back/hidden parts look like
        - Understand the full 3D structure from root to top
        - Know how leaves are arranged around the stem (phyllotaxy)
        - Understand the plant's typical form and silhouette
        
        STEP 3 - DESCRIBE FOR 3D MODELING:
        
        Return ONLY a JSON object with this exact structure (no markdown):
        {
            "identified_plant": {
                "common_name": "Cauliflower",
                "scientific_name": "Brassica oleracea var. botrytis",
                "plant_family": "Brassicaceae",
                "growth_stage": "vegetative" or "flowering" or "fruiting" or "mature"
            },
            
            "plant_architecture": {
                "overall_form": "rosette" or "bushy" or "upright" or "vining" or "columnar" or "spreading" or "grass" or "trailing",
                "symmetry": "radial" or "bilateral" or "asymmetric",
                "height_cm": 40,
                "width_cm": 50,
                "has_central_head": true,
                "head_type": "none" or "cauliflower" or "cabbage" or "broccoli" or "lettuce",
                "head_color_hex": "#F5F5DC",
                "head_size_ratio": 0.3,
                "fruit_type": "none" or "tomato" or "cherry_tomato" or "pepper" or "chili" or "eggplant" or "cucumber" or "squash" or "bean",
                "fruit_color_hex": "#FF6347",
                "fruit_count": 5,
                "fruit_size": 0.08,
                "fruit_stage": "none" or "flowering" or "green" or "ripening" or "ripe",
                "root_type": "none" or "taproot" or "bulb" or "tuber" or "rhizome",
                "root_color_hex": "#FF6600",
                "root_visible": false
            },
            
            "leaf_system": {
                "arrangement": "rosette" or "alternate" or "opposite" or "whorled" or "basal",
                "total_count": 12,
                "leaf_layers": 3,
                "shape": "oval" or "elongated" or "heart" or "lobed" or "wavy" or "ruffled" or "spatulate",
                "size_cm": 25,
                "width_cm": 15,
                "thickness": "thin" or "medium" or "thick" or "succulent",
                "texture": "smooth" or "waxy" or "hairy" or "ribbed" or "veined",
                "edge_type": "smooth" or "wavy" or "serrated" or "lobed" or "ruffled",
                "curl_amount": 0.4,
                "waviness": 0.6,
                "stiffness": "flexible" or "semi-rigid" or "rigid",
                "primary_color_hex": "#228B22",
                "secondary_color_hex": "#90EE90",
                "vein_color_hex": "#FFFFFF",
                "vein_prominence": "subtle" or "visible" or "prominent",
                "orientation": "upward" or "outward" or "drooping" or "cupping"
            },
            
            "stem_system": {
                "visible": true,
                "type": "single" or "branching" or "rosette_base" or "none_visible",
                "thickness_cm": 3,
                "height_cm": 5,
                "color_hex": "#90EE90"
            },
            
            "container": {
                "type": "pot" or "planter" or "ground" or "raised_bed" or "none",
                "visible": true,
                "shape": "round" or "square" or "rectangular" or "natural",
                "material": "terracotta" or "plastic" or "ceramic" or "wood" or "soil",
                "color_hex": "#8B4513",
                "has_rim": true
            },
            
            "soil_ground": {
                "visible": true,
                "type": "potting_soil" or "garden_soil" or "mulch" or "none",
                "color_hex": "#3D2B1F"
            },
            
            "environmental_context": {
                "setting": "indoor" or "outdoor" or "greenhouse",
                "lighting": "bright" or "moderate" or "low",
                "background_plants": false
            },
            
            "3d_generation_notes": "Describe specific instructions for making this 3D model accurate. E.g., 'Large wavy outer leaves cupping inward around a central white cauliflower head. Leaves have prominent white midribs and bluish-green color. Leaves emerge from a thick central stem hidden by the head.'"
        }
        
        IMPORTANT: 
        - Extract ACTUAL colors from the image as hex codes
        - Count ACTUAL visible leaves and estimate total including hidden ones
        - Use your botanical knowledge to fill in what you can't see
        - The 3d_generation_notes should be detailed enough for a 3D artist to recreate this plant
        """
        
        response = model.generate_content([prompt, image])
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json)
        
    except Exception as e:
        st.error(f"Plant structure analysis error: {e}")
        return get_default_plant_structure()


def get_default_plant_structure() -> dict:
    """Return default structure when analysis fails."""
    return {
        "identified_plant": {
            "common_name": "Unknown Plant",
            "scientific_name": "Unknown",
            "plant_family": "Unknown",
            "growth_stage": "vegetative"
        },
        "plant_architecture": {
            "overall_form": "rosette",
            "symmetry": "radial",
            "height_cm": 30,
            "width_cm": 40,
            "has_central_head": False,
            "head_type": "none",
            "head_color_hex": "#FFFFFF",
            "head_size_ratio": 0
        },
        "leaf_system": {
            "arrangement": "rosette",
            "total_count": 12,
            "leaf_layers": 3,
            "shape": "oval",
            "size_cm": 15,
            "width_cm": 10,
            "thickness": "medium",
            "texture": "smooth",
            "edge_type": "smooth",
            "curl_amount": 0.3,
            "waviness": 0.3,
            "stiffness": "semi-rigid",
            "primary_color_hex": "#4CAF50",
            "secondary_color_hex": "#81C784",
            "vein_color_hex": "#FFFFFF",
            "vein_prominence": "subtle",
            "orientation": "outward"
        },
        "stem_system": {
            "visible": False,
            "type": "rosette_base",
            "thickness_cm": 2,
            "height_cm": 3,
            "color_hex": "#90EE90"
        },
        "container": {
            "type": "pot",
            "visible": True,
            "shape": "round",
            "material": "terracotta",
            "color_hex": "#B5651D",
            "has_rim": True
        },
        "soil_ground": {
            "visible": True,
            "type": "potting_soil",
            "color_hex": "#3D2B1F"
        },
        "environmental_context": {
            "setting": "outdoor",
            "lighting": "bright",
            "background_plants": False
        },
        "3d_generation_notes": "Generic leafy plant with oval leaves arranged in a rosette pattern."
    }


def analyze_crop_for_simulation(image_file) -> Optional[dict]:
    """
    Analyze uploaded crop image and return structured data for simulation.
    
    Args:
        image_file: Uploaded image file object
        
    Returns:
        Dictionary with plant analysis data, or None if failed
    """
    try:
        if not image_file:
            return None
            
        image_file.seek(0)
        image = Image.open(image_file)
        
        prompt = """
        You are an expert Agronomist analyzing a crop for digital twin simulation.
        
        Return ONLY a JSON object with this exact structure (no markdown):
        {
            "plant_name": "Common Name (Scientific Name)",
            "health_status": "Healthy" or "Disease Name",
            "health_percentage": 85,
            "disease_severity": "None" or "Mild" or "Moderate" or "Severe",
            "affected_area_percent": 15,
            "primary_color": "#2E7D32",
            "secondary_color": "#81C784",
            "disease_color": "#8B4513",
            "texture_description": "Brief description of surface texture",
            "recommended_action": "One sentence recommendation"
        }
        """
        
        response = model.generate_content([prompt, image])
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json)
        
    except Exception as e:
        st.error(f"Analysis error: {e}")
        return None