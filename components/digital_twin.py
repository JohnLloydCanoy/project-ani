import streamlit as st
import streamlit.components.v1 as components
from typing import Optional
import json


def render_3d_simulation(
    texture_data: Optional[str] = None, 
    plant_structure: Optional[dict] = None,
    height: int = 550
) -> None:
    """
    Renders a botanically accurate 3D plant simulation using Three.js.
    Supports specific plant types: cauliflower, cabbage, broccoli, lettuce, etc.
    Uses Gemini's analysis to generate realistic 3D geometry.
    """
    
    if plant_structure is None:
        plant_structure = get_default_structure()
    
    plant_json = json.dumps(plant_structure)
    
    three_js_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ overflow: hidden; background: transparent; }}
            #canvas-container {{
                width: 100%;
                height: {height}px;
                background: linear-gradient(180deg, #87CEEB 0%, #B0E0E6 30%, #98D8C8 70%, #7CB342 100%);
                border-radius: 15px;
                overflow: hidden;
                position: relative;
            }}
            canvas {{ display: block; border-radius: 15px; }}
            #loading {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #2E7D32;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                text-align: center;
                z-index: 100;
                background: rgba(255,255,255,0.95);
                padding: 25px 35px;
                border-radius: 15px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            }}
            .spinner {{
                width: 45px;
                height: 45px;
                border: 4px solid rgba(76, 175, 80, 0.3);
                border-top: 4px solid #4CAF50;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
                margin: 0 auto 12px;
            }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            #info {{
                position: absolute;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                color: #333;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                background: rgba(255,255,255,0.85);
                padding: 6px 16px;
                border-radius: 15px;
            }}
            #plant-label {{
                position: absolute;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                color: #2E7D32;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: 600;
                background: rgba(255,255,255,0.9);
                padding: 8px 20px;
                border-radius: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="loading">
                <div class="spinner"></div>
                🌱 Building Botanical Model...
            </div>
            <div id="plant-label"></div>
            <div id="info">🖱️ Drag to rotate • Scroll to zoom</div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        
        <script>
            const plantData = {plant_json};
            
            // Helper function
            function get(obj, path, defaultVal) {{
                const keys = path.split('.');
                let result = obj;
                for (const key of keys) {{
                    result = result?.[key];
                    if (result === undefined) return defaultVal;
                }}
                return result;
            }}
            
            // Scene setup
            const container = document.getElementById('canvas-container');
            const loading = document.getElementById('loading');
            const plantLabel = document.getElementById('plant-label');
            
            // Show plant name
            const plantName = get(plantData, 'identified_plant.common_name', 'Plant');
            plantLabel.textContent = '🌿 ' + plantName;
            
            const scene = new THREE.Scene();
            
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / {height}, 0.1, 1000);
            camera.position.set(2.5, 2.5, 3.5);
            camera.lookAt(0, 0.8, 0);
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(container.clientWidth, {height});
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.1;
            container.appendChild(renderer.domElement);
            
            // Lighting
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            scene.add(ambientLight);
            
            const sunLight = new THREE.DirectionalLight(0xfffaf0, 1.0);
            sunLight.position.set(4, 8, 4);
            sunLight.castShadow = true;
            sunLight.shadow.mapSize.width = 2048;
            sunLight.shadow.mapSize.height = 2048;
            scene.add(sunLight);
            
            const fillLight = new THREE.DirectionalLight(0x87CEEB, 0.25);
            fillLight.position.set(-4, 3, -2);
            scene.add(fillLight);
            
            const backLight = new THREE.DirectionalLight(0xffffff, 0.15);
            backLight.position.set(0, 2, -4);
            scene.add(backLight);
            
            const plantGroup = new THREE.Group();
            scene.add(plantGroup);
            
            // ===== SPECIALIZED PLANT BUILDERS =====
            
            // CAULIFLOWER / BROCCOLI / CABBAGE Builder
            function buildBrassicaPlant(headType) {{
                const group = new THREE.Group();
                const leafSys = get(plantData, 'leaf_system', {{}});
                const arch = get(plantData, 'plant_architecture', {{}});
                
                const leafCount = get(leafSys, 'total_count', 12);
                const leafLayers = get(leafSys, 'leaf_layers', 3);
                const primaryColor = get(leafSys, 'primary_color_hex', '#228B22');
                const veinColor = get(leafSys, 'vein_color_hex', '#FFFFFF');
                const leafOrientation = get(leafSys, 'orientation', 'cupping');
                const waviness = get(leafSys, 'waviness', 0.5);
                const headColor = get(arch, 'head_color_hex', '#F5F5DC');
                const headSizeRatio = get(arch, 'head_size_ratio', 0.3);
                
                // Central head (cauliflower/broccoli/cabbage)
                if (headType === 'cauliflower') {{
                    const headGeometry = new THREE.SphereGeometry(0.35 * (1 + headSizeRatio), 32, 32);
                    // Make it bumpy like cauliflower
                    const positions = headGeometry.attributes.position.array;
                    for (let i = 0; i < positions.length; i += 3) {{
                        const noise = (Math.random() - 0.5) * 0.08;
                        positions[i] += noise;
                        positions[i + 1] += noise * 0.5;
                        positions[i + 2] += noise;
                    }}
                    headGeometry.computeVertexNormals();
                    
                    const headMaterial = new THREE.MeshStandardMaterial({{
                        color: new THREE.Color(headColor),
                        roughness: 0.9,
                        metalness: 0
                    }});
                    const head = new THREE.Mesh(headGeometry, headMaterial);
                    head.position.y = 0.9;
                    head.castShadow = true;
                    group.add(head);
                    
                }} else if (headType === 'broccoli') {{
                    // Broccoli has a tree-like floret structure
                    const headGroup = new THREE.Group();
                    for (let i = 0; i < 12; i++) {{
                        const floretGeometry = new THREE.SphereGeometry(0.08 + Math.random() * 0.05, 16, 16);
                        const floretMaterial = new THREE.MeshStandardMaterial({{
                            color: new THREE.Color(headColor),
                            roughness: 0.85
                        }});
                        const floret = new THREE.Mesh(floretGeometry, floretMaterial);
                        const angle = (i / 12) * Math.PI * 2;
                        const radius = 0.15 + Math.random() * 0.1;
                        floret.position.set(
                            Math.cos(angle) * radius,
                            0.08 + Math.random() * 0.1,
                            Math.sin(angle) * radius
                        );
                        headGroup.add(floret);
                    }}
                    // Central floret
                    const centralFloret = new THREE.Mesh(
                        new THREE.SphereGeometry(0.12, 16, 16),
                        new THREE.MeshStandardMaterial({{ color: new THREE.Color(headColor), roughness: 0.85 }})
                    );
                    centralFloret.position.y = 0.12;
                    headGroup.add(centralFloret);
                    headGroup.position.y = 0.85;
                    group.add(headGroup);
                    
                }} else if (headType === 'cabbage') {{
                    // Cabbage has layered leaves forming a ball
                    for (let layer = 0; layer < 4; layer++) {{
                        const layerRadius = 0.35 - layer * 0.06;
                        const layerLeaves = 6 - layer;
                        for (let i = 0; i < layerLeaves; i++) {{
                            const angle = (i / layerLeaves) * Math.PI * 2 + layer * 0.3;
                            const leafGeom = createCurvingLeaf(0.2, 0.25, 0.7 + layer * 0.1);
                            const leafMat = new THREE.MeshStandardMaterial({{
                                color: new THREE.Color(layer < 2 ? '#90EE90' : primaryColor),
                                side: THREE.DoubleSide,
                                roughness: 0.6
                            }});
                            const leaf = new THREE.Mesh(leafGeom, leafMat);
                            leaf.position.set(
                                Math.cos(angle) * layerRadius * 0.3,
                                0.9 + layer * 0.05,
                                Math.sin(angle) * layerRadius * 0.3
                            );
                            leaf.rotation.x = -0.3 - layer * 0.2;
                            leaf.rotation.y = angle;
                            leaf.scale.set(1 - layer * 0.15, 1 - layer * 0.15, 1);
                            group.add(leaf);
                        }}
                    }}
                }}
                
                // Large outer leaves (characteristic of brassicas)
                for (let layer = 0; layer < leafLayers; layer++) {{
                    const leavesInLayer = Math.floor(leafCount / leafLayers);
                    const layerAngleOffset = layer * (Math.PI / leavesInLayer);
                    
                    for (let i = 0; i < leavesInLayer; i++) {{
                        const angle = (i / leavesInLayer) * Math.PI * 2 + layerAngleOffset;
                        
                        // Create large wavy brassica leaf
                        const leafWidth = 0.35 - layer * 0.05;
                        const leafLength = 0.55 - layer * 0.08;
                        const leafGeometry = createBrassicaLeaf(leafWidth, leafLength, waviness);
                        
                        // Gradient from edge to center
                        const colorMix = layer / leafLayers;
                        const leafColor = new THREE.Color(primaryColor);
                        
                        const leafMaterial = new THREE.MeshStandardMaterial({{
                            color: leafColor,
                            side: THREE.DoubleSide,
                            roughness: 0.5,
                            metalness: 0.02
                        }});
                        
                        const leaf = new THREE.Mesh(leafGeometry, leafMaterial);
                        
                        // Position: outer leaves spread out, inner cup inward
                        const radius = 0.15 + layer * 0.12;
                        leaf.position.x = Math.cos(angle) * radius;
                        leaf.position.z = Math.sin(angle) * radius;
                        leaf.position.y = 0.4 + layer * 0.15;
                        
                        // Rotation: cupping toward center
                        const tiltAngle = leafOrientation === 'cupping' ? 
                            (-0.2 - layer * 0.25) : (-0.5 - layer * 0.15);
                        leaf.rotation.x = tiltAngle;
                        leaf.rotation.y = angle + Math.PI / 2;
                        leaf.rotation.z = (Math.random() - 0.5) * 0.15;
                        
                        leaf.castShadow = true;
                        leaf.receiveShadow = true;
                        group.add(leaf);
                        
                        // Add prominent white midrib
                        const midribGeometry = new THREE.BoxGeometry(0.03, leafLength * 0.8, 0.015);
                        const midribMaterial = new THREE.MeshStandardMaterial({{
                            color: new THREE.Color(veinColor),
                            roughness: 0.4
                        }});
                        const midrib = new THREE.Mesh(midribGeometry, midribMaterial);
                        midrib.position.copy(leaf.position);
                        midrib.position.y += 0.02;
                        midrib.rotation.copy(leaf.rotation);
                        group.add(midrib);
                    }}
                }}
                
                return group;
            }}
            
            // Create brassica-style large wavy leaf
            function createBrassicaLeaf(width, length, waviness) {{
                const shape = new THREE.Shape();
                const segments = 20;
                
                shape.moveTo(0, 0);
                
                // Right side with waves
                for (let i = 0; i <= segments; i++) {{
                    const t = i / segments;
                    const wave = Math.sin(t * Math.PI * 4) * waviness * 0.08;
                    const baseWidth = Math.sin(t * Math.PI) * width * (1 - t * 0.3);
                    shape.lineTo(baseWidth + wave, length * t);
                }}
                
                // Left side with waves
                for (let i = segments; i >= 0; i--) {{
                    const t = i / segments;
                    const wave = Math.sin(t * Math.PI * 4 + 0.5) * waviness * 0.08;
                    const baseWidth = Math.sin(t * Math.PI) * width * (1 - t * 0.3);
                    shape.lineTo(-(baseWidth + wave), length * t);
                }}
                
                const geometry = new THREE.ShapeGeometry(shape, 24);
                
                // Add 3D curvature
                const positions = geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {{
                    const x = positions[i];
                    const y = positions[i + 1];
                    
                    // Cup shape - edges curve up
                    positions[i + 2] = Math.pow(Math.abs(x) / width, 1.5) * 0.15;
                    // Lengthwise curve
                    positions[i + 2] += Math.pow(y / length, 2) * 0.1;
                    // Wavy surface
                    positions[i + 2] += Math.sin(y * 8) * 0.02 * waviness;
                }}
                
                geometry.computeVertexNormals();
                return geometry;
            }}
            
            // Create curving leaf for cabbage center
            function createCurvingLeaf(width, length, curl) {{
                const shape = new THREE.Shape();
                shape.moveTo(0, 0);
                shape.bezierCurveTo(width, length * 0.3, width * 0.8, length * 0.7, 0, length);
                shape.bezierCurveTo(-width * 0.8, length * 0.7, -width, length * 0.3, 0, 0);
                
                const geometry = new THREE.ShapeGeometry(shape, 16);
                const positions = geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {{
                    const y = positions[i + 1];
                    positions[i + 2] = Math.pow(y / length, 2) * curl * 0.3;
                }}
                geometry.computeVertexNormals();
                return geometry;
            }}
            
            // FRUITING PLANT Builder (tomato, pepper, eggplant, etc.)
            function buildFruitingPlant() {{
                const group = new THREE.Group();
                const leafSys = get(plantData, 'leaf_system', {{}});
                const arch = get(plantData, 'plant_architecture', {{}});
                const stemSys = get(plantData, 'stem_system', {{}});
                
                const primaryColor = get(leafSys, 'primary_color_hex', '#228B22');
                const stemColor = get(stemSys, 'color_hex', '#2E8B57');
                const fruitType = get(arch, 'fruit_type', 'tomato');
                const fruitColor = get(arch, 'fruit_color_hex', '#FF6347');
                const fruitCount = get(arch, 'fruit_count', 5);
                const fruitSize = get(arch, 'fruit_size', 0.08);
                const plantHeight = get(arch, 'height_estimate', 1.2);
                
                // Main stem
                const stemGeometry = new THREE.CylinderGeometry(0.03, 0.04, plantHeight, 12);
                const stemMaterial = new THREE.MeshStandardMaterial({{
                    color: new THREE.Color(stemColor),
                    roughness: 0.8
                }});
                const mainStem = new THREE.Mesh(stemGeometry, stemMaterial);
                mainStem.position.y = 0.6 + plantHeight / 2;
                mainStem.castShadow = true;
                group.add(mainStem);
                
                // Branches with leaves and fruits
                const branchCount = 4 + Math.floor(Math.random() * 3);
                for (let b = 0; b < branchCount; b++) {{
                    const branchY = 0.7 + (b / branchCount) * plantHeight * 0.8;
                    const branchAngle = (b / branchCount) * Math.PI * 2 + Math.random() * 0.5;
                    const branchLength = 0.2 + Math.random() * 0.15;
                    
                    // Branch
                    const branchGeom = new THREE.CylinderGeometry(0.015, 0.02, branchLength, 8);
                    const branch = new THREE.Mesh(branchGeom, stemMaterial);
                    branch.position.set(
                        Math.cos(branchAngle) * branchLength / 2,
                        branchY,
                        Math.sin(branchAngle) * branchLength / 2
                    );
                    branch.rotation.z = Math.PI / 2 - 0.3;
                    branch.rotation.y = branchAngle;
                    group.add(branch);
                    
                    // Compound leaves (tomato-style)
                    for (let l = 0; l < 3; l++) {{
                        const leafGeom = createCompoundLeaf(0.12, 0.18);
                        const leafMat = new THREE.MeshStandardMaterial({{
                            color: new THREE.Color(primaryColor),
                            side: THREE.DoubleSide,
                            roughness: 0.6
                        }});
                        const leaf = new THREE.Mesh(leafGeom, leafMat);
                        leaf.position.set(
                            Math.cos(branchAngle) * (branchLength * 0.3 + l * 0.08),
                            branchY + 0.02 - l * 0.03,
                            Math.sin(branchAngle) * (branchLength * 0.3 + l * 0.08)
                        );
                        leaf.rotation.x = -0.3 + Math.random() * 0.3;
                        leaf.rotation.y = branchAngle + Math.random() * 0.5;
                        leaf.castShadow = true;
                        group.add(leaf);
                    }}
                }}
                
                // Fruits
                for (let f = 0; f < fruitCount; f++) {{
                    const fruitY = 0.8 + Math.random() * plantHeight * 0.6;
                    const fruitAngle = Math.random() * Math.PI * 2;
                    const fruitRadius = 0.1 + Math.random() * 0.1;
                    
                    let fruitGeom;
                    if (fruitType === 'tomato' || fruitType === 'cherry_tomato') {{
                        fruitGeom = new THREE.SphereGeometry(fruitSize * (0.8 + Math.random() * 0.4), 16, 16);
                    }} else if (fruitType === 'pepper' || fruitType === 'chili') {{
                        fruitGeom = new THREE.ConeGeometry(fruitSize * 0.5, fruitSize * 3, 12);
                    }} else if (fruitType === 'eggplant') {{
                        fruitGeom = new THREE.SphereGeometry(fruitSize, 16, 16);
                        fruitGeom.scale(0.6, 1.5, 0.6);
                    }} else {{
                        fruitGeom = new THREE.SphereGeometry(fruitSize, 16, 16);
                    }}
                    
                    const fruitMat = new THREE.MeshStandardMaterial({{
                        color: new THREE.Color(fruitColor),
                        roughness: 0.3,
                        metalness: 0.1
                    }});
                    const fruit = new THREE.Mesh(fruitGeom, fruitMat);
                    fruit.position.set(
                        Math.cos(fruitAngle) * fruitRadius,
                        fruitY,
                        Math.sin(fruitAngle) * fruitRadius
                    );
                    if (fruitType === 'pepper' || fruitType === 'chili') {{
                        fruit.rotation.x = Math.PI;
                    }}
                    fruit.castShadow = true;
                    group.add(fruit);
                    
                    // Small stem on fruit
                    const stemletGeom = new THREE.CylinderGeometry(0.005, 0.008, 0.03, 6);
                    const stemlet = new THREE.Mesh(stemletGeom, stemMaterial);
                    stemlet.position.set(fruit.position.x, fruit.position.y + fruitSize, fruit.position.z);
                    group.add(stemlet);
                }}
                
                return group;
            }}
            
            // Create compound leaf (for tomatoes, etc.)
            function createCompoundLeaf(width, length) {{
                const shape = new THREE.Shape();
                const leaflets = 5;
                
                shape.moveTo(0, 0);
                for (let i = 0; i < leaflets; i++) {{
                    const t = i / (leaflets - 1);
                    const y = t * length;
                    const leafletSize = Math.sin(t * Math.PI) * width * 0.4;
                    
                    // Right leaflet
                    shape.lineTo(leafletSize, y);
                    shape.lineTo(leafletSize * 0.3, y + length / leaflets * 0.5);
                }}
                shape.lineTo(0, length);
                for (let i = leaflets - 1; i >= 0; i--) {{
                    const t = i / (leaflets - 1);
                    const y = t * length;
                    const leafletSize = Math.sin(t * Math.PI) * width * 0.4;
                    
                    // Left leaflet
                    shape.lineTo(-leafletSize * 0.3, y + length / leaflets * 0.5);
                    shape.lineTo(-leafletSize, y);
                }}
                shape.lineTo(0, 0);
                
                const geometry = new THREE.ShapeGeometry(shape, 16);
                geometry.computeVertexNormals();
                return geometry;
            }}
            
            // GENERIC LEAFY PLANT Builder (lettuce, herbs, etc.)
            function buildLeafyPlant() {{
                const group = new THREE.Group();
                const leafSys = get(plantData, 'leaf_system', {{}});
                
                const leafCount = get(leafSys, 'total_count', 12);
                const leafShape = get(leafSys, 'shape', 'oval');
                const primaryColor = get(leafSys, 'primary_color_hex', '#4CAF50');
                const curl = get(leafSys, 'curl_amount', 0.3);
                const waviness = get(leafSys, 'waviness', 0.3);
                const orientation = get(leafSys, 'orientation', 'outward');
                const arrangement = get(leafSys, 'arrangement', 'rosette');
                
                for (let i = 0; i < leafCount; i++) {{
                    const layer = Math.floor(i / 5);
                    const indexInLayer = i % 5;
                    const angle = (indexInLayer / 5) * Math.PI * 2 + layer * 0.5;
                    
                    const leafGeometry = createLeafByShape(leafShape, 0.25, 0.4, waviness);
                    
                    const colorVariation = new THREE.Color(primaryColor);
                    colorVariation.offsetHSL(0, (Math.random() - 0.5) * 0.1, (Math.random() - 0.5) * 0.1);
                    
                    const leafMaterial = new THREE.MeshStandardMaterial({{
                        color: colorVariation,
                        side: THREE.DoubleSide,
                        roughness: 0.55,
                        metalness: 0.02
                    }});
                    
                    const leaf = new THREE.Mesh(leafGeometry, leafMaterial);
                    
                    // Position based on arrangement
                    const radius = 0.08 + layer * 0.08;
                    leaf.position.x = Math.cos(angle) * radius;
                    leaf.position.z = Math.sin(angle) * radius;
                    leaf.position.y = 0.6 + layer * 0.08;
                    
                    // Rotation based on orientation
                    let tilt = -0.4 - layer * 0.15;
                    if (orientation === 'upward') tilt = -0.2 - layer * 0.1;
                    if (orientation === 'drooping') tilt = 0.2 + layer * 0.1;
                    
                    leaf.rotation.x = tilt + (Math.random() - 0.5) * 0.2;
                    leaf.rotation.y = angle + Math.PI / 2;
                    leaf.rotation.z = (Math.random() - 0.5) * 0.15;
                    
                    const scale = 0.8 + Math.random() * 0.4;
                    leaf.scale.set(scale, scale, scale);
                    
                    leaf.castShadow = true;
                    group.add(leaf);
                }}
                
                return group;
            }}
            
            // Create leaf by shape type
            function createLeafByShape(shape, width, length, waviness) {{
                const leafShape = new THREE.Shape();
                
                if (shape === 'frilly' || shape === 'ruffled') {{
                    const segments = 24;
                    leafShape.moveTo(0, 0);
                    for (let i = 0; i <= segments; i++) {{
                        const t = i / segments;
                        const wave = Math.sin(t * Math.PI * 8) * 0.06 * waviness;
                        const baseWidth = Math.sin(t * Math.PI) * width;
                        leafShape.lineTo(baseWidth + wave, length * t);
                    }}
                    for (let i = segments; i >= 0; i--) {{
                        const t = i / segments;
                        const wave = Math.sin(t * Math.PI * 8 + 0.5) * 0.06 * waviness;
                        const baseWidth = Math.sin(t * Math.PI) * width;
                        leafShape.lineTo(-(baseWidth + wave), length * t);
                    }}
                }} else if (shape === 'lobed') {{
                    const lobes = 5;
                    leafShape.moveTo(0, 0);
                    for (let i = 0; i <= lobes * 2; i++) {{
                        const t = i / (lobes * 2);
                        const lobe = Math.sin(t * Math.PI * lobes) * 0.1;
                        const baseWidth = Math.sin(t * Math.PI) * width;
                        leafShape.lineTo(baseWidth + lobe, length * t);
                    }}
                    for (let i = lobes * 2; i >= 0; i--) {{
                        const t = i / (lobes * 2);
                        const lobe = Math.sin(t * Math.PI * lobes) * 0.1;
                        const baseWidth = Math.sin(t * Math.PI) * width;
                        leafShape.lineTo(-(baseWidth + lobe), length * t);
                    }}
                }} else if (shape === 'elongated' || shape === 'spatulate') {{
                    length *= 1.5;
                    width *= 0.6;
                    leafShape.moveTo(0, 0);
                    leafShape.bezierCurveTo(width * 0.3, length * 0.3, width, length * 0.7, 0, length);
                    leafShape.bezierCurveTo(-width, length * 0.7, -width * 0.3, length * 0.3, 0, 0);
                }} else if (shape === 'heart') {{
                    leafShape.moveTo(0, 0);
                    leafShape.bezierCurveTo(width * 1.2, length * 0.3, width * 0.8, length * 0.8, 0, length);
                    leafShape.bezierCurveTo(-width * 0.8, length * 0.8, -width * 1.2, length * 0.3, 0, 0);
                }} else {{
                    // Default oval
                    leafShape.moveTo(0, 0);
                    leafShape.bezierCurveTo(width * 0.7, length * 0.25, width * 0.6, length * 0.75, 0, length);
                    leafShape.bezierCurveTo(-width * 0.6, length * 0.75, -width * 0.7, length * 0.25, 0, 0);
                }}
                
                const geometry = new THREE.ShapeGeometry(leafShape, 24);
                
                // Add 3D curvature
                const positions = geometry.attributes.position.array;
                for (let i = 0; i < positions.length; i += 3) {{
                    const x = positions[i];
                    const y = positions[i + 1];
                    positions[i + 2] = Math.pow(y / length, 1.5) * 0.15;
                    positions[i + 2] += Math.pow(Math.abs(x) / width, 2) * 0.08;
                    positions[i + 2] += Math.sin(y * 10) * waviness * 0.02;
                }}
                
                geometry.computeVertexNormals();
                return geometry;
            }}
            
            // CONTAINER Builder
            function buildContainer() {{
                const containerData = get(plantData, 'container', {{}});
                const containerType = get(containerData, 'type', 'pot');
                
                if (containerType === 'none' || containerType === 'ground') {{
                    // Just soil mound
                    const soilGeometry = new THREE.CylinderGeometry(0.6, 0.7, 0.15, 32);
                    const soilData = get(plantData, 'soil_ground', {{}});
                    const soilMaterial = new THREE.MeshStandardMaterial({{
                        color: new THREE.Color(get(soilData, 'color_hex', '#3D2B1F')),
                        roughness: 1
                    }});
                    const soil = new THREE.Mesh(soilGeometry, soilMaterial);
                    soil.position.y = 0.08;
                    soil.receiveShadow = true;
                    return soil;
                }}
                
                const group = new THREE.Group();
                
                const shape = get(containerData, 'shape', 'round');
                const material = get(containerData, 'material', 'terracotta');
                const colorHex = get(containerData, 'color_hex', '#B5651D');
                const hasRim = get(containerData, 'has_rim', true);
                
                // Material properties
                let roughness = 0.8, metalness = 0;
                if (material === 'ceramic') roughness = 0.3;
                if (material === 'plastic') {{ roughness = 0.4; metalness = 0.1; }}
                if (material === 'metal') {{ roughness = 0.3; metalness = 0.7; }}
                if (material === 'wood') roughness = 0.9;
                
                const potMaterial = new THREE.MeshStandardMaterial({{
                    color: new THREE.Color(colorHex),
                    roughness: roughness,
                    metalness: metalness
                }});
                
                // Pot geometry
                let potGeometry;
                if (shape === 'square' || shape === 'rectangular') {{
                    potGeometry = new THREE.BoxGeometry(0.9, 0.6, 0.9);
                }} else if (shape === 'cylindrical') {{
                    potGeometry = new THREE.CylinderGeometry(0.45, 0.45, 0.6, 32);
                }} else {{
                    potGeometry = new THREE.CylinderGeometry(0.5, 0.35, 0.6, 32);
                }}
                
                const pot = new THREE.Mesh(potGeometry, potMaterial);
                pot.position.y = 0.3;
                pot.castShadow = true;
                pot.receiveShadow = true;
                group.add(pot);
                
                // Rim
                if (hasRim) {{
                    const rimGeometry = new THREE.TorusGeometry(0.52, 0.04, 12, 32);
                    const rim = new THREE.Mesh(rimGeometry, potMaterial);
                    rim.rotation.x = Math.PI / 2;
                    rim.position.y = 0.6;
                    group.add(rim);
                }}
                
                // Soil
                const soilData = get(plantData, 'soil_ground', {{}});
                if (get(soilData, 'visible', true)) {{
                    const soilGeometry = new THREE.CylinderGeometry(0.45, 0.45, 0.08, 32);
                    const soilMaterial = new THREE.MeshStandardMaterial({{
                        color: new THREE.Color(get(soilData, 'color_hex', '#3D2B1F')),
                        roughness: 1
                    }});
                    const soil = new THREE.Mesh(soilGeometry, soilMaterial);
                    soil.position.y = 0.56;
                    soil.receiveShadow = true;
                    group.add(soil);
                }}
                
                return group;
            }}
            
            // Ground
            const groundGeometry = new THREE.PlaneGeometry(10, 10);
            const groundMaterial = new THREE.MeshStandardMaterial({{
                color: 0x7CB342,
                roughness: 0.9
            }});
            const ground = new THREE.Mesh(groundGeometry, groundMaterial);
            ground.rotation.x = -Math.PI / 2;
            ground.position.y = -0.01;
            ground.receiveShadow = true;
            scene.add(ground);
            
            // ===== BUILD THE SCENE =====
            function buildScene() {{
                const headType = get(plantData, 'plant_architecture.head_type', 'none');
                const fruitType = get(plantData, 'plant_architecture.fruit_type', 'none');
                const plantFamily = get(plantData, 'identified_plant.plant_family', '');
                const plantName = get(plantData, 'identified_plant.common_name', '').toLowerCase();
                
                // Add container
                const container = buildContainer();
                if (container) plantGroup.add(container);
                
                // Build plant based on type
                let plant;
                
                // Check for fruiting plants (tomato, pepper, eggplant)
                if (fruitType !== 'none' || 
                    plantName.includes('tomato') || 
                    plantName.includes('pepper') || 
                    plantName.includes('chili') ||
                    plantName.includes('eggplant') ||
                    plantFamily === 'Solanaceae') {{
                    plant = buildFruitingPlant();
                }}
                // Check for brassicas (cauliflower, broccoli, cabbage)
                else if (headType === 'cauliflower' || headType === 'broccoli' || headType === 'cabbage' ||
                    plantFamily === 'Brassicaceae') {{
                    plant = buildBrassicaPlant(headType);
                }} 
                // Default to leafy plant
                else {{
                    plant = buildLeafyPlant();
                }}
                
                plantGroup.add(plant);
                loading.style.display = 'none';
            }}
            
            setTimeout(buildScene, 150);
            
            // Controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 1.5;
            controls.maxDistance = 8;
            controls.maxPolarAngle = Math.PI / 2 + 0.1;
            controls.target.set(0, 0.7, 0);
            controls.update();
            
            // Animation
            let time = 0;
            function animate() {{
                requestAnimationFrame(animate);
                time += 0.008;
                
                // Gentle movement
                plantGroup.children.forEach((child) => {{
                    if (child.type === 'Group') {{
                        child.children.forEach((leaf, i) => {{
                            if (leaf.geometry?.type === 'ShapeGeometry') {{
                                leaf.rotation.z += Math.sin(time + i * 0.3) * 0.0004;
                            }}
                        }});
                    }}
                }});
                
                controls.update();
                renderer.render(scene, camera);
            }}
            
            animate();
            
            window.addEventListener('resize', function() {{
                const width = container.clientWidth;
                camera.aspect = width / {height};
                camera.updateProjectionMatrix();
                renderer.setSize(width, {height});
            }});
        </script>
    </body>
    </html>
    """
    
    components.html(three_js_html, height=height + 20, scrolling=False)


def get_default_structure() -> dict:
    """Returns default structure for placeholder."""
    return {
        "identified_plant": {"common_name": "Plant", "plant_family": "Unknown"},
        "plant_architecture": {"head_type": "none", "has_central_head": False},
        "leaf_system": {
            "total_count": 12, "shape": "oval", "primary_color_hex": "#4CAF50",
            "waviness": 0.3, "curl_amount": 0.3, "orientation": "outward"
        },
        "container": {"type": "pot", "shape": "round", "material": "terracotta", "color_hex": "#B5651D"},
        "soil_ground": {"visible": True, "color_hex": "#3D2B1F"}
    }
