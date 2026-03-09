from rest_framework import serializers
from db.document import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for returning id, tiel document details for create docs
    """
    class Meta:
        model = Document
        fields = [
            'id',
            'title'
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
            'issue_at',
            'expiry_at',
        ]

class DocumentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating documents
    Handles title, type, description, and recipient details
    source_url and ocr_content are populated via internal logic
    """
    class Meta:
        model = Document
        fields = [
            # 'id',
            'title',
            'type',
            'description',
            'recipient_name',
            'recipient_email',
            'issuing_affiliation',
            'settings',
            'issue_at',
            'expiry_at',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        if 'source_url' not in validated_data:
            validated_data['source_url'] = "https://example.com/placeholder-source-url"
        if 'ocr_content' not in validated_data:
            validated_data['ocr_content'] = {"status": "pending", "message": "OCR processing in progress"}
        
        return super().create(validated_data)
