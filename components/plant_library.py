"""
Plant Library Configuration - Modular, Data-Driven Plant Definitions
This file contains all plant type configurations for the 3D Digital Twin.
Easy to add new plants by adding entries to the PLANT_LIBRARY dictionary.
"""

# ============================================================================
# PLANT LIBRARY - Organized by Category
# ============================================================================

PLANT_LIBRARY = {
    # === PHILIPPINE STAPLE CROPS ===
    "rice": {
        "aliases": ["palay", "bigas", "rice plant", "oryza sativa"],
        "category": "grain",
        "builder": "buildGrainPlant",
        "characteristics": {
            "stem_type": "culm",
            "stem_count": 8,
            "stem_height": 1.0,
            "stem_color": "#6B8E23",
            "leaf_type": "grass_blade",
            "leaf_color": "#228B22",
            "has_grain_head": True,
            "grain_type": "panicle",
            "grain_color": "#DAA520",
            "grain_count": 12,
            "growth_habit": "tillering"
        }
    },
    "corn": {
        "aliases": ["maize", "mais"],
        "category": "grain",
        "builder": "buildGrainPlant",
        "characteristics": {
            "stem_type": "stalk",
            "stem_count": 1,
            "stem_height": 1.8,
            "stem_color": "#8BC34A",
            "stem_diameter": 0.05,
            "leaf_type": "corn_blade",
            "leaf_color": "#228B22",
            "leaf_count": 8,
            "has_cob": True,
            "cob_color": "#FFD700",
            "has_tassel": True,
            "tassel_color": "#D2691E"
        }
    },
    
    # === FRUIT TREES ===
    "mango": {
        "aliases": ["mangga", "mangifera indica"],
        "category": "fruit_tree",
        "builder": "buildFruitTree",
        "characteristics": {
            "trunk_height": 0.8,
            "trunk_diameter": 0.08,
            "trunk_color": "#4A3728",
            "canopy_type": "rounded",
            "canopy_radius": 0.6,
            "leaf_type": "lanceolate",
            "leaf_color": "#1B5E20",
            "leaf_count": 40,
            "fruit_shape": "kidney",
            "fruit_color": "#FFC107",
            "fruit_size": 0.1,
            "fruit_count": 5
        }
    },
    "banana": {
        "aliases": ["saging", "musa"],
        "category": "pseudostem",
        "builder": "buildBananaPlant",
        "characteristics": {
            "trunk_type": "pseudostem",
            "trunk_height": 1.2,
            "trunk_diameter": 0.15,
            "trunk_color": "#7CB342",
            "leaf_type": "banana_leaf",
            "leaf_color": "#2E7D32",
            "leaf_count": 8,
            "leaf_length": 0.8,
            "leaf_width": 0.2,
            "has_bunch": True,
            "bunch_color": "#FFEB3B",
            "fruit_count": 12
        }
    },
    "coconut": {
        "aliases": ["niyog", "cocos nucifera", "buko"],
        "category": "palm",
        "builder": "buildPalmTree",
        "characteristics": {
            "trunk_type": "palm",
            "trunk_height": 1.5,
            "trunk_diameter": 0.12,
            "trunk_color": "#8B7355",
            "trunk_rings": True,
            "leaf_type": "pinnate",
            "leaf_color": "#228B22",
            "frond_count": 12,
            "frond_length": 0.7,
            "has_coconuts": True,
            "coconut_color": "#8B4513",
            "coconut_count": 4
        }
    },
    "papaya": {
        "aliases": ["papaw", "carica papaya", "papaya tree"],
        "category": "tropical_tree",
        "builder": "buildPapayaTree",
        "characteristics": {
            "trunk_type": "single",
            "trunk_height": 1.2,
            "trunk_diameter": 0.1,
            "trunk_color": "#9E9D24",
            "leaf_type": "palmate",
            "leaf_color": "#388E3C",
            "leaf_count": 12,
            "leaf_size": 0.35,
            "fruit_shape": "oval",
            "fruit_color": "#FF9800",
            "fruit_size": 0.12,
            "fruit_count": 6
        }
    },
    "pineapple": {
        "aliases": ["pinya", "ananas comosus"],
        "category": "bromeliad",
        "builder": "buildPineapplePlant",
        "characteristics": {
            "rosette_diameter": 0.5,
            "leaf_type": "sword",
            "leaf_color": "#2E7D32",
            "leaf_count": 25,
            "leaf_length": 0.4,
            "has_fruit": True,
            "fruit_color": "#FFC107",
            "fruit_size": 0.15,
            "crown_color": "#388E3C"
        }
    },
    
    # === CASH CROPS ===
    "coffee": {
        "aliases": ["kape", "coffea"],
        "category": "shrub",
        "builder": "buildCoffeePlant",
        "characteristics": {
            "trunk_height": 0.8,
            "trunk_diameter": 0.03,
            "trunk_color": "#5D4037",
            "branching_style": "opposite",
            "branch_count": 6,
            "leaf_type": "elliptical",
            "leaf_color": "#1B5E20",
            "leaf_count": 24,
            "berry_color": "#B71C1C",
            "berry_count": 15,
            "berry_size": 0.015
        }
    },
    "cacao": {
        "aliases": ["kakaw", "theobroma cacao", "cocoa"],
        "category": "tree",
        "builder": "buildCacaoTree",
        "characteristics": {
            "trunk_height": 0.9,
            "trunk_diameter": 0.06,
            "trunk_color": "#4E342E",
            "branching_style": "jorquette",
            "leaf_type": "large_elliptical",
            "leaf_color": "#2E7D32",
            "leaf_count": 20,
            "pod_color": "#FF6F00",
            "pod_count": 4,
            "pod_size": 0.12
        }
    },
    
    # === ROOT CROPS ===
    "cassava": {
        "aliases": ["kamoteng kahoy", "balinghoy", "manihot esculenta"],
        "category": "root_crop",
        "builder": "buildCassavaPlant",
        "characteristics": {
            "stem_height": 1.0,
            "stem_diameter": 0.03,
            "stem_color": "#795548",
            "stem_count": 3,
            "leaf_type": "palmate",
            "leaf_color": "#388E3C",
            "leaf_count": 18,
            "lobes_per_leaf": 7,
            "root_visible": True,
            "root_color": "#D7CCC8"
        }
    },
    "gabi": {
        "aliases": ["taro", "colocasia esculenta"],
        "category": "root_crop",
        "builder": "buildTaroPlant",
        "characteristics": {
            "corm_visible": True,
            "corm_color": "#8D6E63",
            "leaf_type": "elephant_ear",
            "leaf_color": "#1B5E20",
            "leaf_count": 6,
            "leaf_size": 0.35,
            "petiole_length": 0.4,
            "petiole_color": "#7CB342"
        }
    },
    "peanut": {
        "aliases": ["mani", "arachis hypogaea"],
        "category": "legume",
        "builder": "buildPeanutPlant",
        "characteristics": {
            "stem_height": 0.35,
            "stem_color": "#689F38",
            "leaf_type": "compound",
            "leaf_color": "#4CAF50",
            "leaflet_count": 4,
            "flower_color": "#FFEB3B",
            "pods_underground": True,
            "pod_color": "#D7CCC8"
        }
    },
    
    # === VEGETABLES ===
    "sitaw": {
        "aliases": ["string beans", "yard-long beans", "vigna unguiculata"],
        "category": "vine",
        "builder": "buildBeanVine",
        "characteristics": {
            "vine_length": 0.8,
            "vine_color": "#558B2F",
            "leaf_type": "trifoliate",
            "leaf_color": "#43A047",
            "bean_color": "#8BC34A",
            "bean_length": 0.25,
            "bean_count": 5
        }
    },
    "patola": {
        "aliases": ["luffa", "sponge gourd", "luffa aegyptiaca"],
        "category": "vine",
        "builder": "buildGourdVine",
        "characteristics": {
            "vine_length": 1.0,
            "vine_color": "#558B2F",
            "leaf_type": "lobed",
            "leaf_color": "#66BB6A",
            "fruit_shape": "cylindrical",
            "fruit_color": "#8BC34A",
            "fruit_length": 0.3,
            "fruit_count": 3
        }
    },
    "upo": {
        "aliases": ["bottle gourd", "calabash", "lagenaria siceraria"],
        "category": "vine",
        "builder": "buildGourdVine",
        "characteristics": {
            "vine_length": 1.2,
            "vine_color": "#558B2F",
            "leaf_type": "rounded",
            "leaf_color": "#81C784",
            "fruit_shape": "bottle",
            "fruit_color": "#C5E1A5",
            "fruit_length": 0.35,
            "fruit_count": 2
        }
    },
    "ampalaya": {
        "aliases": ["bitter gourd", "bitter melon", "momordica charantia"],
        "category": "vine",
        "builder": "buildGourdVine",
        "characteristics": {
            "vine_length": 0.9,
            "vine_color": "#558B2F",
            "leaf_type": "palmate_lobed",
            "leaf_color": "#4CAF50",
            "fruit_shape": "warty_spindle",
            "fruit_color": "#689F38",
            "fruit_length": 0.2,
            "fruit_count": 4
        }
    },
    "kalabasa": {
        "aliases": ["squash", "pumpkin", "cucurbita"],
        "category": "vine",
        "builder": "buildSquashVine",
        "characteristics": {
            "vine_length": 1.5,
            "vine_color": "#558B2F",
            "leaf_type": "large_lobed",
            "leaf_color": "#43A047",
            "leaf_size": 0.25,
            "fruit_shape": "round",
            "fruit_color": "#FF9800",
            "fruit_size": 0.2,
            "fruit_count": 2
        }
    },
    
    # === LEAFY VEGETABLES ===
    "pechay": {
        "aliases": ["bok choy", "pak choi", "brassica rapa"],
        "category": "brassica",
        "builder": "buildBrassicaPlant",
        "characteristics": {
            "head_type": "loose",
            "leaf_color": "#4CAF50",
            "leaf_count": 10,
            "stem_color": "#FAFAFA",
            "stem_thick": True
        }
    },
    "kangkong": {
        "aliases": ["water spinach", "ipomoea aquatica"],
        "category": "vine",
        "builder": "buildVinePlant",
        "characteristics": {
            "vine_length": 0.6,
            "vine_color": "#43A047",
            "leaf_type": "arrow",
            "leaf_color": "#388E3C",
            "hollow_stem": True
        }
    },
    "mustasa": {
        "aliases": ["mustard greens", "brassica juncea"],
        "category": "brassica",
        "builder": "buildBrassicaPlant",
        "characteristics": {
            "head_type": "loose",
            "leaf_color": "#7CB342",
            "leaf_count": 12,
            "leaf_shape": "wavy"
        }
    }
}

