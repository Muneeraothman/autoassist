import os

import boto3
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

PRESIGNED_URL_EXPIRE_SECONDS = 300

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heif",
}

s3_client = boto3.client("s3", region_name=AWS_REGION)


def build_receipt_key(user_id: int, vehicle_id: int, service_id: int, extension: str) -> str:
    return f"users/{user_id}/vehicles/{vehicle_id}/receipts/{service_id}/receipt.{extension}"


def generate_upload_url(key: str, content_type: str) -> str:
    return s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": key, "ContentType": content_type},
        ExpiresIn=PRESIGNED_URL_EXPIRE_SECONDS,
    )


def generate_view_url(key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET_NAME, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRE_SECONDS,
    )
