from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from fastapi import Request
from slowapi.middleware import SlowAPIMiddleware
from celery.result import AsyncResult
from app.worker.tasks import celery as celery_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from fastapi import Request
from slowapi.errors import RateLimitExceeded
# from slowapi.decorators import limiter
from app.s3_utils import generate_presigned_url
from app.redis_utils import save_file_metadata, get_file_metadata, get_cached_answer
from app.worker.tasks import process_question

app = FastAPI()

origins = ["http://localhost:8501"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_real_ip(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host

limiter = Limiter(key_func=get_real_ip)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )



class AskRequest(BaseModel):
    file_id: str
    question: str

class UploadRequest(BaseModel):
    filename: str

cache_hits = 0
cache_misses = 0

@app.post("/ask/")
@limiter.limit("20/minute")  
async def ask_question(request: Request, data: AskRequest):
    global cache_hits, cache_misses
    file_meta = get_file_metadata(data.file_id)
    if not file_meta:
        return JSONResponse(status_code=404, content={"error": "File metadata not found"})

    cached = get_cached_answer(data.file_id, data.question)
    if cached:
        cache_hits += 1
        return {"answer": cached, "cached": True}
    else:
        cache_misses += 1

    print(f"[CACHE] Hits: {cache_hits}, Misses: {cache_misses}")
    task = process_question.delay(data.file_id, data.question)
    return {"status": "processing", "task_id": task.id}

@app.post("/upload/")
async def get_presigned_url(file: UploadRequest):
    print("[backend] /upload/ endpoint hit")

    user_id = str(uuid.uuid4())
    upload_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())

    try:
        print(f"[backend] Generating presigned URL for: {file.filename}")
        upload_url, s3_key = generate_presigned_url(user_id, upload_id, file.filename)
        print(f"[backend] S3 Key: {s3_key}")

        save_file_metadata(file_id, file.filename, s3_key, user_id=user_id)
        print("[backend] Metadata saved to Redis")

        return {
            "upload_url": upload_url,
            "file_id": file_id,
            "s3_path": s3_key,
            "message": "Upload successful"
        }
    except Exception as e:
        print("[backend] ERROR in /upload/:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "pending"}
    if result.state == "SUCCESS":
        return {"status": "done", "answer": result.result}
    return {"status": result.state}

@app.get("/cache_stats/")
async def get_cache_stats():
    return {
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "hit_rate": f"{(cache_hits / (cache_hits + cache_misses + 1e-5)):.2%}"
    }