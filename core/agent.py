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
    "gemini-3-pro-preview",
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

# Main ANI agent function
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
            
            "health_assessment": {
                "health_status": "Healthy" or "Name of Disease/Problem",
                "disease_name": "" or "Specific disease name if detected",
                "severity": 0.0 to 1.0 (0=healthy, 1=severe),
                "affected_percentage": 0 to 100,
                "affected_areas": ["leaf tips", "lower leaves", "stem base", "fruits", "whole plant"],
                "issues": ["List of observed problems like yellowing, spots, wilting, pest damage"],
                "disease_pattern": "spots" or "patches" or "coating" or "wilting" or "discoloration" or "none",
                "disease_color_hex": "#8B4513" or color of disease symptoms
            },
            
            "3d_generation_notes": "Describe specific instructions for making this 3D model accurate. E.g., 'Large wavy outer leaves cupping inward around a central white cauliflower head. Leaves have prominent white midribs and bluish-green color. Leaves emerge from a thick central stem hidden by the head.'"
        }
        
        IMPORTANT: 
        - Extract ACTUAL colors from the image as hex codes
        - Count ACTUAL visible leaves and estimate total including hidden ones
        - Use your botanical knowledge to fill in what you can't see
        - The 3d_generation_notes should be detailed enough for a 3D artist to recreate this plant
        - CAREFULLY assess plant health: look for spots, discoloration, wilting, pest damage, yellowing
        - If plant shows ANY signs of disease/damage, set health_status to the problem name and severity > 0
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
        "health_assessment": {
            "health_status": "Healthy",
            "disease_name": "",
            "severity": 0,
            "affected_percentage": 0,
            "affected_areas": [],
            "issues": [],
            "disease_pattern": "none",
            "disease_color_hex": ""
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


def analyze_multi_angle_images(image_files: list) -> Optional[dict]:
    """
    Analyze multiple images from different angles for more accurate 3D modeling.
    Combines insights from all angles to create a comprehensive plant profile.
    
    Args:
        image_files: List of uploaded image file objects (3-5 images recommended)
        
    Returns:
        Dictionary with merged plant analysis and structure data
    """
    try:
        if not image_files or len(image_files) == 0:
            return None
        
        # Load all images
        images = []
        for img_file in image_files:
            img_file.seek(0)
            images.append(Image.open(img_file))
        
        # Build the prompt with all images
        prompt = f"""
        You are an expert 3D botanical modeler analyzing {len(images)} images of THE SAME PLANT from different angles.
        
        CRITICAL TASK: Combine information from ALL angles to create an accurate 3D model.
        
        For each image, note:
        - What parts of the plant are visible (front, back, top, sides, underside of leaves)
        - Any diseases, damage, or discoloration visible from that angle
        - Details about structure (stems, branches, leaf arrangement)
        
        Then MERGE all observations into a single comprehensive analysis.
        
        Return ONLY a JSON object with this exact structure (no markdown):
        {{
            "identified_plant": {{
                "common_name": "Plant Name",
                "scientific_name": "Scientific name",
                "plant_family": "Family name",
                "growth_stage": "vegetative" or "flowering" or "fruiting" or "mature",
                "confidence": 0.95
            }},
            
            "multi_angle_observations": {{
                "angles_analyzed": {len(images)},
                "front_view_notes": "What was observed from front angle",
                "back_view_notes": "What was observed from back angle (if available)",
                "top_view_notes": "What was observed from top angle (if available)",
                "side_view_notes": "What was observed from side angles",
                "underside_notes": "Leaf underside observations (if visible)"
            }},
            
            "plant_architecture": {{
                "overall_form": "rosette" or "bushy" or "upright" or "vining" or "columnar" or "spreading",
                "symmetry": "radial" or "bilateral" or "asymmetric",
                "height_cm": 40,
                "width_cm": 50,
                "has_central_head": false,
                "head_type": "none" or "cauliflower" or "cabbage" or "broccoli" or "lettuce",
                "fruit_type": "none" or "tomato" or "pepper" or "eggplant" or "cucumber",
                "fruit_count": 0,
                "fruit_color_hex": "#FF0000"
            }},
            
            "leaf_system": {{
                "arrangement": "rosette" or "alternate" or "opposite" or "whorled",
                "total_count": 12,
                "shape": "oval" or "elongated" or "heart" or "lobed" or "wavy",
                "primary_color_hex": "#228B22",
                "secondary_color_hex": "#90EE90",
                "underside_color_hex": "#98FB98",
                "waviness": 0.3,
                "orientation": "upward" or "outward" or "drooping" or "cupping"
            }},
            
            "health_analysis": {{
                "overall_health_percentage": 85,
                "health_status": "Healthy" or "Disease Name",
                "disease_severity": "None" or "Mild" or "Moderate" or "Severe",
                "affected_leaves_count": 0,
                "affected_area_percent": 5,
                "disease_locations": ["top leaves", "underside of lower leaves"],
                "symptoms_observed": ["yellowing", "spots", "wilting"],
                "diseases_detected": []
            }},
            
            "container": {{
                "type": "pot" or "ground" or "raised_bed" or "field",
                "shape": "round" or "square" or "natural",
                "material": "terracotta" or "plastic" or "soil",
                "color_hex": "#8B4513"
            }},
            
            "environmental_context": {{
                "setting": "indoor" or "outdoor" or "greenhouse" or "field",
                "lighting": "bright" or "moderate" or "low"
            }},
            
            "3d_generation_notes": "Detailed notes combining all angle observations for accurate 3D modeling. Include hidden parts that were revealed by multi-angle views.",
            
            "recommended_action": "One sentence recommendation based on complete analysis"
        }}
        """
        
        # Send all images with the prompt
        content = [prompt] + images
        response = model.generate_content(content)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json)
        
    except Exception as e:
        st.error(f"Multi-angle analysis error: {e}")
        return None


