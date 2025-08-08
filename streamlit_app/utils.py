import requests

BACKEND_URL = "http://backend:8000"  

def get_presigned_upload(filename: str):
    try:
        print(f"[frontend] Sending POST to backend /upload with filename: {filename}")
        res = requests.post("http://backend:8000/upload/", json={"filename": filename})
        print(f"[frontend] Received response: {res.status_code} - {res.text}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[frontend] Exception in get_presigned_upload: {e}")
        raise

def upload_file_to_s3(upload_url: str, file_bytes: bytes):
    headers = {"Content-Type": "text/csv"}
    res = requests.put(upload_url, data=file_bytes, headers=headers)
    res.raise_for_status()

def ask_question(file_id, question):
    print(f"[frontend] Sending POST to backend /upload with filename: {file_id} and question: {question}")
    res = requests.post("http://backend:8000/ask/",json={"file_id": file_id, "question": question})
    print(f"[frontend] Received response: {res.status_code} - {res.text}")
    res.raise_for_status() 
    return res.json()

def poll_result(task_id: str):
    res = requests.get(f"{BACKEND_URL}/result/{task_id}")
    res.raise_for_status()
    return res.json()


