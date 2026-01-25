import plotly.graph_objects as go
import numpy as np
import json
import random
from scipy.spatial import Delaunay

def render_twin_from_json(json_data):
    """
    Takes a JSON object (from Gemini) and returns a 3D Plotly Figure.
    Renders a hyper-realistic digital twin based on plant biometrics.
    """
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except:
            data = {} 
    else:
        data = json_data
        
    structure = data.get("structure_type", "rosette")
    
    if structure == "rosette":
        return _draw_rosette_pattern(data)
    elif structure == "stalk":
        return _draw_stalk_pattern(data)
    else:
        return _draw_generic_pattern(data)


# ==========================================
# HYPER-REALISTIC LETTUCE DIGITAL TWIN
# Based on image analysis: Loose-leaf lettuce variety
# Dense rosette pattern with frilly, ruffled edges
# ==========================================

def _draw_rosette_pattern(data):
    """
    Draws realistic loose-leaf lettuce rosettes matching the reference image.
    Key features: Dense leaves, frilly edges, lime-green gradient, terracotta pot.
    """
    fig = go.Figure()
    
    # === CONFIGURATION FROM JSON ===
    num_plants = data.get("plant_count", 3)
    base_spread = data.get("estimated_spread_cm", 25)
    plant_name = data.get("plant_name", "Lettuce")
    health = data.get("health_status", "healthy")
    
    # Leaf density based on health and JSON data
    base_leaf_count = data.get("leaf_count", 35)
    leaves_per_plant = max(40, base_leaf_count + 15)  # Dense rosette
    
    # === REALISTIC COLOR PALETTE (from image analysis) ===
    # Inner leaves: bright lime-green (#9ACD32 to #ADFF2F)
    # Middle leaves: vibrant green (#66CD00 to #32CD32)
    # Outer leaves: slightly darker (#228B22 to #2E8B57)
    
    if health == "healthy":
        leaf_colorscale = [
            [0.0, "#ADFF2F"],   # GreenYellow - inner/new leaves
            [0.2, "#9ACD32"],   # YellowGreen
            [0.4, "#7CFC00"],   # LawnGreen
            [0.6, "#32CD32"],   # LimeGreen
            [0.8, "#228B22"],   # ForestGreen
            [1.0, "#2E8B57"],   # SeaGreen - outer/older leaves
        ]
    else:
        # Unhealthy - more yellow/brown tones
        leaf_colorscale = [
            [0.0, "#DAA520"],
            [0.5, "#9ACD32"],
            [1.0, "#556B2F"],
        ]
    
    # === ENVIRONMENT SETUP ===
    pot_length = base_spread * num_plants * 0.85
    pot_width = base_spread * 1.1
    
    # Add terracotta pot with realistic details
    _add_terracotta_pot(fig, pot_width, pot_length)
    
    # Add rich dark soil with organic matter texture
    _add_realistic_soil(fig, pot_width, pot_length)
    
    # === PLANT POSITIONS (evenly spaced in pot) ===
    spacing = pot_length * 1.0 / (num_plants + 0.5)
    positions = [(i - (num_plants - 1) / 2) * spacing for i in range(num_plants)]
    
    # === DRAW EACH LETTUCE PLANT ===
    for plant_idx, x_pos in enumerate(positions):
        random.seed(plant_idx * 42 + 123)
        np.random.seed(plant_idx * 42 + 123)
        
        # Slight variation in plant size (natural look)
        plant_scale = random.uniform(0.85, 1.0)
        local_spread = base_spread * plant_scale
        
        # Small random offset for natural placement
        x_offset = x_pos + random.uniform(-1.5, 1.5)
        y_offset = random.uniform(-1.0, 1.0)
        
        _draw_single_lettuce_rosette(
            fig, 
            x_offset, 
            y_offset, 
            local_spread, 
            leaves_per_plant, 
            leaf_colorscale,
            plant_idx
        )
    
    # === FINAL LAYOUT ===
    _set_common_layout(
        fig, 
        plant_name, 
        z_range=[-12, 28],
        camera_eye=dict(x=0.8, y=-2.2, z=1.0)  # Slight angle like photo
    )
    
    return fig


