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

def delete_file_from_s3(file_url):
    """
    Deletes a file from AWS S3 using its full URL.
    """
    if not getattr(settings, 'ENABLE_S3_STORAGE', False):
        print(f"S3 Storage is disabled: mock deletion for {file_url}", flush=True)
        return True

    if not file_url:
        return False

    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    try:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        # The key is anything after the bucket domain
        # Example URL: https://bucket.s3.region.amazonaws.com/folder/file-uuid.ext
        # We need to extract 'folder/file-uuid.ext'
        
        # Split by the bucket name and the .s3. domain
        parts = file_url.split(f"{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/")
        if len(parts) < 2:
             # Try a simpler split if the above fails (sometimes region is omitted in some S3 URLs or varies)
            parts = file_url.split(".amazonaws.com/")
            if len(parts) < 2:
                print(f"Could not parse S3 key from URL: {file_url}", flush=True)
                return False
        
        file_key = parts[1]
        
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"Successfully deleted {file_key} from S3 bucket {bucket_name}", flush=True)
        return True
    except Exception as e:
        print(f"!!! S3 Deletion Error: {str(e)}", flush=True)
        return False
