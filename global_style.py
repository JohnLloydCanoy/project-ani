import streamlit as st


# --- MOBILE-FRIENDLY CSS ---
st.markdown("""
<style>
    /* Clean layout */
    .block-container { 
        padding: 1rem !important; 
        padding-bottom: 120px !important;
        max-width: 100% !important;
    }
    
    /* Hide technical stuff */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Navigation buttons - big and clear */
    .nav-button {
        display: inline-block;
        padding: 15px 25px;
        margin: 5px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 15px;
        text-decoration: none;
        cursor: pointer;
        border: none;
        transition: all 0.3s;
    }
    
    .nav-active {
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.4);
    }
    
    .nav-inactive {
        background: #f0f0f0;
        color: #333;
    }
    
    /* Big buttons */
    .stButton > button {
        width: 100% !important;
        min-height: 55px !important;
        font-size: 18px !important;
        border-radius: 15px !important;
        margin: 5px 0 !important;
    }
    
    /* Camera styling */
    [data-testid="stCameraInput"] { width: 100% !important; }
    [data-testid="stCameraInput"] video { 
        width: 100% !important; 
        border-radius: 15px !important;
        max-height: 35vh !important;
    }
    [data-testid="stCameraInput"] button { 
        width: 100% !important; 
        height: 60px !important; 
        background-color: #22c55e !important; 
        color: white !important; 
        font-size: 20px !important; 
        border-radius: 15px !important; 
    }
    
    /* Chat messages */
    [data-testid="stChatMessage"] {
        font-size: 17px !important;
        padding: 12px !important;
        border-radius: 12px !important;
    }
    
    /* Global floating mic section */
    .floating-mic-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        padding: 15px 20px;
        z-index: 9999;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
        border-radius: 20px 20px 0 0;
    }
    
    .mic-hint {
        color: white;
        text-align: center;
        font-size: 14px;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    
    /* Page header */
    .page-header {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid #22c55e;
    }
    
    .page-title {
        font-size: 28px;
        font-weight: bold;
        color: #16a34a;
        margin: 0;
    }
    
    .page-subtitle {
        font-size: 16px;
        color: #666;
        margin: 5px 0 0 0;
    }
    
    /* Command examples box */
    .command-box {
        background: #fffbeb;
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .command-title {
        font-weight: bold;
        color: #d97706;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

