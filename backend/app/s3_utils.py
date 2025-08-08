import boto3
import os
from dotenv import load_dotenv
load_dotenv()
from app.redis_utils import get_file_metadata
from typing import Tuple

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client(
    "s3",
    region_name = os.getenv("AWS_REGION"),
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
)

def generate_presigned_url(user_id: str, upload_id: str, filename: str, expiration: int = 3600) -> Tuple[str, str]:
    s3_key = f"{user_id}/uploads/{upload_id}/{filename}.csv"

    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": S3_BUCKET_NAME,
            "Key": s3_key,
            "ContentType": "text/csv"
        },
        ExpiresIn=expiration
    )
    return presigned_url, s3_key

def download_file_from_s3(file_id):
    file_meta = get_file_metadata(file_id)
    if not file_meta:
        raise Exception("File metadata not found for file_id: " + file_id)

    key = file_meta["s3_path"]  
    local_path = f"/tmp/{file_id}.csv"

    s3_client.download_file(S3_BUCKET_NAME, key, local_path)
    return local_path
