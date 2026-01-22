def take_picture():
    img_file_buffer = st.camera_input("Take a picture", label_visibility="collapsed")
        
    if img_file_buffer is not None:
            image = Image.open(img_file_buffer)
            st.session_state.camera_active = False
            st.rerun()
            return image