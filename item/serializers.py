from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    """Basic Item seriaizer"""
    class Meta:
        model = Item
        fields = '__all__'
