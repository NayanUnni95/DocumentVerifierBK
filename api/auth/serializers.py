from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from db.user import User
from utils.hashing_util import Hash


class EmailAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "email", "password"]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        password = validated_data.pop("password")
        hashed_password = Hash.encrypt_password(password)
        validated_data["password"] = hashed_password

        user = super().create(validated_data)
        return user

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }