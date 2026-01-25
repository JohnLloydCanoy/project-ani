import streamlit as st
from twin_renderer import render_twin_from_json

st.set_page_config(layout="wide", page_title="🥬 Digital Twin", page_icon="🌱")

# Custom CSS for better appearance
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .main > div { padding: 1rem 2rem; }
    .stJson { background-color: #1a1a1a !important; }
    h1, h2, h3 { color: #00FF88 !important; }
    .success { color: #00FF88; }
</style>
""", unsafe_allow_html=True)

st.title("🥬 Lettuce Digital Twin - Photorealistic Rendering")
st.markdown("*AI-powered 3D visualization from plant biometrics*")

# Divider
st.markdown("---")

# THE INPUT JSON - Detailed biometrics from image analysis
# Simulates Gemini's analysis of the reference photo
lettuce_json = {
    "plant_name": "Loose-Leaf Lettuce (Lactuca sativa var. crispa)",
    "structure_type": "rosette",
    "plant_count": 3,
    "health_status": "healthy",
    "estimated_height_cm": 18,
    "estimated_spread_cm": 22,
    "leaf_count": 45,
    "leaf_color_hex": "#7CFC00",
    "leaf_texture": "frilly",
    "growth_stage": "mature",
    "container_type": "terracotta_rectangular",
    "soil_moisture": "adequate",
    "diagnosis_notes": "Vibrant lime-green foliage with characteristic frilly edges. Dense rosette formation indicates healthy growth. No signs of bolting, pest damage, or nutrient deficiency. Leaves show excellent turgor pressure."
}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 AI Plant Analysis")
    st.markdown("*Extracted biometrics from photo:*")
    
    # Display key metrics
    st.metric("🌿 Plant Count", lettuce_json["plant_count"])
    st.metric("📏 Spread", f"{lettuce_json['estimated_spread_cm']} cm")
    st.metric("🍃 Leaf Count", f"~{lettuce_json['leaf_count']} per plant")
    st.metric("💚 Health", lettuce_json["health_status"].title())
    
    st.markdown("---")
    st.markdown("**Full JSON Data:**")
    st.json(lettuce_json)

with col2:
    st.subheader("🧬 3D Digital Twin")
    
    # Render the digital twin
    with st.spinner("Generating photorealistic 3D model..."):
        fig = render_twin_from_json(lettuce_json)
    
    # Display the 3D visualization
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']
    })
    
    st.success(f"✅ Rendered {lettuce_json['plant_count']} plants × ~{lettuce_json['leaf_count']} leaves = {lettuce_json['plant_count'] * lettuce_json['leaf_count']}+ individual leaf surfaces")

# Footer info
st.markdown("---")
st.markdown("""
**🎨 Visualization Features:**
- Realistic frilly leaf edges (loose-leaf lettuce variety)
- Golden angle phyllotaxis (137.5°) for natural spiral pattern  
- Age-based color gradient (lime center → forest green outer)
- Terracotta pot with textured soil
- Dynamic lighting and shadows
""")
st.caption("Rotate the 3D model by dragging. Zoom with scroll wheel.")