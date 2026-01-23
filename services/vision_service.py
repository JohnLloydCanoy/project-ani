import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
from components.take_picture import take_picture

def open_camera():
    take_picture()