def compare_plant_health_over_time(current_analysis: dict, history: list) -> dict:
    """
    Compare current plant health with historical data to detect progression.
    
    Args:
        current_analysis: Current scan analysis dictionary
        history: List of previous analysis dictionaries with timestamps
        
    Returns:
        Dictionary with progression analysis
    """
    try:
        if not history or len(history) == 0:
            return {
                "has_history": False,
                "trend": "first_scan",
                "message": "This is the first scan. Future scans will show progression.",
                "recommendation": "Continue monitoring regularly."
            }
        
        # Get health percentages over time
        current_health = current_analysis.get("health_percentage", 0) or \
                        current_analysis.get("health_analysis", {}).get("overall_health_percentage", 0)
        
        health_timeline = []
        for h in history:
            hp = h.get("analysis_json", {}).get("health_percentage", 0) or \
                h.get("analysis_json", {}).get("health_analysis", {}).get("overall_health_percentage", 0)
            health_timeline.append({
                "date": h.get("created_at", "Unknown"),
                "health": hp,
                "status": h.get("health_status", "Unknown")
            })
        
        # Calculate trend
        if len(health_timeline) >= 2:
            first_health = health_timeline[-1]["health"]  # Oldest
            last_health = health_timeline[0]["health"]    # Most recent before current
            
            health_change = current_health - first_health
            recent_change = current_health - last_health
            
            if health_change > 10:
                trend = "improving"
                trend_emoji = "📈"
                message = f"Plant health improved by {health_change}% since first scan!"
            elif health_change < -10:
                trend = "declining"
                trend_emoji = "📉"
                message = f"Plant health declined by {abs(health_change)}% since first scan. Action needed."
            else:
                trend = "stable"
                trend_emoji = "➡️"
                message = f"Plant health is stable (±{abs(health_change)}% change)."
            
            # Generate recommendation based on trend
            if trend == "declining":
                recommendation = "The plant's health is declining. Check for pests, diseases, or environmental stress. Consider adjusting watering or fertilization."
            elif trend == "improving":
                recommendation = "Treatment is working! Continue current care routine."
            else:
                recommendation = "Plant is stable. Maintain current care and continue monitoring."
            
            return {
                "has_history": True,
                "scan_count": len(history) + 1,
                "trend": trend,
                "trend_emoji": trend_emoji,
                "health_change_total": health_change,
                "health_change_recent": recent_change,
                "current_health": current_health,
                "first_health": first_health,
                "message": message,
                "health_timeline": health_timeline,
                "recommendation": recommendation
            }
        else:
            return {
                "has_history": True,
                "scan_count": 2,
                "trend": "insufficient_data",
                "message": "Need at least 2 previous scans to determine trend.",
                "health_timeline": health_timeline,
                "recommendation": "Continue scanning regularly to track progression."
            }
            
    except Exception as e:
        return {
            "has_history": False,
            "trend": "error",
            "message": f"Could not analyze progression: {e}",
            "recommendation": "Continue monitoring."
        }
