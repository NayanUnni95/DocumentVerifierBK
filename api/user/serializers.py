from rest_framework import serializers
from db.user import User, Affiliation
from utils.hashing_util import Hash

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.password = Hash.encrypt_password(password)
        
        return super().update(instance, validated_data)

class AffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Affiliation
        fields = ["id", "name", "type", "website"]
        read_only_fields = ["id"]
