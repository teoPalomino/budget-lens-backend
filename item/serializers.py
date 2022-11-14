from rest_framework import serializers
from item.models import Item
from receipts.models import Receipts
from receipts.serializers import ReceiptsSerializer

class ItemSerializer(serializers.ModelSerializer):
    receipt_id = serializers.IntegerField(required=True)
    class Meta:
        model = Item
        fields = ('receipt_id', 'tax', 'name', 'price', 'important_dates')

    def create(self, validated_data):
        item = Item.objects.create(
            receipt_id=validated_data['receipt_id'],
            tax=validated_data['tax'],
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
        fields = ('receipt_id', 'tax', 'name', 'price','important_dates')