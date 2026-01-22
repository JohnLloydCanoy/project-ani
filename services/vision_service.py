import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
from components.open_camera import pic_button

def open_camera():
    pic_button()