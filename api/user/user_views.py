from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from db.user import Affiliation
from api.user import serializers
from utils.jwt_util import JWTAuthentication
from utils.response import CustomResponse

class UserProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = serializers.UserProfileSerializer(request.user)
        return CustomResponse(
            message="User profile retrieved successfully",
            response=serializer.data
        ).get_success_response()

    def put(self, request):
        serializer = serializers.UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return CustomResponse(
                message="User profile updated successfully",
                response=serializer.data
            ).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()

    def delete(self, request):
        user = request.user
        user.delete()
        return CustomResponse(
            message="User account deleted successfully"
        ).get_success_response()

class UserOrgView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_affiliation(self, user):
        return Affiliation.objects.filter(user=user).first()

    def get(self, request):
        affiliation = self.get_affiliation(request.user)
        if not affiliation:
             return CustomResponse(
                general_message="Organization details not found"
            ).get_failure_response(status_code=404)
            
        serializer = serializers.AffiliationSerializer(affiliation)
        return CustomResponse(
            message="Organization details retrieved successfully",
            response=serializer.data
        ).get_success_response()

    def put(self, request):
        affiliation = self.get_affiliation(request.user)
        if affiliation:
            serializer = serializers.AffiliationSerializer(affiliation, data=request.data, partial=True)
        else:
            serializer = serializers.AffiliationSerializer(data=request.data)
            
        if serializer.is_valid():
            serializer.save(user=request.user)
            return CustomResponse(
                message="Organization details updated successfully",
                response=serializer.data
            ).get_success_response()
        return CustomResponse(message=serializer.errors).get_failure_response()

    def delete(self, request):
        affiliation = self.get_affiliation(request.user)
        if not affiliation:
            return CustomResponse(
                general_message="Organization details not found"
            ).get_failure_response(status_code=404)
            
        affiliation.delete()
        return CustomResponse(
            message="Organization details deleted successfully"
        ).get_success_response()
