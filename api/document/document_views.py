from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from api.document import serializers
from db.document import Document
from utils.jwt_util import JWTAuthentication
from utils.response import CustomResponse


class DocumentListCreateView(APIView):
    """
    Handles GET for listing user documents and POST for creating a new document.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Allow filtering or pagination later for scalability
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
            
        # The serializer handles default values for source_url and ocr_content in .create()
        # We manually set the audit fields (created_by and updated_by) here
        document = serializer.save(created_by=request.user, updated_by=request.user)
        
        detail_serializer = serializers.DocumentSerializer(document, many=False)
        return CustomResponse(
            message="Document created successfully",
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

        # Update audit field updated_by
        document = serializer.save(updated_by=request.user)
        
        detail_serializer = serializers.DocumentSerializer(document, many=False)
        return CustomResponse(
            message="Document updated successfully",
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
