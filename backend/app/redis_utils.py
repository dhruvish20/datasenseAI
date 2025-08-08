import redis
import os
import json
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)

def save_file_metadata(file_id: str, filename: str, s3_path: str, user_id: Optional[str] = None):
    key = f"file:{file_id}"
    metadata = {
        "filename": filename,
        "s3_path": s3_path,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    if user_id:
        metadata["user_id"] = user_id

    print(f"[DEBUG] Saving metadata to Redis under key {key}: {metadata}")
    redis_client.hset(key, mapping=metadata)


def get_cached_answer(file_id, question):
    key = f"{file_id}:{question}"
    val = redis_client.get(key)
    return val if val else None 

def get_file_metadata(file_id: str):
    key = f"file:{file_id}"
    data = redis_client.hgetall(key)
    return data if data else None

def cache_answer(file_id: str, question: str, answer: str):
    key = f"answer:{file_id}:{question}"
    redis_client.set(key, answer)