def _draw_single_lettuce_rosette(fig, x_center, y_center, spread, num_leaves, colorscale, seed_offset):
    """
    Draws a single lettuce rosette with realistic frilly leaves.
    Uses golden angle (137.5°) for natural phyllotaxis pattern.
    """
    random.seed(seed_offset * 100)
    
    # === LEAF LAYERS (inner to outer) ===
    # More leaves = denser, more realistic appearance
    
    for leaf_idx in range(num_leaves):
        # === PHYLLOTAXIS ANGLE (Golden Angle) ===
        golden_angle = 137.5
        base_angle = leaf_idx * golden_angle
        # Add slight randomness for natural look
        angle_rad = np.radians(base_angle + random.uniform(-8, 8))
        
        # === AGE FACTOR (0 = center/young, 1 = outer/old) ===
        age_factor = leaf_idx / num_leaves
        
        # === LEAF DIMENSIONS ===
        # Inner leaves are smaller and more upright
        # Outer leaves are larger and more spread out
        # Photo analysis: lettuce heads are ~15-18cm tall, dome-shaped
        
        min_length = spread * 0.12
        max_length = spread * 0.65
        leaf_length = min_length + (age_factor ** 0.6) * (max_length - min_length)
        
        # Width varies - lettuce has wide, ruffled leaves
        width_ratio = 0.75 + random.uniform(-0.1, 0.15)
        leaf_width = leaf_length * width_ratio
        
        # === LEAF TILT (angle from vertical) ===
        # Inner leaves: nearly vertical (cupping upward to form dome)
        # Middle leaves: slight outward tilt
        # Outer leaves: more horizontal but still rising
        # This creates the tall dome shape seen in photo
        if age_factor < 0.3:
            # Inner leaves - very upright (0.1 to 0.25 radians = ~6-14 degrees)
            base_tilt = 0.1 + age_factor * 0.5
        elif age_factor < 0.6:
            # Middle leaves - moderate tilt (0.25 to 0.55 radians = ~14-31 degrees)
            base_tilt = 0.25 + (age_factor - 0.3) * 1.0
        else:
            # Outer leaves - more spread but still upward (0.55 to 0.85 radians = ~31-49 degrees)
            base_tilt = 0.55 + (age_factor - 0.6) * 0.75
        tilt = base_tilt + random.uniform(-0.08, 0.08)
        
        # === GENERATE LEAF SURFACE ===
        leaf_mesh = _create_frilly_leaf(
            leaf_length, 
            leaf_width, 
            age_factor,
            ruffle_intensity=0.8 + age_factor * 0.4
        )
        
        # === TRANSFORM LEAF TO POSITION ===
        x_leaf, y_leaf, z_leaf, intensity = _transform_leaf(
            leaf_mesh, 
            angle_rad, 
            tilt, 
            x_center, 
            y_center,
            age_factor
        )
        
        # === ADD TO FIGURE ===
        fig.add_trace(go.Mesh3d(
            x=x_leaf,
            y=y_leaf,
            z=z_leaf,
            intensity=intensity,
            colorscale=colorscale,
            showscale=False,
            opacity=0.95,
            lighting=dict(
                ambient=0.5,
                diffuse=0.85,
                roughness=0.6,
                specular=0.25,
                fresnel=0.15
            ),
            lightposition=dict(x=100, y=-200, z=300),
            hoverinfo='skip',
            showlegend=False
        ))