# ============================================================================
# DISEASE PATTERNS - For Disease Visualization
# ============================================================================

DISEASE_PATTERNS = {
    "leaf_spot": {
        "pattern_type": "spots",
        "colors": ["#8B4513", "#654321", "#3E2723"],
        "spot_size_range": [0.02, 0.08],
        "density": 0.3,
        "spread_from": "random",
        "animation": "expand"
    },
    "blight": {
        "pattern_type": "patches",
        "colors": ["#3E2723", "#212121", "#5D4037"],
        "spread_from": "edges",
        "coverage": 0.4,
        "animation": "creep"
    },
    "powdery_mildew": {
        "pattern_type": "coating",
        "colors": ["#E0E0E0", "#BDBDBD", "#F5F5F5"],
        "opacity": 0.6,
        "spread_from": "center",
        "animation": "fade_in"
    },
    "rust": {
        "pattern_type": "pustules",
        "colors": ["#FF6F00", "#E65100", "#BF360C"],
        "spread_from": "underside",
        "animation": "appear"
    },
    "mosaic_virus": {
        "pattern_type": "discoloration",
        "colors": ["#FFEB3B", "#C0CA33", "#CDDC39"],
        "pattern": "mottled",
        "animation": "shift"
    },
    "wilt": {
        "pattern_type": "deformation",
        "effect": "droop",
        "color_shift": "#8D6E63",
        "animation": "collapse"
    },
    "rot": {
        "pattern_type": "decay",
        "colors": ["#3E2723", "#1B1B1B", "#5D4037"],
        "texture": "soft",
        "spread_from": "base",
        "animation": "dissolve"
    },
    "yellowing": {
        "pattern_type": "color_change",
        "colors": ["#FDD835", "#FBC02D", "#F9A825"],
        "spread_from": "tips",
        "animation": "gradient"
    },
    "necrosis": {
        "pattern_type": "dead_tissue",
        "colors": ["#795548", "#5D4037", "#3E2723"],
        "spread_from": "edges",
        "animation": "spread"
    }
}

