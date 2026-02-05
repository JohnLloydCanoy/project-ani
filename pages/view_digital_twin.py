import streamlit as st
from typing import Optional
from core.agent import (
    generate_texture_from_upload, 
    analyze_crop_for_simulation, 
    analyze_plant_structure,
    analyze_multi_angle_images,
    compare_plant_health_over_time
)
from components.digital_twin import render_3d_simulation
from components.growth_simulator import integrate_growth_simulation, render_growth_timeline
from services.db_service import (
    fetch_plant_history,
    get_unique_tracked_plants,
    save_tracked_plant_scan,
    generate_tracking_id,
    upload_image_to_supabase
)

def view_digital_twin():
    """
    Digital Twin Simulator Page - Visual Cloning Feature
    Now supports:
    - Multi-angle image upload (3-5 images) for better 3D accuracy
    - Progressive disease tracking over time
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
    if "tracking_mode" not in st.session_state:
        st.session_state.tracking_mode = False
    if "current_tracking_id" not in st.session_state:
        st.session_state.current_tracking_id = None
    if "progression_data" not in st.session_state:
        st.session_state.progression_data = None
    if "multi_angle_mode" not in st.session_state:
        st.session_state.multi_angle_mode = False
    
    # Mode selector tabs
    tab1, tab2, tab3 = st.tabs(["📷 Single Image", "📐 Multi-Angle (3-5 Photos)", "📊 Track Plant Over Time"])
    
    with tab1:
        render_single_image_mode()
    
    with tab2:
        render_multi_angle_mode()
    
    with tab3:
        render_tracking_mode()


def render_single_image_mode():
    """Original single image upload mode."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Crop Image")
        st.caption("Upload a clear photo of your crop for AI-powered 3D cloning.")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear, well-lit photo of your crop leaf or plant.",
            key="single_image_uploader"
        )
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption="📷 Uploaded Image Preview", use_container_width=True)
            
            if st.button("🧬 Clone & Simulate", type="primary", use_container_width=True, key="single_clone_btn"):
                run_single_image_analysis(uploaded_file)
        else:
            st.info("👆 Upload an image to begin 3D cloning")
        
        if st.session_state.simulation_active:
            if st.button("🔄 Reset Simulation", use_container_width=True, key="single_reset_btn"):
                reset_simulation()
    
    with col2:
        render_3d_preview()


def render_multi_angle_mode():
    """Multi-angle image upload for better 3D accuracy."""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📐 Multi-Angle Analysis")
        st.caption("Upload 3-5 photos from different angles for more accurate 3D modeling.")
        
        st.info("""
        **📸 Recommended angles:**
        1. Front view (main shot)
        2. Back view (behind the plant)
        3. Top view (looking down)
        4. Side view (left or right)
        5. Underside of leaves (if possible)
        """)
        
        uploaded_files = st.file_uploader(
            "Choose 3-5 images",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True,
            help="Upload 3-5 clear photos from different angles.",
            key="multi_image_uploader"
        )
        
        if uploaded_files and len(uploaded_files) > 0:
            # Show previews in a grid
            st.markdown(f"**{len(uploaded_files)} image(s) uploaded:**")
            
            if len(uploaded_files) < 3:
                st.warning("⚠️ Upload at least 3 images for best results")
            elif len(uploaded_files) > 5:
                st.warning("⚠️ Maximum 5 images recommended")
            
            # Display image grid
            cols = st.columns(min(len(uploaded_files), 3))
            for idx, img in enumerate(uploaded_files[:5]):
                with cols[idx % 3]:
                    st.image(img, caption=f"Angle {idx + 1}", use_container_width=True)
            
            if len(uploaded_files) >= 2:
                if st.button("🧬 Analyze All Angles", type="primary", use_container_width=True, key="multi_clone_btn"):
                    run_multi_angle_analysis(uploaded_files[:5])
        else:
            st.info("👆 Upload 3-5 images from different angles")
        
        if st.session_state.simulation_active:
            if st.button("🔄 Reset Simulation", use_container_width=True, key="multi_reset_btn"):
                reset_simulation()
    
    with col2:
        render_3d_preview()
        
        # Show multi-angle specific insights
        if st.session_state.plant_structure and st.session_state.multi_angle_mode:
            with st.expander("📐 Multi-Angle Insights", expanded=True):
                ps = st.session_state.plant_structure
                obs = ps.get("multi_angle_observations", {})
                
                st.markdown(f"**Angles Analyzed:** {obs.get('angles_analyzed', 1)}")
                
                if obs.get("front_view_notes"):
                    st.markdown(f"**Front:** {obs.get('front_view_notes')}")
                if obs.get("back_view_notes"):
                    st.markdown(f"**Back:** {obs.get('back_view_notes')}")
                if obs.get("top_view_notes"):
                    st.markdown(f"**Top:** {obs.get('top_view_notes')}")
                if obs.get("underside_notes"):
                    st.markdown(f"**Underside:** {obs.get('underside_notes')}")


