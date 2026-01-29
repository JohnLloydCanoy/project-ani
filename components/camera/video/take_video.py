import streamlit as st
import streamlit.components.v1 as components
import base64


def open_video_camera():
    """Opens the camera for video recording and manages state. Returns True if camera is active."""
    if "video_camera_active" not in st.session_state:
        st.session_state.video_camera_active = False
    
    # Check if user clicked close via query param
    query_params = st.query_params
    if query_params.get("close_video_camera") == "true":
        st.session_state.video_camera_active = False
        st.query_params.clear()
        st.rerun()

    if not st.session_state.video_camera_active:
        if st.button("🎥 Open Video Camera"):
            st.session_state.video_camera_active = True
            st.rerun()
        return False
    
    return True


def get_video_camera_styles():
    """Returns the video camera UI styles."""
    return """
        <style>
            /* RESET: Hide ALL Streamlit UI */
            header, footer, [data-testid="stSidebar"], 
            [data-testid="stHeader"], [data-testid="stToolbar"],
            .stDeployButton, #MainMenu {
                display: none !important;
                visibility: hidden !important;
            }
            
            /* RESET: Remove ALL margins/padding */
            html, body, [data-testid="stAppViewContainer"], 
            [data-testid="stMain"], .main, .block-container,
            [data-testid="stVerticalBlock"] {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100vw !important;
                width: 100vw !important;
                height: 100vh !important;
                overflow: hidden !important;
            }
            
            .video-container {
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                bottom: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 99999 !important;
                background: #000 !important;
            }
            
            #videoElement {
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                object-fit: cover !important;
                z-index: 1 !important;
            }
            
            #custom-close-btn {
                position: fixed !important;
                top: 20px !important;
                left: 20px !important;
                z-index: 999999999 !important;
                background: #dc3545 !important;
                color: white !important;
                border: 3px solid white !important;
                border-radius: 50% !important;
                width: 60px !important;
                height: 60px !important;
                font-size: 32px !important;
                font-weight: bold !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
                text-decoration: none !important;
            }
            
            #switchCameraBtn {
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                z-index: 999999999 !important;
                background: rgba(255,255,255,0.9) !important;
                color: #000 !important;
                border: none !important;
                border-radius: 50% !important;
                width: 60px !important;
                height: 60px !important;
                font-size: 28px !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 4px 20px rgba(0,0,0,0.7) !important;
            }
            
            #recordBtn {
                position: fixed !important;
                bottom: 30px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 100001 !important;
                width: 80px !important;
                height: 80px !important;
                border-radius: 50% !important;
                background: #fff !important;
                border: 5px solid #fff !important;
                cursor: pointer !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            #recordBtn .inner {
                width: 60px !important;
                height: 60px !important;
                background: #dc3545 !important;
                border-radius: 50% !important;
                transition: all 0.2s ease !important;
            }
            
            #recordBtn.recording .inner {
                width: 30px !important;
                height: 30px !important;
                border-radius: 8px !important;
            }
            
            #timer {
                position: fixed !important;
                top: 100px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 999999999 !important;
                background: rgba(220, 53, 69, 0.9) !important;
                color: white !important;
                padding: 10px 20px !important;
                border-radius: 20px !important;
                font-size: 18px !important;
                font-weight: bold !important;
                display: none !important;
            }
            
            #timer.visible {
                display: block !important;
            }
        </style>
    """


def get_video_recorder_html():
    """Returns the HTML/JS for video recording with back camera support."""
    return """
        <div class="video-container">
            <video id="videoElement" autoplay playsinline muted></video>
            <a id="custom-close-btn" href="?close_video_camera=true" target="_self">✕</a>
            <button id="switchCameraBtn" onclick="switchCamera()">🔄</button>
            <button id="recordBtn" onclick="toggleRecording()">
                <div class="inner"></div>
            </button>
            <div id="timer">● REC 00:00</div>
        </div>
        
        <script>
            let stream = null;
            let mediaRecorder = null;
            let recordedChunks = [];
            let isRecording = false;
            let timerInterval = null;
            let seconds = 0;
            let currentFacingMode = 'environment'; // Start with back camera
            
            async function initCamera(facingMode) {
                // Stop existing stream
                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
                
                try {
                    stream = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: facingMode },
                        audio: true
                    });
                    document.getElementById('videoElement').srcObject = stream;
                    currentFacingMode = facingMode;
                } catch (err) {
                    // If back camera fails, try front camera
                    if (facingMode === 'environment') {
                        try {
                            stream = await navigator.mediaDevices.getUserMedia({
                                video: { facingMode: 'user' },
                                audio: true
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
            
            function toggleRecording() {
                if (!isRecording) {
                    startRecording();
                } else {
                    stopRecording();
                }
            }
            
            function startRecording() {
                recordedChunks = [];
                const options = { mimeType: 'video/webm;codecs=vp9,opus' };
                
                try {
                    mediaRecorder = new MediaRecorder(stream, options);
                } catch (e) {
                    // Fallback for browsers that don't support vp9
                    mediaRecorder = new MediaRecorder(stream);
                }
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: 'video/webm' });
                    const url = URL.createObjectURL(blob);
                    
                    // Create download link
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'recorded_video_' + Date.now() + '.webm';
                    a.click();
                    
                    // Send to Streamlit via postMessage
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64data = reader.result;
                        window.parent.postMessage({
                            type: 'video_recorded',
                            data: base64data
                        }, '*');
                    };
                    reader.readAsDataURL(blob);
                };
                
                mediaRecorder.start();
                isRecording = true;
                document.getElementById('recordBtn').classList.add('recording');
                document.getElementById('timer').classList.add('visible');
                
                // Start timer
                seconds = 0;
                timerInterval = setInterval(() => {
                    seconds++;
                    const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
                    const secs = (seconds % 60).toString().padStart(2, '0');
                    document.getElementById('timer').textContent = '● REC ' + mins + ':' + secs;
                }, 1000);
            }
            
            function stopRecording() {
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                }
                isRecording = false;
                document.getElementById('recordBtn').classList.remove('recording');
                document.getElementById('timer').classList.remove('visible');
                
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                }
            }
            
            // Initialize with back camera
            initCamera('environment');
        </script>
    """


def take_video():
    """Opens camera and records video. Returns the recorded video or None."""
    camera_is_active = open_video_camera()
    
    if not camera_is_active:
        return None
    
    st.markdown(get_video_camera_styles(), unsafe_allow_html=True)
    
    components.html(get_video_recorder_html(), height=800)
    
    return None