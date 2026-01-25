def get_picture_camera_html():
    """Returns the HTML/JS for picture taking with back camera support."""
    return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body, html {
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                width: 100% !important;
                height: 100% !important;
                background: #000 !important;
            }
            
            .camera-container {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000;
                overflow: hidden;
            }
            
            #videoElement {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            #canvas {
                display: none;
            }
            
            #closeBtn {
                position: absolute;
                top: 20px;
                left: 15px;
                z-index: 9999;
                background: #dc3545;
                color: white;
                border: 3px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 26px;
                font-weight: bold;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.7);
            }
            
            #switchCameraBtn {
                position: absolute;
                top: 20px;
                right: 15px;
                z-index: 9999;
                background: rgba(255,255,255,0.9);
                color: #000;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 24px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.7);
            }
            
            #captureBtn {
                position: absolute;
                bottom: 80px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 9999;
                padding: 15px 45px;
                font-size: 18px;
                border-radius: 30px;
                background: rgba(255,255,255,0.95);
                color: #000;
                border: none;
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
                cursor: pointer;
            }
            
            #captureBtn:active {
                background: rgba(200,200,200,0.9);
                transform: translateX(-50%) scale(0.95);
            }
            
            #previewContainer {
                display: none;
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000;
                z-index: 10000;
            }
            
            #previewImage {
                width: 100%;
                height: 100%;
                object-fit: cover;
            }
            
            #retakeBtn, #usePhotoBtn {
                position: absolute;
                bottom: 80px;
                z-index: 10001;
                padding: 15px 30px;
                font-size: 16px;
                border-radius: 30px;
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            }
            
            #retakeBtn {
                left: 10%;
                background: #dc3545;
                color: white;
            }
            
            #usePhotoBtn {
                right: 10%;
                background: #28a745;
                color: white;
            }
            
            /* Responsive adjustments */
            @media (max-width: 400px) {
                #closeBtn, #switchCameraBtn {
                    width: 45px;
                    height: 45px;
                    font-size: 22px;
                }
                
                #captureBtn {
                    padding: 12px 35px;
                    font-size: 16px;
                    bottom: 60px;
                }
                
                #retakeBtn, #usePhotoBtn {
                    padding: 12px 22px;
                    font-size: 14px;
                    bottom: 60px;
                }
            }
        </style>
        
        <div class="camera-container">
            <video id="videoElement" autoplay playsinline></video>
            <canvas id="canvas"></canvas>
            <button id="switchCameraBtn" onclick="switchCamera()">🔄</button>
            <button id="captureBtn" onclick="capturePhoto()">Take Photo</button>
        </div>
        
        <div id="previewContainer">
            <img id="previewImage" />
            <button id="retakeBtn" onclick="retakePhoto()">Retake</button>
            <button id="usePhotoBtn" onclick="usePhoto()">Use Photo</button>
        </div>
        
        <script>
            let stream = null;
            let currentFacingMode = 'environment'; // Start with back camera
            
            function closeCamera() {
                // Stop camera stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                // Navigate to close - this forces a full page reload with the query param
                window.top.location.href = '/?close_camera=true';
            }
            
            async function initCamera(facingMode) {
                // Stop existing stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        video: { 
                            facingMode: facingMode,
                            width: { ideal: 1920 },
                            height: { ideal: 1080 }
                        },
                        audio: false
                    });
                    document.getElementById('videoElement').srcObject = stream;
                    currentFacingMode = facingMode;
                } catch (err) {
                    // If back camera fails, try front camera
                    if (facingMode === 'environment') {
                        try {
                            stream = await navigator.mediaDevices.getUserMedia({
                                video: { 
                                    facingMode: 'user',
                                    width: { ideal: 1920 },
                                    height: { ideal: 1080 }
                                },
                                audio: false
                            });
                            document.getElementById('videoElement').srcObject = stream;
                            currentFacingMode = 'user';
                        } catch (err2) {
                            console.error('Camera error:', err2);
                            alert('Could not access camera');
                        }
                    }
                }
            }
            
            function switchCamera() {
                const newFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
                initCamera(newFacingMode);
            }
            
            function capturePhoto() {
                const video = document.getElementById('videoElement');
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');
                
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0);
                
                const imageData = canvas.toDataURL('image/jpeg', 0.9);
                document.getElementById('previewImage').src = imageData;
                document.getElementById('previewContainer').style.display = 'block';
                document.querySelector('.camera-container').style.display = 'none';
            }
            
            function retakePhoto() {
                document.getElementById('previewContainer').style.display = 'none';
                document.querySelector('.camera-container').style.display = 'block';
            }
            
            function usePhoto() {
                const imageData = document.getElementById('previewImage').src;
                
                // Stop camera stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                
                // Download the image
                const a = document.createElement('a');
                a.href = imageData;
                a.download = 'photo_' + Date.now() + '.jpg';
                a.click();
                
                // Show message to user to click the X button to close
                alert('Photo saved! Click the X button to return to the main page.');
            }
            
            // Initialize with back camera
            initCamera('environment');
        </script>
    """


def get_picture_camera_styles():
    """Returns styles to hide Streamlit UI when camera is active."""
    return """
        <style>
            header, footer, [data-testid="stSidebar"], 
            [data-testid="stHeader"], [data-testid="stToolbar"],
            .stDeployButton, #MainMenu {
                display: none !important;
                visibility: hidden !important;
            }
            
            html, body, [data-testid="stAppViewContainer"], 
            [data-testid="stMain"], .main, .block-container,
            [data-testid="stVerticalBlock"] {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100vw !important;
                width: 100vw !important;
                height: 100vh !important;
                overflow: hidden !important;
                background: #000 !important;
            }
            
            [data-testid="stVerticalBlock"] > div:has(> iframe) {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 999999 !important;
            }
            
            [data-testid="stVerticalBlock"] > div:has(> iframe) > iframe {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                border: none !important;
                z-index: 999999 !important;
            }
        </style>
    """
