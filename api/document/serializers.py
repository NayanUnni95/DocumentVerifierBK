from rest_framework import serializers
from db.document import Document
from django.conf import settings


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for returning id, tiel document details for create docs
    """
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'document_hash',
            'blockchain_tx_hash',
        ]

class DocumentListAllSerializer(serializers.ModelSerializer):
    """
    Serializer for returning complete document details for list all docs
    """
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'type',
            'description',
            'issue_at',
            'expiry_at',
            'document_hash',
            'blockchain_tx_hash',
        ]

class DocumentListSpecifcSerializer(serializers.ModelSerializer):
    """
    Serializer for returning complete document details for list specific doc
    """
    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'type',
            'description',
            'recipient_name',
            'recipient_email',
            'issuing_affiliation',
            # 'settings',
            "source_url",
            'issue_at',
            'expiry_at',
            'document_hash',
            'blockchain_tx_hash',
        ]

class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating documents.
    Handles title, type, description, and recipient details.
    The uploaded file is used to upload to S3; the returned URL is stored in source_url.
    source_url and ocr_content are NOT accepted from the client directly.
    """
    file = serializers.FileField(required=False, write_only=True)

    class Meta:
        model = Document
        fields = [
            'title',
            'type',
            'description',
            'recipient_name',
            'recipient_email',
            'issuing_affiliation',
            'settings',
            'issue_at',
            'expiry_at',
            'file',
            'source_url',
        ]
        read_only_fields = ['id']

    def _upload_file(self, file_obj):
        """
        Uploads the file to S3 (or returns mock URL if S3 is disabled).
        Returns the URL string, or '' if no file given.
        """
        if not file_obj:
            return ''
        from utils.s3_utils import upload_file_to_s3
        print(f"Uploading file to S3: {file_obj.name}", flush=True)
        file_obj.seek(0)
        url = upload_file_to_s3(file_obj)
        print(f"Upload result URL: {url}", flush=True)
        return url or ''

    def create(self, validated_data):
        # print(f"[DEBUG] create() called. Keys in validated_data: {list(validated_data.keys())}", flush=True)

        # Extract the file — do NOT pass it to the model
        file_obj = validated_data.pop('file', None)
        # print(f"[DEBUG] file_obj after pop: {file_obj}", flush=True)

        # Upload file and set source_url
        url = self._upload_file(file_obj)
        # print(f"[DEBUG] URL returned from _upload_file: {url!r}", flush=True)
        validated_data['source_url'] = url

        # Set default ocr_content if not already provided by view
        if 'ocr_content' not in validated_data:
            if not getattr(settings, 'ENABLE_OCR', True):
                validated_data['ocr_content'] = {
                    "status": "disabled",
                    "message": "OCR feature is currently disabled via feature flag",
                    "ocr_text": "Default OCR content: OCR processing is disabled. Please enable it in settings to process documents.",
                    "pages": []
                }
            else:
                validated_data['ocr_content'] = {"status": "pending", "message": "OCR processing in progress"}

        # print(f"[DEBUG] Final source_url before save: {validated_data.get('source_url')!r}", flush=True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Extract the file — do NOT pass it to the model
        file_obj = validated_data.pop('file', None)

        # If a new file is uploaded, re-upload and update source_url
        if file_obj:
            url = self._upload_file(file_obj)
            if url:
                validated_data['source_url'] = url

        # Handle partial update for the 'settings' JSON field
        if 'settings' in validated_data and isinstance(validated_data['settings'], dict):
            existing_settings = instance.settings or {}
            new_settings = validated_data.pop('settings')
            # Merge the new settings into the existing one
            existing_settings.update(new_settings)
            instance.settings = existing_settings

        return super().update(instance, validated_data)