def _create_frilly_leaf(length, width, age_factor, ruffle_intensity=1.0):
    """
    Creates a single frilly lettuce leaf with realistic ruffled edges.
    Returns (x, y, z, intensity) arrays for the leaf surface.
    """
    # Higher resolution for smooth ruffles
    u_res = 25  # Along leaf length
    v_res = 20  # Across leaf width
    
    u = np.linspace(0, 1, u_res)
    v = np.linspace(-1, 1, v_res)
    U, V = np.meshgrid(u, v)
    
    # === BASE LEAF SHAPE ===
    # X: extends along the leaf length
    x_base = U * length
    
    # Y: width tapers at base and tip (elliptical envelope)
    taper = np.sqrt(1 - (2*U - 1)**4) * 0.95  # Smooth taper
    y_base = V * width * 0.5 * taper
    
    # === FRILLY EDGE RUFFLES (key characteristic) ===
    # Multiple frequencies for complex ruffle pattern
    ruffle_freq_1 = 12  # Main ruffle frequency
    ruffle_freq_2 = 20  # Fine detail
    ruffle_freq_3 = 6   # Broad waves
    
    # Ruffles increase toward edges (|V| close to 1)
    edge_factor = np.abs(V) ** 1.5
    
    # Ruffles increase toward outer parts of leaf (high U)
    length_factor = U ** 0.8
    
    # Combined ruffle pattern
    ruffle = (
        np.sin(U * ruffle_freq_1 * np.pi + V * 4) * 0.4 +
        np.sin(U * ruffle_freq_2 * np.pi - V * 8) * 0.2 +
        np.sin(V * ruffle_freq_3 * np.pi + U * 3) * 0.3
    ) * edge_factor * length_factor * ruffle_intensity * (length * 0.12)
    
    # === CENTRAL VEIN DEPRESSION ===
    vein_depth = np.exp(-V**2 * 8) * U * length * 0.03
    
    # === LEAF CURL (cupping) ===
    # Creates the curved, cupped appearance - stronger curl for dome shape
    curl_amount = (1 - age_factor) * 0.25 + 0.08
    curl = -(V ** 2) * curl_amount * length
    
    # === VERTICAL ARCH (key for height) ===
    # Leaves arch upward then curve back - creates the tall dome
    # Inner leaves arch more, outer leaves less
    arch_strength = (1 - age_factor) * 0.4 + 0.15
    vertical_arch = np.sin(U * np.pi * 0.8) * arch_strength * length
    
    # === NATURAL WAVE (undulation) ===
    wave = np.sin(U * np.pi * 2.5) * (1 - np.abs(V)) * length * 0.06
    
    # === COMBINE Z COMPONENTS ===
    z_base = ruffle + curl + wave + vertical_arch - vein_depth
    
    # === INTENSITY FOR COLORING (age-based) ===
    # Center/base = young (low intensity = bright green)
    # Edge/tip = older (high intensity = darker green)
    intensity = (U * 0.6 + (1 - np.exp(-V**2 * 2)) * 0.4) * age_factor + (1 - age_factor) * 0.2
    
    return x_base, y_base, z_base, intensity


def _transform_leaf(leaf_mesh, angle_rad, tilt, x_center, y_center, age_factor):
    """
    Transforms leaf from local coords to world position.
    Applies rotation, tilt, and translation.
    """
    x_local, y_local, z_local, intensity = leaf_mesh
    
    # === TILT (rotation around Y axis - makes leaf spread outward) ===
    cos_tilt = np.cos(tilt)
    sin_tilt = np.sin(tilt)
    
    x_tilted = x_local * cos_tilt - z_local * sin_tilt
    z_tilted = x_local * sin_tilt + z_local * cos_tilt
    y_tilted = y_local
    
    # === ROTATION (around Z axis - position in rosette) ===
    cos_rot = np.cos(angle_rad)
    sin_rot = np.sin(angle_rad)
    
    x_rot = x_tilted * cos_rot - y_tilted * sin_rot
    y_rot = x_tilted * sin_rot + y_tilted * cos_rot
    z_rot = z_tilted
    
    # === HEIGHT OFFSET (creates tall dome shape like in photo) ===
    # Photo analysis: lettuce is ~15-18cm tall
    # Inner leaves sit at the peak of the dome
    # Height decreases gradually toward outer leaves
    base_height = 2.0  # Soil level offset
    inner_height = 14.0  # Peak height for innermost leaves
    outer_height = 4.0   # Height for outermost leaves
    
    # Smooth interpolation - creates dome profile
    dome_factor = (1 - age_factor) ** 1.5  # More height in center
    z_offset = base_height + dome_factor * (inner_height - outer_height) + outer_height * (1 - dome_factor * 0.5)
    
    # === FINAL POSITION ===
    x_final = x_rot + x_center
    y_final = y_rot + y_center
    z_final = z_rot + z_offset
    
    # Flatten and triangulate for Mesh3d
    x_flat = x_final.flatten()
    y_flat = y_final.flatten()
    z_flat = z_final.flatten()
    intensity_flat = intensity.flatten()
    
    return x_flat, y_flat, z_flat, intensity_flat


