import io
import matplotlib.pyplot as plt
import boto3
import os
from uuid import uuid4
import tempfile
from app.redis_utils import get_file_metadata
from dotenv import load_dotenv
load_dotenv()


s3_bucket_name = os.getenv("S3_BUCKET_NAME")
s3_client = boto3.client("s3")

def upload_plot_to_s3(fig, file_id: str, prefix: str) -> str:
    meta = get_file_metadata(file_id)
    if not meta:
        raise Exception("No metadata found")

    print(f"[DEBUG] Uploading plot for file_id: {file_id} with prefix: {prefix}")
    user_id = meta["user_id"]
    s3_base = f"{user_id}/uploads/{file_id}/{prefix}"
    filename = f"{uuid4()}.png"
    key = f"{s3_base}/{filename}"

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        fig.savefig(tmp.name)
        s3_client.upload_file(
            tmp.name,
            s3_bucket_name,
            key,
            ExtraArgs={"ContentType": "image/png"} 
        )
        os.unlink(tmp.name)

    presigned_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_bucket_name, "Key": key},
        ExpiresIn=3600
    )

    return presigned_url

def store_text_result(file_id: str, content: str, filename="results.json"):
    meta = get_file_metadata(file_id)
    if not meta:
        raise Exception("No metadata")

    user_id = meta["user_id"]
    key = f"{user_id}/uploads/{file_id}/{filename}"

    s3_client.put_object(
        Bucket=s3_bucket_name,
        Key=key,
        Body=content.encode("utf-8"),
        ContentType="application/json"
    )
