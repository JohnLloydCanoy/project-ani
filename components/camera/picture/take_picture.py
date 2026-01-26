import streamlit as st
import streamlit.components.v1 as components
import base64
from io import BytesIO


def open_picture_camera():

    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False
    

    if st.query_params.get("close_camera") == "true":
        st.session_state.camera_active = False
        st.query_params.clear() # Clean the URL
        st.rerun()

    if not st.session_state.camera_active:
        return False
    
    return True


def take_picture():
    camera_is_active = open_picture_camera()
    if not camera_is_active:
        return None

    camera_html = """
    <div id="camera-container">
        <video id="video" autoplay playsinline muted></video>
        <canvas id="canvas" style="display:none;"></canvas>
        
        <div id="flip-btn" class="ctrl-btn">⟲</div>
        <div id="capture-btn"></div>
        <div id="status">Starting camera...</div>
    </div>
    
    <style>
        #camera-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            z-index: 999999;
        }               
        
        #video {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .ctrl-btn {
            position: fixed;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            border: 3px solid white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            cursor: pointer;
            z-index: 1000001;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        
        #flip-btn {
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.6);
            color: white;
        }
        
        #capture-btn {
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 4px solid white;
            background: rgba(255, 255, 255, 0.3);
            cursor: pointer;
            z-index: 1000001;
            touch-action: manipulation;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #capture-btn::after {
            content: "";
            display: block;
            width: 60px;
            height: 60px;
            background: #dc3545;
            border-radius: 50%;
        }
        
        .ctrl-btn:active, #capture-btn:active {
            opacity: 0.7;
            transform: scale(0.95);
        }
        
        #capture-btn:active {
            transform: translateX(-50%) scale(0.95);
        }
        
        #status {
            position: fixed;
            bottom: 140px;
            left: 50%;
            transform: translateX(-50%);
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            background: rgba(0,0,0,0.6);
            padding: 10px 20px;
            border-radius: 25px;
            z-index: 1000001;
            white-space: nowrap;
        }
    </style>
    
    <script>
        let currentStream = null;
        let useFrontCamera = true; // Start with front/default camera for compatibility
        
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const status = document.getElementById('status');
        const flipBtn = document.getElementById('flip-btn');
        const captureBtn = document.getElementById('capture-btn');
        
        async function startCamera() {
            try {
                // Stop any existing stream
                if (currentStream) {
                    currentStream.getTracks().forEach(t => t.stop());
                    currentStream = null;
                    video.srcObject = null;
                }
                
                status.style.opacity = '1';
                status.textContent = useFrontCamera ? 'Starting front camera...' : 'Starting back camera...';
                
                // Try with facingMode first
                let constraints = {
                    video: {
                        facingMode: useFrontCamera ? 'user' : 'environment',
                        width: { ideal: 1920 },
                        height: { ideal: 1080 }
                    },
                    audio: false
                };
                
                console.log('Requesting camera:', constraints.video.facingMode);
                
                try {
                    currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                } catch (facingError) {
                    // facingMode failed, try without it (for desktop)
                    console.log('FacingMode failed, trying default camera');
                    constraints = { video: true, audio: false };
                    currentStream = await navigator.mediaDevices.getUserMedia(constraints);
                }
                
                video.srcObject = currentStream;
                await video.play();
                
                status.textContent = useFrontCamera ? '🤳 Front Camera' : '📷 Back Camera';
                setTimeout(() => { status.style.opacity = '0'; }, 2000);
                
            } catch (err) {
                console.error('Camera error:', err);
                status.textContent = 'Camera Error: ' + err.message;
                status.style.opacity = '1';
            }
        }
        
        // FLIP CAMERA
        flipBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            status.style.opacity = '1';
            status.textContent = 'Flipping...';
            flipBtn.style.opacity = '0.5';
            
            useFrontCamera = !useFrontCamera;
            await startCamera();
            
            flipBtn.style.opacity = '1';
        });
        
        flipBtn.addEventListener('touchend', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            status.style.opacity = '1';
            status.textContent = 'Flipping...';
            flipBtn.style.opacity = '0.5';
            
            useFrontCamera = !useFrontCamera;
            await startCamera();
            
            flipBtn.style.opacity = '1';
        });
        
        // CAPTURE PHOTO
        function capture() {
            status.style.opacity = '1';
            status.textContent = 'Capturing...';
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            const ctx = canvas.getContext('2d');
            
            // Flip horizontally if front camera (mirror effect)
            if (useFrontCamera) {
                ctx.translate(canvas.width, 0);
                ctx.scale(-1, 1);
            }
            
            ctx.drawImage(video, 0, 0);
            
            // Stop camera
            if (currentStream) {
                currentStream.getTracks().forEach(t => t.stop());
            }
            
            // Get image data
            const imageData = canvas.toDataURL('image/jpeg', 0.9);
            
            // Send to parent Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                data: imageData
            }, '*');
            
            status.textContent = 'Photo captured!';
        }
        
        captureBtn.addEventListener('click', capture);
        captureBtn.addEventListener('touchend', function(e) {
            e.preventDefault();
            capture();
        });
        
        // Initialize
        startCamera();
    </script>
    """

    st.markdown("""
    <style>
        html, body, .stApp {
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
            max-height: 100vh !important;
            position: fixed !important;
            width: 100vw !important;
            top: 0 !important;
            left: 0 !important;
        }
        header, footer, [data-testid="stSidebar"] { display: none !important; }
        .stApp { background: black !important; }
        .block-container { 
            padding: 0 !important; 
            margin: 0 !important; 
            max-width: 100vw !important;
            overflow: hidden !important;
        }
        [data-testid="stVerticalBlock"] { gap: 0 !important; }
        .stApp > div:first-child { padding: 0 !important; }
        
        /* Force iframe to be fullscreen */
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            border: none !important;
            z-index: 999998 !important;
        }
        
        /* CLOSE BUTTON - OUTSIDE IFRAME */
        #streamlit-close-btn {
            position: fixed !important;
            top: 20px !important;
            left: 20px !important;
            width: 55px;
            height: 55px;
            border-radius: 50%;
            border: 3px solid white;
            background: #dc3545;
            color: white;
            font-size: 26px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            z-index: 2147483647 !important;
            cursor: pointer;
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        #streamlit-close-btn:hover {
            background: #c82333;
        }
    </style>
    
    <a id="streamlit-close-btn" href="?close_camera=true" target="_self">✕</a>
    """, unsafe_allow_html=True)

    result = components.html(camera_html, height=2000, scrolling=False)
    
    if result and isinstance(result, str) and result.startswith('data:image'):
        try:
            base64_data = result.split(',')[1]
            image_bytes = base64.b64decode(base64_data)
            
            st.session_state.captured_image = BytesIO(image_bytes)
            st.session_state.camera_active = False
            st.rerun()
        except Exception as e:
            st.error(f"Error processing image: {e}")
    
    return None