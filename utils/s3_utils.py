import boto3
import os
import uuid
from django.conf import settings

def upload_file_to_s3(file_obj, folder_name="documents"):
    """
    Upload a file to AWS S3.
    If ENABLE_S3_STORAGE is True, uploads to real S3.
    If ENABLE_S3_STORAGE is False, returns a mock URL.
    """
    # Use Mock Storage if S3 is disabled
    if not getattr(settings, 'ENABLE_S3_STORAGE', False):
        print(f"S3 Storage is disabled: returning mock URL for {file_obj.name}", flush=True)
        return f"https://example.com/mock-storage/{file_obj.name}"

    print(f"Starting S3 upload process for file: {file_obj.name}", flush=True)
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        ext = os.path.splitext(file_obj.name)[1]
        # S3 automatically creates "folders" based on the key prefix
        file_name = f"{folder_name}/{uuid.uuid4()}{ext}"
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # print(f"Target Bucket: {bucket_name}", flush=True)
        # print(f"Target Key (Path): {file_name}", flush=True)
        
        # Determine ACL - some buckets block public access
        upload_args = {}
        upload_args['ContentType'] = file_obj.content_type
        
        # print(f"Uploading to S3 with ACL: {upload_args.get('ContentType')}...", flush=True)
        
        s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            file_name,
            ExtraArgs=upload_args
        )
        
        # print("S3 upload successful!", flush=True)
        url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
        # print(f"Generated S3 URL: {url}", flush=True)
        return url
    except Exception as e:
        print(f"!!! S3 Upload Error: {str(e)}", flush=True)
        print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}", flush=True)
        print(f"Region: {settings.AWS_S3_REGION_NAME}", flush=True)
        # Hint about common issues
        if "AccessDenied" in str(e):
            print("Hint: Check if your AWS credentials have S3 PutObject permissions and if the bucket allows 'public-read' ACL.", flush=True)
        return None