def _add_terracotta_pot(fig, width, length):
    """
    Creates a realistic terracotta rectangular planter.
    Matches the brown/orange pot in the reference image.
    """
    # Pot dimensions - sized to contain soil
    l = length * 0.62
    w = width * 0.55
    pot_bottom = -8
    pot_top = 2  # Rim slightly above soil level
    
    # Terracotta colors
    pot_main = "#C66B3D"
    pot_dark = "#A85A30"
    pot_light = "#D4764A"
    
    # === SIMPLE BOX POT WITH 4 WALLS ===
    
    # Front wall (y = -w)
    _add_pot_wall(fig, 
        x_coords=[-l, l, l, -l],
        y_coords=[-w, -w, -w, -w],
        z_coords=[pot_top, pot_top, pot_bottom, pot_bottom],
        color=pot_main)
    
    # Back wall (y = +w) 
    _add_pot_wall(fig,
        x_coords=[-l, l, l, -l],
        y_coords=[w, w, w, w],
        z_coords=[pot_top, pot_top, pot_bottom, pot_bottom],
        color=pot_main)
    
    # Left wall (x = -l)
    _add_pot_wall(fig,
        x_coords=[-l, -l, -l, -l],
        y_coords=[-w, w, w, -w],
        z_coords=[pot_top, pot_top, pot_bottom, pot_bottom],
        color=pot_dark)
    
    # Right wall (x = +l)
    _add_pot_wall(fig,
        x_coords=[l, l, l, l],
        y_coords=[-w, w, w, -w],
        z_coords=[pot_top, pot_top, pot_bottom, pot_bottom],
        color=pot_light)
    
    # Rim (top edge - slightly wider)
    rim_l = l + 1.5
    rim_w = w + 1.5
    rim_thickness = 1.5
    
    # Front rim
    _add_pot_wall(fig,
        x_coords=[-rim_l, rim_l, rim_l, -rim_l],
        y_coords=[-rim_w, -rim_w, -w, -w],
        z_coords=[pot_top + rim_thickness, pot_top + rim_thickness, pot_top, pot_top],
        color=pot_light)
    
    # Back rim
    _add_pot_wall(fig,
        x_coords=[-rim_l, rim_l, rim_l, -rim_l],
        y_coords=[rim_w, rim_w, w, w],
        z_coords=[pot_top + rim_thickness, pot_top + rim_thickness, pot_top, pot_top],
        color=pot_main)
    
    # Left rim
    _add_pot_wall(fig,
        x_coords=[-rim_l, -rim_l, -l, -l],
        y_coords=[-rim_w, rim_w, w, -w],
        z_coords=[pot_top + rim_thickness, pot_top + rim_thickness, pot_top, pot_top],
        color=pot_dark)
    
    # Right rim
    _add_pot_wall(fig,
        x_coords=[rim_l, rim_l, l, l],
        y_coords=[-rim_w, rim_w, w, -w],
        z_coords=[pot_top + rim_thickness, pot_top + rim_thickness, pot_top, pot_top],
        color=pot_light)


def _add_pot_wall(fig, x_coords, y_coords, z_coords, color):
    """Helper to add a single pot wall as a quad."""
    fig.add_trace(go.Mesh3d(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        i=[0, 0],
        j=[1, 2],
        k=[2, 3],
        color=color,
        flatshading=True,
        lighting=dict(ambient=0.6, diffuse=0.7, specular=0.15, roughness=0.8),
        hoverinfo='skip',
        showlegend=False
    ))


