import streamlit as st
from state import init_session_state

init_session_state()

st.set_page_config(page_title="DataSense", page_icon="📊", layout="wide")
st.title("Welcome to DataSense")
st.markdown("Start by uploading a CSV file from the sidebar ➡️")
