from rest_framework import serializers
from images.models import Images

class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id', 'image', 'user']
        read_only_fields = ['id', 'user']