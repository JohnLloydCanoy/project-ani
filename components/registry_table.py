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

    display_df = df[["image_url", "plant_name", "health_status", "created_at", "confidence"]]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "image_url": st.column_config.ImageColumn("Plant", width="small"),
            "plant_name": st.column_config.TextColumn("ID", width="medium"),
            "health_status": st.column_config.TextColumn("Health", width="small"),
            "created_at": st.column_config.DatetimeColumn("Scanned", format="MMM D, h:mm a"),
            "confidence": st.column_config.ProgressColumn("Confidence", format="%d%%", min_value=0, max_value=100),
        }
    )