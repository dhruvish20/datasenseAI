import streamlit as st
from state import init_session_state
from utils import ask_question, poll_result

init_session_state()

st.title("Ask a Question")

if not st.session_state.file_id:
    st.warning("Please upload a CSV first in the Upload tab.")
    st.stop()

question = st.text_input("Enter your question")

if st.button("Ask"):
    try:
        with st.spinner("Sending to backend..."):
            resp = ask_question(st.session_state.file_id, question)
            task_id = resp.get("task_id")

        with st.spinner("Waiting for result..."):
            import time
            while True:
                result = poll_result(task_id)
                if result["status"] == "done":
                    break
                time.sleep(1)

            answer = result.get("answer")
            if answer.endswith(".png") or "s3.amazonaws.com" in answer:
                st.image(answer, use_container_width=True) 
            else:
                st.write(answer)


    except Exception as e:
        st.error(f"Error: {e}")
