from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

from api.document import serializers
from db.document import Document
from utils.jwt_util import JWTAuthentication
from utils.response import CustomResponse
from utils.doctr_utils import extract_document_text
import tempfile
import os
from utils.hashing_util import HashingUtils
from utils.blockchain_util import BlockchainUtils
from utils.feature_flags import FeatureFlags


class DocumentListCreateView(APIView):
    """
    Handles GET for listing user documents and POST for creating a new document.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _process_ocr(self, file_obj):
        """
        Helper method to perform OCR on an uploaded file.
        Check's ENABLE_OCR feature flag from settings.
        """
        if not file_obj:
            return None

        # Centralized check for OCR feature flag
        if not getattr(settings, 'ENABLE_OCR', True):
            return {
                "status": "disabled",
                "message": "OCR feature is currently disabled via feature flag",
                "ocr_text": "Default OCR content: OCR processing is disabled. Please enable it in settings to process documents.",
                "pages": []
            }

        # Save the uploaded file to a temporary location for processing
        file_obj.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_obj.name)[1]) as temp_file:
            for chunk in file_obj.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        try:
            return extract_document_text(temp_file_path, structured=True)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def get(self, request):
        documents = Document.objects.filter(created_by=request.user)
        serializer = serializers.DocumentListAllSerializer(documents, many=True)
        return CustomResponse(
            message="Documents retrieved successfully",
            response=serializer.data
        ).get_success_response()

    def post(self, request):
        serializer = serializers.DocumentCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(message=serializer.errors).get_failure_response()

        file_obj = request.FILES.get('file')

        # Run OCR before saving (needs the file pointer at position 0)
        ocr_result = self._process_ocr(file_obj)

        # Build save arguments — serializer.create() handles the S3 upload itself
        save_kwargs = {'created_by': request.user, 'updated_by': request.user}
        if ocr_result:
            save_kwargs['ocr_content'] = ocr_result

        # Hashing and Blockchain logic
        doc_hash = None
        tx_hash = None
        if ocr_result and ocr_result.get('status') not in ['error', 'disabled'] and FeatureFlags.ENABLE_BLOCKCHAIN:
            try:
                # Generate hash from OCR result
                doc_hash = HashingUtils.sha256_from_json(ocr_result)
                save_kwargs['document_hash'] = doc_hash

                # Send hash to blockchain
                blockchain_utils = BlockchainUtils()
                tx_hash = blockchain_utils.send_hash_transaction(doc_hash)
                save_kwargs['blockchain_tx_hash'] = tx_hash
            except Exception as e:
                # Log error or handle as needed
                print(f"Blockchain/Hashing error: {str(e)}")

        document = serializer.save(**save_kwargs)

        detail_serializer = serializers.DocumentSerializer(document, many=False)

        # Build response message
        message = "Document created successfully"
        if ocr_result:
            if ocr_result.get('status') == 'disabled':
                message += " (OCR disabled)"
            elif ocr_result.get('status') == 'error':
                message += " (OCR processing failed)"
            else:
                message += " with OCR"

        if document.source_url:
            if getattr(settings, 'ENABLE_S3_STORAGE', False):
                message += " and uploaded to S3"
            else:
                message += " (Mock storage used)"
        elif file_obj:
            message += " (Storage upload failed)"

        return CustomResponse(
            message=message,
            response=detail_serializer.data
        ).get_success_response()


class DocumentRetrieveUpdateDeleteView(APIView):
    """
    Handles GET (retrieve), PUT (update), and DELETE for a specific document.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_document(self, pk, user):
        try:
            return Document.objects.get(pk=pk, created_by=user)
        except Document.DoesNotExist:
            return None

    def get(self, request, pk):
        document = self.get_document(pk, request.user)
        if not document:
            return CustomResponse(
                general_message="Document not found or access denied."
            ).get_failure_response(status_code=404)

        serializer = serializers.DocumentListSpecifcSerializer(document, many=False)
        return CustomResponse(
            message="Document retrieved successfully",
            response=serializer.data
        ).get_success_response()

    def put(self, request, pk):
        document = self.get_document(pk, request.user)
        if not document:
            return CustomResponse(
                general_message="Document not found or access denied."
            ).get_failure_response(status_code=404)

        serializer = serializers.DocumentCreateUpdateSerializer(document, data=request.data, partial=True)
        if not serializer.is_valid():
            return CustomResponse(message=serializer.errors).get_failure_response()

        file_obj = request.FILES.get('file')

        # Run OCR if a new file was sent
        ocr_result = None
        if file_obj:
            list_view = DocumentListCreateView()
            ocr_result = list_view._process_ocr(file_obj)

        # serializer.update() handles S3 re-upload automatically when file is present
        save_kwargs = {'updated_by': request.user}
        if ocr_result:
            save_kwargs['ocr_content'] = ocr_result

        # Hashing and Blockchain logic
        doc_hash = None
        tx_hash = None
        if ocr_result and ocr_result.get('status') not in ['error', 'disabled'] and FeatureFlags.ENABLE_BLOCKCHAIN:
            try:
                # Generate new hash from OCR result
                doc_hash = HashingUtils.sha256_from_json(ocr_result)
                save_kwargs['document_hash'] = doc_hash

                # Send new hash to blockchain
                blockchain_utils = BlockchainUtils()
                tx_hash = blockchain_utils.send_hash_transaction(doc_hash)
                save_kwargs['blockchain_tx_hash'] = tx_hash
            except Exception as e:
                print(f"Blockchain/Hashing error: {str(e)}")

        document = serializer.save(**save_kwargs)

        detail_serializer = serializers.DocumentSerializer(document, many=False)

        message = "Document updated successfully"
        if ocr_result:
            if ocr_result.get('status') == 'disabled':
                message += " (OCR disabled)"
            elif ocr_result.get('status') == 'error':
                message += " (OCR processing failed)"
            else:
                message += " with OCR"

        if file_obj and document.source_url:
            if getattr(settings, 'ENABLE_S3_STORAGE', False):
                message += " and updated in S3"
            else:
                message += " (Mock storage used)"
        elif file_obj:
            message += " (Storage update failed)"

        return CustomResponse(
            message=message,
            response=detail_serializer.data
        ).get_success_response()

    def delete(self, request, pk):
        document = self.get_document(pk, request.user)
        if not document:
            return CustomResponse(
                general_message="Document not found or access denied."
            ).get_failure_response(status_code=404)

        document.delete()
        return CustomResponse(
            message="Document deleted successfully"
        ).get_success_response()
