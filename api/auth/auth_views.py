from rest_framework.views import APIView
from api.auth import serializers
from django.conf import settings

from utils.response import CustomResponse
from db.user import User
from utils.hashing_util import Hash
from utils.jwt_util import JWTUtil


class RegisterView(APIView):
    """
    User registration endpoint
    Creates a new user account with email and password
    """

    def post(self, request):
        data = request.data
        data = {key: value for key, value in data.items() if value}

        serializer = serializers.UserSerializer(data=data)
        if not serializer.is_valid():
            return CustomResponse(message=serializer.errors).get_failure_response()
        
        user = serializer.save()

        user_access_token = JWTUtil.create_access_token({"id": user.id})
        user_refresh_token = JWTUtil.create_refresh_token({"id": user.id})
        response_data = serializers.UserDetailSerializer(user, many=False).data

        return CustomResponse(
            message="User registered successfully",
            response={
                "user": response_data,
                "access_token": user_access_token,
                "access_token_expiry": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token": user_refresh_token,
                "refresh_token_expiry": settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            }
        ).get_success_response()


class LoginView(APIView):
    """
    User login endpoint
    Authenticates user and returns JWT token
    """

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return CustomResponse(
                message="Email and password are required"
            ).get_failure_response()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return CustomResponse(
                message="Invalid email or password"
            ).get_failure_response()

        if not Hash.verify_password(password, user.password):
            return CustomResponse(
                message="Invalid email or password"
            ).get_failure_response()

        user_access_token = JWTUtil.create_access_token({"id": user.id})
        user_refresh_token = JWTUtil.create_refresh_token({"id": user.id})

        user_data = serializers.UserDetailSerializer(user, many=False).data

        return CustomResponse(
            message="User login success.",
            response={
                "user": user_data,
                "access_token": user_access_token,
                "access_token_expiry": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                "refresh_token": user_refresh_token,
                "refresh_token_expiry": settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            }
        ).get_success_response()
