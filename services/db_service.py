import streamlit as st
import uuid
from datetime import datetime
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


def fetch_tracked_plants(device_id: str = None):
    """
    Gets all tracked plants for the current device/user.
    Tracked plants are those that have been scanned multiple times.
    """
    supabase = get_supabase_client()
    if not supabase: return []
    
    try:
        query = supabase.table("plants_registry").select("*")
        
        if device_id:
            # Filter by device if available
            query = query.eq("device_id", device_id)
        
        # Get plants with tracking_id (plants being tracked over time)
        query = query.not_.is_("tracking_id", "null")
        response = query.order("created_at", desc=True).execute()
        
        return response.data
    except Exception as e:
        print(f"DB Error fetching tracked plants: {e}")
        return []


def fetch_plant_history(tracking_id: str):
    """
    Gets all scan history for a specific tracked plant.
    
    Args:
        tracking_id: Unique ID assigned when user starts tracking a plant
        
    Returns:
        List of all scans for this plant, ordered by date (newest first)
    """
    supabase = get_supabase_client()
    if not supabase: return []
    
    try:
        response = supabase.table("plants_registry") \
            .select("*") \
            .eq("tracking_id", tracking_id) \
            .order("created_at", desc=True) \
            .execute()
        return response.data
    except Exception as e:
        print(f"DB Error fetching plant history: {e}")
        return []


def get_unique_tracked_plants(device_id: str = None):
    """
    Gets unique tracked plants (one entry per tracking_id with latest data).
    """
    supabase = get_supabase_client()
    if not supabase: return []
    
    try:
        # Get all tracked plants
        query = supabase.table("plants_registry").select("*")
        
        if device_id:
            query = query.eq("device_id", device_id)
        
        query = query.not_.is_("tracking_id", "null")
        response = query.order("created_at", desc=True).execute()
        
        # Group by tracking_id and get most recent
        plants_by_id = {}
        for plant in response.data:
            tid = plant.get("tracking_id")
            if tid and tid not in plants_by_id:
                # Count how many scans exist for this plant
                plant["scan_count"] = len([p for p in response.data if p.get("tracking_id") == tid])
                plants_by_id[tid] = plant
        
        return list(plants_by_id.values())
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

def save_plant_to_db(plant_name, image_url, json_data, farm_name="Main Field", tracking_id=None, device_id=None):
    """
    Saves a new scan to the database.
    
    Args:
        plant_name: Name of the plant
        image_url: URL of the uploaded image
        json_data: Analysis JSON data
        farm_name: Name of the farm/field
        tracking_id: Optional ID for tracking same plant over time
        device_id: Optional device ID for user identification
    """
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
    
    # Add tracking fields if provided
    if tracking_id:
        data["tracking_id"] = tracking_id
    if device_id:
        data["device_id"] = device_id
    
    return supabase.table("plants_registry").insert(data).execute()


def save_tracked_plant_scan(plant_name, image_url, json_data, tracking_id, plant_nickname=None, device_id=None):
    """
    Save a scan for a tracked plant (progressive monitoring).
    
    Args:
        plant_name: Identified plant name
        image_url: URL of uploaded image
        json_data: Full analysis JSON
        tracking_id: Unique ID for this plant being tracked
        plant_nickname: User-given name like "Tomato Plant #1"
        device_id: Device identifier
    """
    supabase = get_supabase_client()
    if not supabase: return None
    
    # Extract health data from different possible structures
    health_pct = json_data.get("health_percentage", 0) or \
                 json_data.get("health_analysis", {}).get("overall_health_percentage", 0)
    
    data = {
        "plant_name": plant_nickname or plant_name,
        "image_url": image_url,
        "category": json_data.get("category", "Crop"),
        "health_status": json_data.get("health_status", "Unknown"),
        "confidence": json_data.get("confidence", 0.0) or \
                     json_data.get("identified_plant", {}).get("confidence", 0.0),
        "farm_name": "Tracked Plant",
        "analysis_json": json_data,
        "tracking_id": tracking_id,
        "device_id": device_id
    }
    
    return supabase.table("plants_registry").insert(data).execute()


def generate_tracking_id():
    """Generate a unique tracking ID for a new plant to track."""
    return f"track_{uuid.uuid4().hex[:12]}"


def delete_tracked_plant(tracking_id: str):
    """
    Delete all scans associated with a tracked plant.
    """
    supabase = get_supabase_client()
    if not supabase: return False
    
    try:
        supabase.table("plants_registry") \
            .delete() \
            .eq("tracking_id", tracking_id) \
            .execute()
        return True
    except Exception as e:
        print(f"Error deleting tracked plant: {e}")
        return False