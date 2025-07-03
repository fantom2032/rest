from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


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


