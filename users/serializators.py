from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username", "first_name", 
            "last_name", "email", "password"
        ]
        # exclude = ["username"]


# class UserSerializer(serializers.Serializer):
#     username = serializers.CharField(
#         required=True,
#         read_only=True,
#         max_length=50
#     )

#     def validate(self, attrs):
#         if len(attrs) < 8:
#             raise ValueError
#         return super().validate(attrs)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_repeat = serializers.CharField(required=False)

    def validate(self, attrs):
        user = self.context["request"].user
        current_password = attrs.get("current_password")
        new_password = attrs.get("new_password")
        new_password_repeat = attrs.get("new_password_repeat")

        if not check_password(current_password, user.password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        if new_password_repeat is not None and new_password != new_password_repeat:
            raise serializers.ValidationError({"new_password_repeat": "Passwords do not match."})

        if current_password == new_password:
            raise serializers.ValidationError({"new_password": "New password must be different from current password."})

        return attrs