import streamlit as st

def init_session_state():
    if "file_id" not in st.session_state:
        st.session_state.file_id = None
    if "upload_url" not in st.session_state:
        st.session_state.upload_url = None
    if "filename" not in st.session_state:
        st.session_state.filename = None
