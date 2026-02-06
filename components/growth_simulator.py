"""
Growth Simulator Module for Digital Twin
Provides growth stage simulation, "what-if" scenarios, and harvest prediction.
Integrates with the existing digital_twin.py without modifying it.
"""

import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

# ============================================================================
# GROWTH STAGES CONFIGURATION
# ============================================================================

GROWTH_STAGES = {
    "seed": {
        "name": "Seed/Germination",
        "icon": "🌰",
        "scale": 0.05,
        "leaf_factor": 0.0,
        "fruit_factor": 0.0,
        "height_factor": 0.05,
        "color_shift": 0.0,
        "days_range": (0, 7),
        "description": "Seed germinating underground"
    },
    "seedling": {
        "name": "Seedling",
        "icon": "🌱",
        "scale": 0.2,
        "leaf_factor": 0.15,
        "fruit_factor": 0.0,
        "height_factor": 0.15,
        "color_shift": 0.1,  # Lighter green
        "days_range": (7, 21),
        "description": "First true leaves emerging"
    },
    "vegetative": {
        "name": "Vegetative Growth",
        "icon": "🌿",
        "scale": 0.5,
        "leaf_factor": 0.6,
        "fruit_factor": 0.0,
        "height_factor": 0.5,
        "color_shift": 0.0,
        "days_range": (21, 45),
        "description": "Rapid leaf and stem development"
    },
    "flowering": {
        "name": "Flowering",
        "icon": "🌸",
        "scale": 0.75,
        "leaf_factor": 0.85,
        "fruit_factor": 0.1,
        "height_factor": 0.8,
        "color_shift": 0.0,
        "days_range": (45, 60),
        "description": "Producing flowers for reproduction"
    },
    "fruiting": {
        "name": "Fruiting",
        "icon": "🍅",
        "scale": 0.9,
        "leaf_factor": 0.9,
        "fruit_factor": 0.7,
        "height_factor": 0.95,
        "color_shift": 0.0,
        "days_range": (60, 80),
        "description": "Fruits developing and growing"
    },
    "mature": {
        "name": "Mature/Harvest Ready",
        "icon": "🌾",
        "scale": 1.0,
        "leaf_factor": 1.0,
        "fruit_factor": 1.0,
        "height_factor": 1.0,
        "color_shift": 0.0,
        "days_range": (80, 100),
        "description": "Ready for harvest"
    },
    "senescence": {
        "name": "Post-Harvest/Decline",
        "icon": "🍂",
        "scale": 0.9,
        "leaf_factor": 0.7,
        "fruit_factor": 0.3,
        "height_factor": 0.95,
        "color_shift": -0.2,  # Yellowing
        "days_range": (100, 120),
        "description": "Natural decline after harvest window"
    }
}

# ============================================================================
# PLANT-SPECIFIC GROWTH DATA
# ============================================================================

