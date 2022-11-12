from rest_framework import serializers
from item.models import Item
from receipts.models import Receipts



class ItemSerializer(serializers.ModelSerializer):
    
    receipt_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Item
        fields = '__all__'

    def create(self, validated_data):
        item = Item.objects.create(
            receipt_id=validated_data['receipt_id'],
            tax=validated_data['tax'],
            name=validated_data['name'],
            price=validated_data['price'],
            important_dates=validated_data['important_dates'],
        )
        return item