def render_tracking_mode():
    """Progressive disease tracking over time."""
    st.markdown("### 📊 Track Plant Health Over Time")
    st.caption("Monitor the same plant over days/weeks to see disease progression or recovery.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Get device ID for filtering
        device_id = st.session_state.get("device_id", None)
        
        # Show existing tracked plants
        tracked_plants = get_unique_tracked_plants(device_id)
        
        tracking_option = st.radio(
            "What would you like to do?",
            ["🌱 Start tracking a new plant", "📈 Update existing plant"],
            key="tracking_option"
        )
        
        if tracking_option == "🌱 Start tracking a new plant":
            st.markdown("---")
            st.markdown("#### New Plant to Track")
            
            plant_nickname = st.text_input(
                "Give your plant a nickname",
                placeholder="e.g., Tomato Plant #1, Kitchen Basil",
                key="plant_nickname"
            )
            
            uploaded_file = st.file_uploader(
                "Take first photo",
                type=["jpg", "jpeg", "png"],
                key="new_tracking_uploader"
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="First scan", use_container_width=True)
                
                if st.button("🌱 Start Tracking", type="primary", use_container_width=True):
                    if not plant_nickname:
                        st.error("Please give your plant a nickname first!")
                    else:
                        start_new_plant_tracking(uploaded_file, plant_nickname, device_id)
        
        else:  # Update existing plant
            st.markdown("---")
            
            if not tracked_plants:
                st.info("No plants being tracked yet. Start tracking a new plant first!")
            else:
                # Plant selector
                plant_options = {
                    f"{p.get('plant_name', 'Unknown')} ({p.get('scan_count', 1)} scans)": p.get('tracking_id')
                    for p in tracked_plants
                }
                
                selected_plant = st.selectbox(
                    "Select plant to update",
                    options=list(plant_options.keys()),
                    key="tracked_plant_selector"
                )
                
                if selected_plant:
                    tracking_id = plant_options[selected_plant]
                    st.session_state.current_tracking_id = tracking_id
                    
                    # Show plant history
                    history = fetch_plant_history(tracking_id)
                    
                    if history:
                        st.markdown(f"**Last scanned:** {history[0].get('created_at', 'Unknown')[:10]}")
                        st.markdown(f"**Last status:** {history[0].get('health_status', 'Unknown')}")
                    
                    # Upload new scan
                    uploaded_file = st.file_uploader(
                        "Upload new scan",
                        type=["jpg", "jpeg", "png"],
                        key="update_tracking_uploader"
                    )
                    
                    if uploaded_file:
                        st.image(uploaded_file, caption="New scan", use_container_width=True)
                        
                        if st.button("📈 Add Scan & Compare", type="primary", use_container_width=True):
                            add_tracking_scan(uploaded_file, tracking_id, selected_plant.split(" (")[0], device_id)
    
    with col2:
        render_3d_preview()
        
        # Show progression analysis
        if st.session_state.progression_data:
            render_progression_analysis()


def render_progression_analysis():
    """Display health progression over time."""
    prog = st.session_state.progression_data
    
    st.markdown("### 📈 Health Progression")
    
    if not prog.get("has_history"):
        st.info(prog.get("message", "Start tracking to see progression"))
        return
    
    # Trend indicator
    trend = prog.get("trend", "stable")
    trend_emoji = prog.get("trend_emoji", "➡️")
    
    if trend == "improving":
        st.success(f"{trend_emoji} {prog.get('message', 'Improving!')}")
    elif trend == "declining":
        st.error(f"{trend_emoji} {prog.get('message', 'Declining')}")
    else:
        st.info(f"{trend_emoji} {prog.get('message', 'Stable')}")
    
    # Health metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Health", f"{prog.get('current_health', 0)}%")
    with col2:
        st.metric("First Scan", f"{prog.get('first_health', 0)}%")
    with col3:
        change = prog.get("health_change_total", 0)
        st.metric("Change", f"{change:+}%", delta=change)
    
    # Timeline
    timeline = prog.get("health_timeline", [])
    if timeline:
        st.markdown("**📅 Scan History:**")
        for entry in timeline[:5]:
            date = entry.get("date", "")[:10] if entry.get("date") else "Unknown"
            health = entry.get("health", 0)
            status = entry.get("status", "Unknown")
            
            # Color code based on health
            if health >= 80:
                color = "🟢"
            elif health >= 50:
                color = "🟡"
            else:
                color = "🔴"
            
            st.markdown(f"{color} **{date}** - {health}% ({status})")
    
    # Recommendation
    if prog.get("recommendation"):
        st.info(f"💡 **Recommendation:** {prog.get('recommendation')}")


def run_single_image_analysis(uploaded_file):
    """Run analysis on a single uploaded image."""
    with st.status("🔬 Gemini is analyzing your plant...", expanded=True) as status:
        st.write("🔍 Analyzing crop health...")
        analysis = analyze_crop_for_simulation(uploaded_file)
        
        if analysis:
            st.session_state.crop_analysis = analysis
            st.write(f"✅ Identified: {analysis.get('plant_name', 'Unknown')}")
            
            st.write("🧠 Analyzing plant structure for 3D modeling...")
            plant_structure = analyze_plant_structure(uploaded_file)
            
            if plant_structure:
                st.session_state.plant_structure = plant_structure
            
            st.write("🎨 Finalizing 3D model...")
            texture = generate_texture_from_upload(uploaded_file)
            
            if texture:
                st.session_state.generated_texture = texture
                st.session_state.simulation_active = True
                st.session_state.multi_angle_mode = False
                status.update(label="✅ 3D Plant Ready!", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="⚠️ Using fallback", state="complete")
                st.session_state.simulation_active = True
                st.rerun()
        else:
            status.update(label="❌ Analysis failed", state="error")
            st.error("Could not analyze the image. Please try a clearer photo.")


def run_multi_angle_analysis(uploaded_files):
    """Run analysis on multiple images from different angles."""
    with st.status(f"🔬 Analyzing {len(uploaded_files)} angles...", expanded=True) as status:
        st.write(f"📐 Processing {len(uploaded_files)} images from different angles...")
        
        # Run multi-angle analysis
        combined_analysis = analyze_multi_angle_images(uploaded_files)
        
        if combined_analysis:
            st.write(f"✅ Identified: {combined_analysis.get('identified_plant', {}).get('common_name', 'Unknown')}")
            st.write(f"✅ Analyzed from {combined_analysis.get('multi_angle_observations', {}).get('angles_analyzed', len(uploaded_files))} angles")
            
            # Use first image for texture
            st.write("🎨 Generating texture from primary image...")
            texture = generate_texture_from_upload(uploaded_files[0])
            
            # Convert multi-angle analysis to format expected by 3D renderer
            st.session_state.plant_structure = combined_analysis
            st.session_state.generated_texture = texture
            st.session_state.simulation_active = True
            st.session_state.multi_angle_mode = True
            
            # Also store crop analysis for display
            st.session_state.crop_analysis = {
                "plant_name": combined_analysis.get("identified_plant", {}).get("common_name", "Unknown") + 
                            f" ({combined_analysis.get('identified_plant', {}).get('scientific_name', '')})",
                "health_status": combined_analysis.get("health_analysis", {}).get("health_status", "Unknown"),
                "health_percentage": combined_analysis.get("health_analysis", {}).get("overall_health_percentage", 0),
                "disease_severity": combined_analysis.get("health_analysis", {}).get("disease_severity", "None"),
                "affected_area_percent": combined_analysis.get("health_analysis", {}).get("affected_area_percent", 0),
                "recommended_action": combined_analysis.get("recommended_action", "")
            }
            
            status.update(label="✅ Multi-Angle 3D Model Ready!", state="complete", expanded=False)
            st.rerun()
        else:
            status.update(label="❌ Multi-angle analysis failed", state="error")
            st.error("Could not analyze the images. Please try with clearer photos.")


def start_new_plant_tracking(uploaded_file, nickname, device_id):
    """Start tracking a new plant."""
    with st.status("🌱 Setting up plant tracking...", expanded=True) as status:
        # Generate tracking ID
        tracking_id = generate_tracking_id()
        st.write(f"📝 Created tracking ID: {tracking_id[:15]}...")
        
        # Analyze the plant
        st.write("🔬 Analyzing initial plant state...")
        analysis = analyze_crop_for_simulation(uploaded_file)
        plant_structure = analyze_plant_structure(uploaded_file)
        
        if analysis:
            # Upload image
            st.write("☁️ Uploading image...")
            image_url = upload_image_to_supabase(uploaded_file)
            
            # Combine analysis data
            combined_data = {**analysis, "plant_structure": plant_structure}
            
            # Save to database with tracking ID
            st.write("💾 Saving to database...")
            save_tracked_plant_scan(
                plant_name=nickname,
                image_url=image_url,
                json_data=combined_data,
                tracking_id=tracking_id,
                plant_nickname=nickname,
                device_id=device_id
            )
            
            # Update session state
            st.session_state.crop_analysis = analysis
            st.session_state.plant_structure = plant_structure
            st.session_state.generated_texture = generate_texture_from_upload(uploaded_file)
            st.session_state.simulation_active = True
            st.session_state.current_tracking_id = tracking_id
            st.session_state.progression_data = {
                "has_history": False,
                "trend": "first_scan",
                "message": "🌱 First scan recorded! Come back in a few days to add another scan and track progression.",
                "recommendation": "Continue monitoring your plant and add new scans regularly."
            }
            
            status.update(label="✅ Plant tracking started!", state="complete", expanded=False)
            st.rerun()
        else:
            status.update(label="❌ Failed to analyze", state="error")


def add_tracking_scan(uploaded_file, tracking_id, plant_name, device_id):
    """Add a new scan to an existing tracked plant."""
    with st.status("📈 Analyzing and comparing...", expanded=True) as status:
        # Get history
        st.write("📚 Fetching scan history...")
        history = fetch_plant_history(tracking_id)
        
        # Analyze current image
        st.write("🔬 Analyzing current state...")
        analysis = analyze_crop_for_simulation(uploaded_file)
        plant_structure = analyze_plant_structure(uploaded_file)
        
        if analysis:
            # Upload image
            st.write("☁️ Uploading image...")
            image_url = upload_image_to_supabase(uploaded_file)
            
            # Combine analysis data
            combined_data = {**analysis, "plant_structure": plant_structure}
            
            # Save new scan
            st.write("💾 Saving new scan...")
            save_tracked_plant_scan(
                plant_name=plant_name,
                image_url=image_url,
                json_data=combined_data,
                tracking_id=tracking_id,
                plant_nickname=plant_name,
                device_id=device_id
            )
            
            # Compare with history
            st.write("📊 Comparing with previous scans...")
            progression = compare_plant_health_over_time(analysis, history)
            
            # Update session state
            st.session_state.crop_analysis = analysis
            st.session_state.plant_structure = plant_structure
            st.session_state.generated_texture = generate_texture_from_upload(uploaded_file)
            st.session_state.simulation_active = True
            st.session_state.progression_data = progression
            
            status.update(label="✅ Scan added & compared!", state="complete", expanded=False)
            st.rerun()
        else:
            status.update(label="❌ Failed to analyze", state="error")


def render_3d_preview():
    """Render the 3D simulation preview with growth simulation controls."""
    st.markdown("### 🎮 3D Simulation")
    
    if st.session_state.simulation_active:
        # Apply growth simulation if plant structure exists
        plant_structure = st.session_state.plant_structure
        
        if plant_structure:
            # Integrate growth simulation controls (renders expander with sliders)
            # Returns modified structure based on growth stage and scenarios
            modified_structure = integrate_growth_simulation(plant_structure)
            
            # Render 3D with potentially modified structure
            render_3d_simulation(
                texture_data=st.session_state.generated_texture,
                plant_structure=modified_structure,
                height=400
            )
            
            # Show growth timeline for the plant
            plant_name = plant_structure.get("identified_plant", {}).get("common_name", "Plant")
            render_growth_timeline(plant_name)
        else:
            render_3d_simulation(
                texture_data=st.session_state.generated_texture,
                plant_structure=plant_structure,
                height=400
            )
        
        # Show analysis results
        if st.session_state.crop_analysis:
            render_analysis_results()
    else:
        render_3d_simulation(texture_data=None, plant_structure=None, height=400)
        st.caption("Upload an image to generate a 3D digital twin.")


def render_analysis_results():
    """Display analysis results below the 3D view."""
    st.markdown("### 📊 Analysis Results")
    analysis = st.session_state.crop_analysis
    
    health_status = analysis.get("health_status", "Unknown")
    health_pct = analysis.get("health_percentage", 0)
    
    if health_status == "Healthy" or health_pct >= 80:
        st.success(f"🌿 **{analysis.get('plant_name', 'Unknown')}** - Healthy ({health_pct}%)")
    elif health_pct >= 50:
        st.warning(f"⚠️ **{analysis.get('plant_name', 'Unknown')}** - {health_status} ({health_pct}%)")
    else:
        st.error(f"🔴 **{analysis.get('plant_name', 'Unknown')}** - {health_status} ({health_pct}%)")
    
    met_col1, met_col2 = st.columns(2)
    with met_col1:
        st.metric("Health Score", f"{health_pct}%")
    with met_col2:
        severity = analysis.get("disease_severity", "None")
        st.metric("Severity", severity)
    
    affected = analysis.get("affected_area_percent", 0)
    st.progress(min(affected / 100, 1.0), text=f"Affected Area: {affected}%")
    
    if analysis.get("recommended_action"):
        st.info(f"💡 **Recommendation:** {analysis.get('recommended_action')}")


def reset_simulation():
    """Reset all simulation state."""
    st.session_state.generated_texture = None
    st.session_state.crop_analysis = None
    st.session_state.plant_structure = None
    st.session_state.simulation_active = False
    st.session_state.progression_data = None
    st.session_state.multi_angle_mode = False
    st.rerun()


view_digital_twin()
