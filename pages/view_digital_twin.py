import streamlit as st
from typing import Optional
from core.agent import generate_texture_from_upload, analyze_crop_for_simulation, analyze_plant_structure
from components.digital_twin import render_3d_simulation

def view_digital_twin():
    """
    Digital Twin Simulator Page - Visual Cloning Feature
    Users upload a crop photo, system analyzes and generates a 3D texture simulation.
    """
    st.markdown("""
    <div style='text-align: center;'>
        <h2 style='margin-bottom: 0; margin-top: 70px;'>🌿 Digital Twin Simulator</h2>
        <p style='color: gray; font-size: 16px; margin-top: -15px;'>Clone your crops into realistic 3D simulations</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("---")
    # Initialize session state
    if "generated_texture" not in st.session_state:
        st.session_state.generated_texture = None
    if "crop_analysis" not in st.session_state:
        st.session_state.crop_analysis = None
    if "plant_structure" not in st.session_state:
        st.session_state.plant_structure = None
    if "simulation_active" not in st.session_state:
        st.session_state.simulation_active = False
    
    # Layout: Two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Crop Image")
        st.caption("Upload a clear photo of your crop for AI-powered 3D cloning.")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear, well-lit photo of your crop leaf or plant.",
            key="digital_twin_uploader"
        )
        
        if uploaded_file is not None:
            # Show preview
            st.image(uploaded_file, caption="📷 Uploaded Image Preview", use_container_width=True)
            
            # Clone & Simulate button
            if st.button("🧬 Clone & Simulate", type="primary", use_container_width=True):
                with st.status("🔬 Gemini is analyzing your plant...", expanded=True) as status:
                    
                    # Step 1: Analyze crop health
                    st.write("🔍 Analyzing crop health...")
                    analysis = analyze_crop_for_simulation(uploaded_file)
                    
                    if analysis:
                        st.session_state.crop_analysis = analysis
                        st.write(f"✅ Identified: {analysis.get('plant_name', 'Unknown')}")
                        
                        # Step 2: Deep analysis of plant structure for 3D modeling
                        st.write("🧠 Gemini analyzing plant shape, colors, and container...")
                        plant_structure = analyze_plant_structure(uploaded_file)
                        
                        if plant_structure:
                            st.session_state.plant_structure = plant_structure
                            leaf_data = plant_structure.get('leaf_details', {})
                            container_data = plant_structure.get('container', {})
                            st.write(f"✅ Leaves: {leaf_data.get('shape', 'oval')} shape, {leaf_data.get('count', 12)} count")
                            st.write(f"✅ Container: {container_data.get('material', 'terracotta')} {container_data.get('type', 'pot')}")
                            st.write(f"✅ Pattern: {plant_structure.get('growth_pattern', 'rosette')}")
                        
                        # Step 3: Generate texture (optional now since we use colors)
                        st.write("🎨 Finalizing 3D model...")
                        texture = generate_texture_from_upload(uploaded_file)
                        
                        if texture:
                            st.session_state.generated_texture = texture
                            st.session_state.simulation_active = True
                            status.update(label="✅ 3D Plant Ready!", state="complete", expanded=False)
                            st.rerun()
                        else:
                            status.update(label="⚠️ Texture generation failed", state="error")
                            st.error("Could not generate texture. Using fallback simulation.")
                            st.session_state.simulation_active = True
                            st.rerun()
                    else:
                        status.update(label="❌ Analysis failed", state="error")
                        st.error("Could not analyze the image. Please upload a clearer photo of a crop.")
        else:
            st.info("👆 Upload an image to begin 3D cloning")
        
        # Reset button
        if st.session_state.simulation_active:
            if st.button("🔄 Reset Simulation", use_container_width=True):
                st.session_state.generated_texture = None
                st.session_state.crop_analysis = None
                st.session_state.plant_structure = None
                st.session_state.simulation_active = False
                st.rerun()
    
    with col2:
        st.markdown("### 🎮 3D Simulation")
        
        if st.session_state.simulation_active:
            # Render the 3D simulation with plant structure
            render_3d_simulation(
                texture_data=st.session_state.generated_texture,
                plant_structure=st.session_state.plant_structure,
                height=450
            )
            
            # Show analysis results below
            if st.session_state.crop_analysis:
                st.markdown("### 📊 Analysis Results")
                analysis = st.session_state.crop_analysis
                
                # Health status card
                health_status = analysis.get("health_status", "Unknown")
                health_pct = analysis.get("health_percentage", 0)
                
                if health_status == "Healthy":
                    st.success(f"🌿 **{analysis.get('plant_name', 'Unknown')}** - Healthy ({health_pct}%)")
                else:
                    st.warning(f"⚠️ **{analysis.get('plant_name', 'Unknown')}** - {health_status}")
                
                # Metrics
                met_col1, met_col2 = st.columns(2)
                with met_col1:
                    st.metric("Health Score", f"{health_pct}%")
                with met_col2:
                    severity = analysis.get("disease_severity", "None")
                    st.metric("Severity", severity)
                
                # Affected area
                affected = analysis.get("affected_area_percent", 0)
                st.progress(affected / 100, text=f"Affected Area: {affected}%")
                
                # Recommendation
                if analysis.get("recommended_action"):
                    st.info(f"💡 **Recommendation:** {analysis.get('recommended_action')}")
                
                # Show detailed plant structure info
                if st.session_state.plant_structure:
                    with st.expander("🧬 3D Model Analysis (Gemini Vision)", expanded=True):
                        ps = st.session_state.plant_structure
                        
                        # Leaf details
                        st.markdown("**🌿 Leaf Analysis:**")
                        leaf = ps.get('leaf_details', {})
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"• Shape: `{leaf.get('shape', 'N/A')}`")
                            st.write(f"• Count: `{leaf.get('count', 'N/A')}`")
                            st.write(f"• Size: `{leaf.get('size', 'N/A')}`")
                            st.write(f"• Edge: `{leaf.get('edge_type', 'N/A')}`")
                        with col_b:
                            primary = leaf.get('primary_color_hex', '#4CAF50')
                            secondary = leaf.get('secondary_color_hex', '#81C784')
                            st.markdown(f"• Primary: <span style='color:{primary}'>■</span> `{primary}`", unsafe_allow_html=True)
                            st.markdown(f"• Secondary: <span style='color:{secondary}'>■</span> `{secondary}`", unsafe_allow_html=True)
                            st.write(f"• Glossy: `{leaf.get('glossy', False)}`")
                        
                        st.markdown("---")
                        
                        # Container details
                        st.markdown("**🪴 Container Analysis:**")
                        container = ps.get('container', {})
                        col_c, col_d = st.columns(2)
                        with col_c:
                            st.write(f"• Type: `{container.get('type', 'N/A')}`")
                            st.write(f"• Shape: `{container.get('shape', 'N/A')}`")
                            st.write(f"• Material: `{container.get('material', 'N/A')}`")
                        with col_d:
                            pot_color = container.get('color_hex', '#B5651D')
                            st.markdown(f"• Color: <span style='color:{pot_color}'>■</span> `{pot_color}`", unsafe_allow_html=True)
                            st.write(f"• Rim: `{container.get('rim_style', 'N/A')}`")
                            st.write(f"• Texture: `{container.get('texture', 'N/A')}`")
                        
                        st.markdown("---")
                        st.write(f"**Growth Pattern:** `{ps.get('growth_pattern', 'N/A')}`")
                        st.write(f"**Overall Health:** `{ps.get('overall_health', 'N/A')}`")
        else:
            # Placeholder simulation
            render_3d_simulation(texture_data=None, plant_structure=None, height=450)
            st.caption("Upload an image and click 'Clone & Simulate' to generate a realistic 3D digital twin.")

view_digital_twin()