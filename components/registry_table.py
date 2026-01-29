import streamlit as st
import pandas as pd
from services.db_service import fetch_all_plants 

def render_registry_table():
    st.divider()
    st.markdown("### 📋 Smart Field Registry")
    raw_data = fetch_all_plants()
    
    if not raw_data:
        st.info("No scans yet. Go analyze some plants!")
        return

    df = pd.DataFrame(raw_data)

    if "confidence" in df.columns:
        df["confidence"] = df["confidence"] * 100
    display_df = df[["image_url", "plant_name", "category", "health_status", "farm_name", "confidence", "created_at"]]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "image_url": st.column_config.ImageColumn("Evidence", width="small"),
            "plant_name": st.column_config.TextColumn("Plant", width="medium"), # Renamed from "ID"
            "category": st.column_config.TextColumn("Type", width="small"),
            "health_status": st.column_config.TextColumn("Diagnosis", width="medium"),
            "farm_name": st.column_config.TextColumn("Location", width="medium"), # New Column!
            "created_at": st.column_config.DatetimeColumn("Time", format="h:mm a"),
            "confidence": st.column_config.ProgressColumn(
                "Confidence", 
                format="%d%%", 
                min_value=0, 
                max_value=100
            ),
        }
    )