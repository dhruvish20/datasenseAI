from celery import Celery
from app.s3_utils import download_file_from_s3
from app.agents.agent_runner import run_agent_on_csv
from app.redis_utils import cache_answer
import os
from dotenv import load_dotenv
load_dotenv()
import time

celery = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

@celery.task
def process_question(file_id: str, question: str):
    start = time.time()
    local_csv_path = download_file_from_s3(file_id)
    answer = run_agent_on_csv(local_csv_path, question, file_id=file_id)

    cache_answer(file_id, question, answer)
    duration = time.time() - start
    print(f"[⏱] Total processing time: {duration:.2f} seconds")
    return answer

