from rest_framework import serializers
from item.models import Item
from receipts.models import Receipts


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def create(self, validated_data):
        item = Item.objects.create(
            user=validated_data['user'],
            receipt=validated_data['receipt'],
            category_id=validated_data['category_id'],
            name=validated_data['name'],
            price=validated_data['price']
        )
        return item


class PutPatchItemSerializer(serializers.ModelSerializer):
    '''Serializer for PutItems, used to update a users items in a receipt'''

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    receipt = serializers.HiddenField(default=Receipts)

    class Meta:
        model = Item
        fields = ('user', 'receipt', 'category_id', 'name', 'price')