def _add_realistic_soil(fig, width, length):
    """
    Creates realistic dark soil with organic matter texture.
    Matches the rich, dark soil visible in the reference image.
    """
    l = length * 0.60
    w = width * 0.53
    
    # High-resolution grid for detailed texture
    res = 60
    x_grid = np.linspace(-l, l, res)
    y_grid = np.linspace(-w, w, res)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # === SOIL TEXTURE ===
    np.random.seed(42)
    
    # Base height - raised up so it's visible above pot interior
    Z = np.ones_like(X) * 0.0
    
    # Random bumps (soil clumps)
    for _ in range(20):
        cx, cy = random.uniform(-l*0.8, l*0.8), random.uniform(-w*0.8, w*0.8)
        r = random.uniform(1.5, 4)
        h = random.uniform(0.2, 0.6)
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        Z += h * np.exp(-dist**2 / (2 * r**2))
    
    # Fine noise texture
    noise = np.random.uniform(-0.15, 0.15, X.shape)
    Z += noise
    
    # Slight mounding in center where plants grow
    center_mound = np.exp(-(X**2 + Y**2) / (l * w * 0.5)) * 0.3
    Z += center_mound
    
    # === SOIL COLOR (rich dark brown/black) ===
    soil_colorscale = [
        [0.0, "#1A0F0A"],   # Very dark (wet soil)
        [0.3, "#2C1810"],   # Dark brown
        [0.5, "#3D2817"],   # Medium brown
        [0.7, "#4A3520"],   # Brown with organic matter
        [1.0, "#5C4033"],   # Lighter brown (dry spots)
    ]
    
    # Intensity based on height (darker in low spots = wet)
    Z_norm = (Z - Z.min()) / (Z.max() - Z.min() + 0.001)
    
    fig.add_trace(go.Surface(
        x=X, 
        y=Y, 
        z=Z,
        surfacecolor=Z_norm,
        colorscale=soil_colorscale,
        showscale=False,
        lighting=dict(ambient=0.5, diffuse=0.7, roughness=0.9, specular=0.05),
        hoverinfo='skip',
        name="Soil"
    ))
    
    # === ADD SMALL DEBRIS/MULCH PIECES ===
    num_debris = 30
    for _ in range(num_debris):
        dx = random.uniform(-l*0.9, l*0.9)
        dy = random.uniform(-w*0.9, w*0.9)
        dz = 0.3 + random.uniform(0, 0.3)
        size = random.uniform(0.4, 1.0)
        
        # Small wood chip / mulch piece
        debris_x = [dx-size, dx+size, dx+size*0.5, dx-size*0.5]
        debris_y = [dy-size*0.3, dy-size*0.3, dy+size*0.3, dy+size*0.3]
        debris_z = [dz, dz, dz+0.15, dz+0.15]
        
        fig.add_trace(go.Mesh3d(
            x=debris_x,
            y=debris_y,
            z=debris_z,
            color=random.choice(["#2F1B0C", "#3D2817", "#1F1208", "#4A3520"]),
            opacity=0.95,
            hoverinfo='skip',
            showlegend=False
        ))


# ==========================================
# OTHER PATTERN TYPES
# ==========================================

def _draw_stalk_pattern(data):
    """For stalk-based plants like corn, wheat, etc."""
    fig = go.Figure()
    _set_common_layout(fig, "Corn", [0, 100], dict(x=0.0, y=-2.5, z=0.5))
    return fig


def _draw_generic_pattern(data):
    """Fallback for unknown plant types."""
    fig = go.Figure()
    _set_common_layout(fig, "Generic Plant", [0, 50], dict(x=0.0, y=-2.5, z=0.5))
    return fig


# ==========================================
# LAYOUT & UTILITIES
# ==========================================

def _set_common_layout(fig, title, z_range, camera_eye):
    """Sets consistent layout for all plant visualizations."""
    fig.update_layout(
        title=dict(
            text=f"🧬 Digital Twin: {title}",
            font=dict(size=20, color="#00FF88"),
            x=0.5,
            xanchor='center'
        ),
        paper_bgcolor="#0a0a0a",
        plot_bgcolor="#0a0a0a",
        scene=dict(
            xaxis=dict(visible=False, showgrid=False, zeroline=False),
            yaxis=dict(visible=False, showgrid=False, zeroline=False),
            zaxis=dict(visible=False, showgrid=False, zeroline=False, range=z_range),
            aspectmode='data',
            camera=dict(
                eye=camera_eye,
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0)
            ),
            bgcolor="#0a0a0a"
        ),
        font=dict(color="white", family="Arial"),
        margin=dict(l=0, r=0, b=0, t=50),
        showlegend=False
    )