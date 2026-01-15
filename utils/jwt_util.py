from datetime import datetime, timedelta, timezone
import jwt

from backend import settings
from utils.types import Algorithm
from utils.types import JWTTokenKey


class JWTUtil:
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            JWTTokenKey.EXPIRY.value: str(expire),
            JWTTokenKey.TOKEN_TYPE.value: "Access Token",
            JWTTokenKey.PRODUCT_NAME.value: settings.PROJECT_NAME
        })
    
        return jwt.encode(to_encode, settings.SECRET_KEY, Algorithm.HS256.value)


    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            JWTTokenKey.EXPIRY.value: str(expire),
            JWTTokenKey.TOKEN_TYPE.value: "Refresh Token",
            JWTTokenKey.PRODUCT_NAME.value: settings.PROJECT_NAME
        })

        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=Algorithm.HS256.value)