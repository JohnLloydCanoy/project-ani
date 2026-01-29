import streamlit as st
import uuid  
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Supabase Connection Error: {e}")
        return None

def fetch_all_plants():
    """Gets the raw data from the database."""
    supabase = get_supabase_client()
    if not supabase: return []
    
    try:
        response = supabase.table("plants_registry").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"DB Error: {e}")
        return []

# --- THIS IS THE NEW FUNCTION YOU WERE MISSING ---
def upload_image_to_supabase(image_file):
    """Uploads the raw image file to Supabase Storage and returns the public URL."""
    supabase = get_supabase_client()
    if not supabase: return None

    try:
        # 1. Generate a unique filename (e.g., "scans/abc-123.jpg")
        file_ext = image_file.name.split(".")[-1]
        file_path = f"scans/{uuid.uuid4()}.{file_ext}"
        
        # 2. Upload the bytes to the 'plant-photos' bucket
        # MAKE SURE YOU CREATED THIS BUCKET IN SUPABASE!
        supabase.storage.from_("plant-photos").upload(
            file_path, 
            image_file.getvalue(), 
            {"content-type": image_file.type}
        )
        
        # 3. Get the Public Link so we can save it to the DB
        public_url = supabase.storage.from_("plant-photos").get_public_url(file_path)
        return public_url
        
    except Exception as e:
        st.error(f"Upload Failed: {e}")
        return None

def save_plant_to_db(plant_name, image_url, json_data, farm_name="Main Field"):
    """Saves a new scan."""
    supabase = get_supabase_client()
    if not supabase: return None
    
    data = {
        "plant_name": plant_name,
        "image_url": image_url,
        "category": json_data.get("category", "Uncategorized"),
        "health_status": json_data.get("health_status", "Unknown"),
        "confidence": json_data.get("confidence", 0.0),
        "farm_name": farm_name,
        "analysis_json": json_data
    }
    
    return supabase.table("plants_registry").insert(data).execute()