import boto3
import os
import uuid
from django.conf import settings

def upload_file_to_s3(file_obj, folder_name="documents"):
    """
    Upload a file to AWS S3.
    Respects both ENABLE_MOCK_STORAGE and ENABLE_S3_STORAGE flags.
    """
    # Prioritize Mock Storage if enabled
    if getattr(settings, 'ENABLE_MOCK_STORAGE', False):
        print(f"Mock storage enabled: returning mock URL for {file_obj.name}")
        return f"https://example.com/mock-storage/{file_obj.name}"

    if not getattr(settings, 'ENABLE_S3_STORAGE', False):
        print("S3 storage disabled.")
        return None

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        ext = os.path.splitext(file_obj.name)[1]
        file_name = f"{folder_name}/{uuid.uuid4()}{ext}"
        
        s3_client.upload_fileobj(
            file_obj,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_name,
            ExtraArgs={'ACL': 'public-read'} # Or however the user wants permissions
        )
        
        url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
        return url
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None