# ============================================================================
# GROWTH STAGES - For Growth Simulation
# ============================================================================

GROWTH_STAGES = {
    "seed": {
        "scale": 0.0,
        "visibility": {"stem": False, "leaves": False, "fruit": False},
        "description": "Germinating seed"
    },
    "seedling": {
        "scale": 0.15,
        "visibility": {"stem": True, "leaves": True, "fruit": False},
        "leaf_count_factor": 0.2,
        "description": "Young seedling with first leaves"
    },
    "vegetative": {
        "scale": 0.5,
        "visibility": {"stem": True, "leaves": True, "fruit": False},
        "leaf_count_factor": 0.6,
        "description": "Active leaf and stem growth"
    },
    "flowering": {
        "scale": 0.75,
        "visibility": {"stem": True, "leaves": True, "flowers": True, "fruit": False},
        "leaf_count_factor": 0.9,
        "description": "Producing flowers"
    },
    "fruiting": {
        "scale": 0.9,
        "visibility": {"stem": True, "leaves": True, "flowers": False, "fruit": True},
        "fruit_count_factor": 0.5,
        "description": "Fruits developing"
    },
    "mature": {
        "scale": 1.0,
        "visibility": {"stem": True, "leaves": True, "fruit": True},
        "fruit_count_factor": 1.0,
        "description": "Ready for harvest"
    },
    "senescence": {
        "scale": 0.95,
        "visibility": {"stem": True, "leaves": True, "fruit": True},
        "color_shift": "#8D6E63",
        "description": "Post-harvest decline"
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_plant_config(plant_name: str) -> dict:
    """
    Get plant configuration by name or alias.
    Returns the matching plant config or None.
    """
    plant_name_lower = plant_name.lower().strip()
    
    # Direct match
    if plant_name_lower in PLANT_LIBRARY:
        return PLANT_LIBRARY[plant_name_lower]
    
    # Search aliases
    for key, config in PLANT_LIBRARY.items():
        aliases = config.get("aliases", [])
        for alias in aliases:
            if alias.lower() in plant_name_lower or plant_name_lower in alias.lower():
                return config
    
    return None


def get_builder_for_plant(plant_name: str) -> str:
    """
    Get the appropriate 3D builder function name for a plant.
    Returns default builder if plant not found.
    """
    config = get_plant_config(plant_name)
    if config:
        return config.get("builder", "buildLeafyPlant")
    return "buildLeafyPlant"


def get_disease_pattern(disease_name: str) -> dict:
    """
    Get disease visualization pattern by name.
    Matches partial names for flexibility.
    """
    disease_lower = disease_name.lower()
    
    for key, pattern in DISEASE_PATTERNS.items():
        if key in disease_lower or disease_lower in key:
            return pattern
    
    # Map common disease terms to patterns
    if any(term in disease_lower for term in ["spot", "anthracnose"]):
        return DISEASE_PATTERNS["leaf_spot"]
    if any(term in disease_lower for term in ["blight", "burn"]):
        return DISEASE_PATTERNS["blight"]
    if any(term in disease_lower for term in ["mildew", "powder"]):
        return DISEASE_PATTERNS["powdery_mildew"]
    if any(term in disease_lower for term in ["rust"]):
        return DISEASE_PATTERNS["rust"]
    if any(term in disease_lower for term in ["virus", "mosaic"]):
        return DISEASE_PATTERNS["mosaic_virus"]
    if any(term in disease_lower for term in ["wilt", "droop"]):
        return DISEASE_PATTERNS["wilt"]
    if any(term in disease_lower for term in ["rot", "decay"]):
        return DISEASE_PATTERNS["rot"]
    if any(term in disease_lower for term in ["yellow", "chlorosis", "deficiency"]):
        return DISEASE_PATTERNS["yellowing"]
    
    # Default pattern
    return DISEASE_PATTERNS["leaf_spot"]


def get_growth_stage(stage_name: str) -> dict:
    """Get growth stage configuration."""
    return GROWTH_STAGES.get(stage_name.lower(), GROWTH_STAGES["mature"])


def list_all_plants() -> list:
    """Return list of all plant names in library."""
    return list(PLANT_LIBRARY.keys())


def list_plants_by_category(category: str) -> list:
    """Return plants filtered by category."""
    return [
        name for name, config in PLANT_LIBRARY.items() 
        if config.get("category") == category
    ]


def get_categories() -> list:
    """Return all unique plant categories."""
    categories = set()
    for config in PLANT_LIBRARY.values():
        categories.add(config.get("category", "other"))
    return sorted(list(categories))