PLANT_GROWTH_DATA = {
    # Vegetables
    "tomato": {"days_to_harvest": 70, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "pepper": {"days_to_harvest": 75, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "eggplant": {"days_to_harvest": 80, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "lettuce": {"days_to_harvest": 45, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "cabbage": {"days_to_harvest": 70, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "cauliflower": {"days_to_harvest": 80, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "broccoli": {"days_to_harvest": 65, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "carrot": {"days_to_harvest": 75, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "onion": {"days_to_harvest": 100, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "cucumber": {"days_to_harvest": 55, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "squash": {"days_to_harvest": 50, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    
    # Philippine crops
    "rice": {"days_to_harvest": 120, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "corn": {"days_to_harvest": 90, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "kangkong": {"days_to_harvest": 30, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "pechay": {"days_to_harvest": 30, "stages": ["seed", "seedling", "vegetative", "mature"]},
    "sitaw": {"days_to_harvest": 55, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "ampalaya": {"days_to_harvest": 60, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    "talong": {"days_to_harvest": 80, "stages": ["seed", "seedling", "vegetative", "flowering", "fruiting", "mature"]},
    
    # Default for unknown plants
    "default": {"days_to_harvest": 60, "stages": ["seed", "seedling", "vegetative", "flowering", "mature"]}
}

# ============================================================================
# WHAT-IF SCENARIO EFFECTS
# ============================================================================

SCENARIO_EFFECTS = {
    "water": {
        "low": {
            "name": "Under-watered",
            "icon": "💧",
            "growth_modifier": 0.6,
            "health_impact": -0.2,
            "color_effect": {"hue": 0, "saturation": -0.2, "lightness": -0.1},
            "leaf_droop": 0.3,
            "description": "Wilting, slower growth, leaf curling"
        },
        "optimal": {
            "name": "Optimal Watering",
            "icon": "💦",
            "growth_modifier": 1.0,
            "health_impact": 0.0,
            "color_effect": {"hue": 0, "saturation": 0, "lightness": 0},
            "leaf_droop": 0.0,
            "description": "Healthy, vibrant growth"
        },
        "high": {
            "name": "Over-watered",
            "icon": "🌊",
            "growth_modifier": 0.8,
            "health_impact": -0.15,
            "color_effect": {"hue": 0.05, "saturation": -0.1, "lightness": 0.05},
            "leaf_droop": 0.1,
            "description": "Risk of root rot, yellowing leaves"
        }
    },
    "sunlight": {
        "low": {
            "name": "Low Light",
            "icon": "🌑",
            "growth_modifier": 0.5,
            "health_impact": -0.1,
            "color_effect": {"hue": 0.05, "saturation": -0.15, "lightness": 0.1},
            "stretch_factor": 1.3,  # Etiolation
            "description": "Leggy growth, pale leaves"
        },
        "optimal": {
            "name": "Optimal Light",
            "icon": "☀️",
            "growth_modifier": 1.0,
            "health_impact": 0.0,
            "color_effect": {"hue": 0, "saturation": 0, "lightness": 0},
            "stretch_factor": 1.0,
            "description": "Compact, healthy growth"
        },
        "high": {
            "name": "Intense Sun",
            "icon": "🔥",
            "growth_modifier": 0.9,
            "health_impact": -0.1,
            "color_effect": {"hue": -0.02, "saturation": 0.1, "lightness": -0.1},
            "stretch_factor": 0.9,
            "description": "Possible leaf burn, compact growth"
        }
    },
    "nutrients": {
        "low": {
            "name": "Nutrient Deficient",
            "icon": "📉",
            "growth_modifier": 0.6,
            "health_impact": -0.2,
            "color_effect": {"hue": 0.1, "saturation": -0.3, "lightness": 0.1},  # Yellowing
            "leaf_size_modifier": 0.7,
            "description": "Yellowing, stunted growth, small leaves"
        },
        "optimal": {
            "name": "Well Fertilized",
            "icon": "🌱",
            "growth_modifier": 1.0,
            "health_impact": 0.0,
            "color_effect": {"hue": 0, "saturation": 0, "lightness": 0},
            "leaf_size_modifier": 1.0,
            "description": "Optimal nutrient balance"
        },
        "high": {
            "name": "Over-fertilized",
            "icon": "⚠️",
            "growth_modifier": 0.85,
            "health_impact": -0.15,
            "color_effect": {"hue": -0.05, "saturation": 0.1, "lightness": -0.15},  # Dark, burnt tips
            "leaf_size_modifier": 1.1,
            "description": "Fertilizer burn, dark leaves, crispy tips"
        }
    }
}


# ============================================================================
# GROWTH SIMULATOR CLASS
# ============================================================================

class GrowthSimulator:
    """
    Manages growth simulation state and calculations.
    """
    
    def __init__(self, plant_structure: dict):
        self.original_structure = plant_structure.copy() if plant_structure else {}
        self.plant_name = self._extract_plant_name()
        self.growth_data = self._get_growth_data()
        
        # Simulation state
        self.current_stage = "mature"
        self.growth_percentage = 100
        self.scenarios = {
            "water": "optimal",
            "sunlight": "optimal",
            "nutrients": "optimal"
        }
        
    def _extract_plant_name(self) -> str:
        """Extract plant name from structure."""
        name = self.original_structure.get("identified_plant", {}).get("common_name", "Plant")
        return name.lower().split("(")[0].strip()
    
    def _get_growth_data(self) -> dict:
        """Get growth data for this plant type."""
        # Try to match plant name
        for key in PLANT_GROWTH_DATA:
            if key in self.plant_name or self.plant_name in key:
                return PLANT_GROWTH_DATA[key]
        return PLANT_GROWTH_DATA["default"]
    
    def get_stage_from_percentage(self, percentage: int) -> str:
        """Convert percentage (0-100) to growth stage."""
        stages = self.growth_data["stages"]
        num_stages = len(stages)
        
        if percentage <= 0:
            return stages[0]
        if percentage >= 100:
            return stages[-1]
        
        stage_index = int((percentage / 100) * (num_stages - 1))
        return stages[min(stage_index, num_stages - 1)]
    
    def calculate_days_to_harvest(self, current_percentage: int) -> int:
        """Calculate days remaining to harvest."""
        total_days = self.growth_data["days_to_harvest"]
        current_days = (current_percentage / 100) * total_days
        return max(0, int(total_days - current_days))
    
    def get_harvest_date(self, current_percentage: int) -> str:
        """Get predicted harvest date."""
        days_remaining = self.calculate_days_to_harvest(current_percentage)
        harvest_date = datetime.now() + timedelta(days=days_remaining)
        return harvest_date.strftime("%B %d, %Y")
    
    def apply_growth_modifiers(self, structure: dict, percentage: int) -> dict:
        """Apply growth stage modifications to plant structure."""
        modified = json.loads(json.dumps(structure))  # Deep copy
        
        stage_name = self.get_stage_from_percentage(percentage)
        stage = GROWTH_STAGES.get(stage_name, GROWTH_STAGES["mature"])
        
        # Apply scale factors
        if "plant_architecture" in modified:
            arch = modified["plant_architecture"]
            if "height_cm" in arch:
                arch["height_cm"] = int(arch["height_cm"] * stage["height_factor"])
            if "fruit_count" in arch:
                arch["fruit_count"] = int(arch.get("fruit_count", 0) * stage["fruit_factor"])
        
        if "leaf_system" in modified:
            leaves = modified["leaf_system"]
            if "total_count" in leaves:
                leaves["total_count"] = max(2, int(leaves["total_count"] * stage["leaf_factor"]))
            if "size_cm" in leaves:
                leaves["size_cm"] = int(leaves.get("size_cm", 20) * stage["scale"])
        
        # Store growth metadata for 3D renderer
        modified["growth_simulation"] = {
            "stage": stage_name,
            "stage_display": stage["name"],
            "scale": stage["scale"],
            "percentage": percentage,
            "leaf_factor": stage["leaf_factor"],
            "fruit_factor": stage["fruit_factor"],
            "color_shift": stage["color_shift"]
        }
        
        return modified
    
    def apply_scenario_effects(self, structure: dict) -> dict:
        """Apply what-if scenario effects to plant structure."""
        modified = json.loads(json.dumps(structure))  # Deep copy
        
        # Combine effects from all scenarios
        total_growth_modifier = 1.0
        total_health_impact = 0.0
        combined_color = {"hue": 0, "saturation": 0, "lightness": 0}
        total_droop = 0.0
        total_stretch = 1.0
        leaf_size_mod = 1.0
        
        active_effects = []
        
        for scenario_type, level in self.scenarios.items():
            effect = SCENARIO_EFFECTS[scenario_type][level]
            total_growth_modifier *= effect["growth_modifier"]
            total_health_impact += effect["health_impact"]
            
            color_eff = effect.get("color_effect", {})
            combined_color["hue"] += color_eff.get("hue", 0)
            combined_color["saturation"] += color_eff.get("saturation", 0)
            combined_color["lightness"] += color_eff.get("lightness", 0)
            
            total_droop += effect.get("leaf_droop", 0)
            total_stretch *= effect.get("stretch_factor", 1.0)
            leaf_size_mod *= effect.get("leaf_size_modifier", 1.0)
            
            if level != "optimal":
                active_effects.append(f"{effect['icon']} {effect['name']}")
        
        # Store scenario effects for 3D renderer
        modified["scenario_effects"] = {
            "growth_modifier": total_growth_modifier,
            "health_impact": total_health_impact,
            "color_shift": combined_color,
            "leaf_droop": min(total_droop, 0.5),
            "stretch_factor": total_stretch,
            "leaf_size_modifier": leaf_size_mod,
            "active_effects": active_effects,
            "scenarios": self.scenarios.copy()
        }
        
        return modified
    
    def get_modified_structure(self, percentage: int) -> dict:
        """Get fully modified plant structure with growth and scenarios applied."""
        structure = self.apply_growth_modifiers(self.original_structure, percentage)
        structure = self.apply_scenario_effects(structure)
        return structure


# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def render_growth_controls(plant_structure: dict, key_prefix: str = "") -> dict:
    """
    Render growth simulation controls in Streamlit sidebar or expander.
    Returns modified plant structure based on user inputs.
    
    Args:
        plant_structure: The plant structure dict to modify
        key_prefix: Unique prefix for widget keys to avoid duplicates across tabs
    """
    
    # Initialize simulator in session state
    if "growth_simulator" not in st.session_state:
        st.session_state.growth_simulator = GrowthSimulator(plant_structure)
    
    simulator = st.session_state.growth_simulator
    
    # Update original structure if changed
    if plant_structure != simulator.original_structure:
        simulator = GrowthSimulator(plant_structure)
        st.session_state.growth_simulator = simulator
    
    modified_structure = plant_structure
    
    with st.expander("🌱 Growth Simulation", expanded=False):
        st.markdown("##### Simulate Plant Growth Stages")
        
        # Growth stage slider
        growth_pct = st.slider(
            "Growth Progress",
            min_value=0,
            max_value=100,
            value=st.session_state.get("growth_percentage", 100),
            step=5,
            format="%d%%",
            help="Slide to see the plant at different growth stages",
            key=f"{key_prefix}growth_progress_slider"
        )
        st.session_state.growth_percentage = growth_pct
        
        # Show current stage info
        stage_name = simulator.get_stage_from_percentage(growth_pct)
        stage_info = GROWTH_STAGES[stage_name]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Current Stage",
                value=f"{stage_info['icon']} {stage_info['name']}"
            )
        with col2:
            days_to_harvest = simulator.calculate_days_to_harvest(growth_pct)
            st.metric(
                label="Days to Harvest",
                value=f"~{days_to_harvest} days"
            )
        
        st.caption(f"📝 {stage_info['description']}")
        
        if growth_pct < 100:
            harvest_date = simulator.get_harvest_date(growth_pct)
            st.info(f"🗓️ **Predicted Harvest:** {harvest_date}")
        else:
            st.success("✅ **Ready for Harvest!**")
        
        st.divider()
        
        # What-if Scenarios
        st.markdown("##### 🔮 What-If Scenarios")
        st.caption("See how different conditions affect your plant")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            water_level = st.select_slider(
                "💧 Water",
                options=["low", "optimal", "high"],
                value=st.session_state.get("scenario_water", "optimal"),
                format_func=lambda x: SCENARIO_EFFECTS["water"][x]["icon"],
                key=f"{key_prefix}scenario_water_slider"
            )
            st.session_state.scenario_water = water_level
            simulator.scenarios["water"] = water_level
        
        with col2:
            sun_level = st.select_slider(
                "☀️ Sunlight",
                options=["low", "optimal", "high"],
                value=st.session_state.get("scenario_sunlight", "optimal"),
                format_func=lambda x: SCENARIO_EFFECTS["sunlight"][x]["icon"],
                key=f"{key_prefix}scenario_sunlight_slider"
            )
            st.session_state.scenario_sunlight = sun_level
            simulator.scenarios["sunlight"] = sun_level
        
        with col3:
            nutrient_level = st.select_slider(
                "🌱 Nutrients",
                options=["low", "optimal", "high"],
                value=st.session_state.get("scenario_nutrients", "optimal"),
                format_func=lambda x: SCENARIO_EFFECTS["nutrients"][x]["icon"],
                key=f"{key_prefix}scenario_nutrients_slider"
            )
            st.session_state.scenario_nutrients = nutrient_level
            simulator.scenarios["nutrients"] = nutrient_level
        
        # Show active effects
        modified_structure = simulator.get_modified_structure(growth_pct)
        effects = modified_structure.get("scenario_effects", {}).get("active_effects", [])
        
        if effects:
            st.warning(f"**Active Effects:** {', '.join(effects)}")
        else:
            st.success("🌿 All conditions optimal!")
        
        # Growth impact summary
        growth_mod = modified_structure.get("scenario_effects", {}).get("growth_modifier", 1.0)
        health_impact = modified_structure.get("scenario_effects", {}).get("health_impact", 0)
        
        if growth_mod < 1.0 or health_impact < 0:
            impact_col1, impact_col2 = st.columns(2)
            with impact_col1:
                st.metric(
                    "Growth Rate",
                    f"{int(growth_mod * 100)}%",
                    delta=f"{int((growth_mod - 1) * 100)}%"
                )
            with impact_col2:
                st.metric(
                    "Health Impact",
                    f"{int((1 + health_impact) * 100)}%",
                    delta=f"{int(health_impact * 100)}%"
                )
    
    return modified_structure


def get_growth_stage_timeline(plant_name: str) -> list:
    """Get timeline of growth stages for a plant."""
    # Find plant data
    plant_data = PLANT_GROWTH_DATA.get("default")
    for key in PLANT_GROWTH_DATA:
        if key in plant_name.lower():
            plant_data = PLANT_GROWTH_DATA[key]
            break
    
    total_days = plant_data["days_to_harvest"]
    stages = plant_data["stages"]
    
    timeline = []
    days_per_stage = total_days / len(stages)
    
    for i, stage in enumerate(stages):
        stage_info = GROWTH_STAGES[stage]
        timeline.append({
            "stage": stage,
            "name": stage_info["name"],
            "icon": stage_info["icon"],
            "start_day": int(i * days_per_stage),
            "end_day": int((i + 1) * days_per_stage),
            "description": stage_info["description"]
        })
    
    return timeline


def render_growth_timeline(plant_name: str):
    """Render a visual growth timeline."""
    timeline = get_growth_stage_timeline(plant_name)
    
    st.markdown("#### 📅 Growth Timeline")
    
    # Create timeline display
    cols = st.columns(len(timeline))
    for i, (col, stage) in enumerate(zip(cols, timeline)):
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:10px;background:linear-gradient(180deg,#E8F5E9,#C8E6C9);border-radius:10px;">
                <div style="font-size:24px;">{stage['icon']}</div>
                <div style="font-size:11px;font-weight:600;">{stage['name']}</div>
                <div style="font-size:10px;color:#666;">Day {stage['start_day']}-{stage['end_day']}</div>
            </div>
            """, unsafe_allow_html=True)


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def integrate_growth_simulation(plant_structure: dict, key_prefix: str = "") -> dict:
    """
    Main integration function - call this from the digital twin page.
    Returns modified structure with growth simulation applied.
    
    Usage in view_digital_twin.py:
        from components.growth_simulator import integrate_growth_simulation
        
        modified_structure = integrate_growth_simulation(plant_structure, key_prefix="single_")
        render_3d_simulation(texture_data, modified_structure)
    
    Args:
        plant_structure: The plant structure dict
        key_prefix: Unique prefix for widget keys (e.g., "single_", "multi_", "track_")
    """
    return render_growth_controls(plant_structure, key_prefix)
