from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from users.models import UserProfile

class PhoneAuthRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)

class PhoneAuthConfirmSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=4)

class UserProfileSerializer(serializers.ModelSerializer):
    invited_users = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ['phone', 'invite_code', 'activated_invite_code', 'invited_by', 'invited_users']

    def get_invited_users(self, obj):
        return [u.phone for u in obj.invited_users.all()]

class InviteCodeActivateSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username", "first_name", 
            "last_name", "email", "password"
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        validated_data["is_active"] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"]
            )
        return super().update(instance, validated_data)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(required=True, max_length=50)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True, max_length=50)
    last_name = serializers.CharField(required=True, max_length=50)
    email = serializers.EmailField(required=True)

    def validate_username(self, value):
        if "admin" in value.lower():
            raise serializers.ValidationError("Username cannot contain 'admin'")
        return value

    def validate(self, attrs):
        if attrs["username"] == attrs.get("password"):
            raise serializers.ValidationError("Password cannot be the same as username")
        self.validate_username(value=attrs["username"])
        return attrs

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data["password"]
        )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(
                validated_data["password"]
            )
        return super().update(instance, validated_data)


