from rest_framework import serializers
from .models import ItemSplit


class ItemSplitSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    """
    class Meta:
        model = ItemSplit
        fields = '__all__'
