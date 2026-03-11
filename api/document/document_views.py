from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from db.activity import Activity
from utils.types import ActivityType
from utils.s3_utils import delete_file_from_s3


class OCRProcessorView(APIView):
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


class DocumentListCreateView(OCRProcessorView):
    """
    Handles GET for listing user documents and POST for creating a new document.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

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

        # Log activity
        Activity.objects.create(
            user=request.user,
            doc_owner=request.user,
            doc=document,
            activity_type=ActivityType.UPLOAD.value
        )

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


class DocumentRetrieveUpdateDeleteView(OCRProcessorView):
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
            message="Documents retrieved successfully",
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

        old_public_view = document.settings.get('public_view', False)

        file_obj = request.FILES.get('file')

        # Run OCR if a new file was sent
        ocr_result = None
        if file_obj:
            ocr_result = self._process_ocr(file_obj)

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

        new_public_view = document.settings.get('public_view', False)
        if old_public_view != new_public_view:
            Activity.objects.create(
                user=request.user,
                doc_owner=request.user,
                doc=document,
                activity_type=ActivityType.SHARED.value
            )

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

        if document.source_url:
            delete_file_from_s3(document.source_url)

        document.delete()
        return CustomResponse(
            message="Document deleted successfully"
        ).get_success_response()


class DocumentInsightView(APIView):
    """
    Provides insights for the user's documents and activities.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Document counts
        all_docs = Document.objects.filter(created_by=user)
        total_docs = all_docs.count()
        
        # Public vs Private logic based on JSON settings
        # This is more efficient than iterating in memory if possible, 
        # but since settings is a JSONField, filtering depends on DB support.
        # However, for simplicity and reliability across different DB backends:
        public_docs = Document.objects.filter(created_by=user, settings__public_view=True).count()
        private_docs = total_docs - public_docs

        # Activity counts
        total_verification = Activity.objects.filter(
            doc_owner=user, 
            activity_type=ActivityType.CHECK.value
        ).count()
        
        total_shared = Activity.objects.filter(
            doc_owner=user, 
            activity_type=ActivityType.SHARED.value
        ).count()

        return CustomResponse(
            message="Insights retrieved successfully",
            response={
                "total_docs": total_docs,
                "public_docs": public_docs,
                "private_docs": private_docs,
                "total_verification": total_verification,
                "total_shared": total_shared
            }
        ).get_success_response()


class ActivityListView(APIView):
    """
    Handles GET for listing user activities.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = Activity.objects.filter(doc_owner=request.user).order_by('-created_at')
        serializer = serializers.ActivitySerializer(activities, many=True)
        return CustomResponse(
            message="Activities retrieved successfully",
            response=serializer.data
        ).get_success_response()


class DocumentVerifyView(OCRProcessorView):
    """
    Handles public document verification via file upload.
    No authentication required.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return CustomResponse(
                general_message="No file provided."
            ).get_failure_response(status_code=400)

        # 1. OCR extraction
        ocr_result = self._process_ocr(file_obj)
        
        if not ocr_result or ocr_result.get('status') in ['error', 'disabled']:
            error_msg = "OCR processing failed" if ocr_result and ocr_result.get('status') == 'error' else "OCR is disabled"
            return CustomResponse(
                general_message="Verification failed: " + error_msg
            ).get_failure_response(status_code=400)

        # 2. Hashing
        try:
            doc_hash = HashingUtils.sha256_from_json(ocr_result)
        except Exception as e:
            return CustomResponse(
                general_message=f"Hashing failed: {str(e)}"
            ).get_failure_response(status_code=500)

        # 3. Verify in database & check on blockchain if enabled
        document = Document.objects.filter(document_hash=doc_hash).first()
        
        if not document:
            return CustomResponse(
                general_message="Verification failed: Document hash not found in records."
            ).get_failure_response(status_code=404)

        # "Check in the chain" - verify tx data matches hash if blockchain is enabled
        if FeatureFlags.ENABLE_BLOCKCHAIN and document.blockchain_tx_hash:
            try:
                blockchain_utils = BlockchainUtils()
                tx = blockchain_utils.get_transaction(document.blockchain_tx_hash)
                # Chain check: compare input data with our hash
                # Note: tx['input'] returns a HexBytes object, convert it to a hex string for comparison
                chain_data_hex = blockchain_utils.w3.to_hex(tx.get('input', b''))
                expected_data_hex = blockchain_utils.w3.to_hex(text=doc_hash)
                
                if chain_data_hex.lower() != expected_data_hex.lower():
                    return CustomResponse(
                        general_message="Verification failed: Blockchain data mismatch."
                    ).get_failure_response(status_code=400)
            except Exception as e:
                return CustomResponse(
                    general_message=f"Blockchain verification failed: {str(e)}"
                ).get_failure_response(status_code=400)

        # Log activity
        Activity.objects.create(
            user=None, # Public user
            doc_owner=document.created_by,
            doc=document,
            activity_type=ActivityType.CHECK.value
        )

        # 4. Return basic details
        serializer = serializers.DocumentListAllSerializer(document)
        return CustomResponse(
            message="Document verified successfully",
            response=serializer.data
        ).get_success_response()


class DocumentPublicView(APIView):
    """
    Handles public document viewing via ID.
    No authentication required. Returns docs data if the doc is public.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
        except Document.DoesNotExist:
            return CustomResponse(
                general_message="Document not found."
            ).get_failure_response(status_code=404)

        # Check if the document is public in settings
        # The settings look like: {"public_view": True}
        public_view = document.settings.get('public_view', False)
        
        if not public_view:
            return CustomResponse(
                general_message="Access denied. This document is not public."
            ).get_failure_response(status_code=403)

        serializer = serializers.DocumentListSpecifcSerializer(document)
        return CustomResponse(
            message="Document retrieved successfully",
            response=serializer.data
        ).get_success_response()
