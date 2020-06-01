from rest_framework import serializers
from .models import Signature

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = (
            'document',
        )