import jwt

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime, timedelta, timezone
import uuid

from db.user import User
from backend import settings
from utils.types import Algorithm
from utils.types import JWTTokenKey


class JWTUtil:
    @staticmethod
    def create_access_token(data: dict):
        to_encode = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            JWTTokenKey.EXPIRY.value: str(expire),
            JWTTokenKey.TOKEN_TYPE.value: "Access Token",
            JWTTokenKey.PRODUCT_NAME.value: settings.PROJECT_NAME
        })
    
        return jwt.encode(to_encode, settings.SECRET_KEY, Algorithm.HS256.value)


    @staticmethod
    def decode_token(token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[Algorithm.HS256.value])
            # Manual expiry check since we use a custom 'expiry' key
            expiry_str = payload.get(JWTTokenKey.EXPIRY.value)
            if expiry_str:
                expiry = datetime.fromisoformat(expiry_str)
                if datetime.now(timezone.utc) > expiry:
                    return None
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in data.items()}
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            JWTTokenKey.EXPIRY.value: str(expire),
            JWTTokenKey.TOKEN_TYPE.value: "Refresh Token",
            JWTTokenKey.PRODUCT_NAME.value: settings.PROJECT_NAME
        })

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=Algorithm.HS256.value)



class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        try:
            header_parts = auth_header.split()
            if len(header_parts) != 2 or header_parts[0].lower() != "bearer":
                return None
            
            token = header_parts[1]
            payload = JWTUtil.decode_token(token)
            
            if not payload:
                raise AuthenticationFailed("Invalid or expired token")
            
            user_id = payload.get(JWTTokenKey.ID.value)
            if not user_id:
                raise AuthenticationFailed("Invalid token payload")
                
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
        except Exception as e:
            return None