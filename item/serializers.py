from rest_framework import serializers
from item.models import Item
from receipts.models import Receipts
from receipts.serializers import ReceiptsSerializer

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def create(self, validated_data):
        item = Item.objects.create(
            user=validated_data['user'],
            receipt=validated_data['receipt'],
            name=validated_data['name'],
            price=validated_data['price'],
            important_dates=validated_data['important_dates'],
        )
        return item
        

class PutPatchItemSerializer(serializers.ModelSerializer):
    '''Serializer for PutItems, used to update a users items in a receipt'''
    
    receipt = serializers.HiddenField(default=Receipts)

    class Meta:
        model = Item
        fields = ('receipt_id', 'name', 'price','important_dates')