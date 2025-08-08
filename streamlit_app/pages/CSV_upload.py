import streamlit as st
from state import init_session_state
from utils import get_presigned_upload, upload_file_to_s3

init_session_state()

st.title("📤 Upload your CSV")

file = st.file_uploader("Upload your CSV", type=["csv"])


if file:
    st.session_state.filename = file.name
    st.success(f"File selected: {file.name}")

    if st.button("Upload to S3"):
        with st.spinner("Uploading..."):
            print("[frontend] Upload button clicked.")
            try:
                resp = get_presigned_upload(file.name)
                print("[frontend] Presigned response:", resp)
                upload_file_to_s3(resp["upload_url"], file.getvalue())
                print("[frontend] File uploaded to S3.")
                st.session_state.file_id = resp["file_id"]
                st.session_state.upload_url = resp["upload_url"]
                st.success("File uploaded!")
                st.info(f"Your file_id: `{st.session_state.file_id}`")
            except Exception as e:
                st.error(f"Upload failed: {e}")
                print("[frontend] Upload failed:", e)
