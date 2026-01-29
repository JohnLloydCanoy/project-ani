
import streamlit as st
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
        # Order by newest first
        response = supabase.table("plants_registry").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"DB Error: {e}")
        return []

def save_plant_to_db(plant_name, image_url, json_data):
    """Saves a new scan."""
    supabase = get_supabase_client()
    if not supabase: return None
    
    data = {
        "plant_name": plant_name,
        "image_url": image_url,
        "health_status": json_data.get("health_status", "Unknown"),
        "confidence": json_data.get("confidence", 0),
        "analysis_json": json_data
    }
    
    return supabase.table("plants_registry").insert(data).execute()