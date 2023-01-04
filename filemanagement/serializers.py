from rest_framework import serializers
from .models import *

class FilesSerializer(serializers.ModelSerializer):
    """File Upload"""
    class Meta:
        model = Files
        fields = '__all__'