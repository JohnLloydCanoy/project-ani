from PIL import Image
import streamlit as st

def pic_button():
    open_camera = st.button("📸 Open Camera")
    if open_camera:
        img_file_buffer = st.camera_input("Take a picture")
        if img_file_buffer is not None:
            # To read image file buffer with PIL:
            image = Image.open(img_file_buffer)
            st.image(image, caption='Captured Image.', use_column_width=True)
            # Here you can add code to process the image as needed
    return open_camera