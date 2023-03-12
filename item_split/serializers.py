from rest_framework import serializers

from item.models import Item
from .models import ItemSplit


class ItemSplitSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    """
    item_id = serializers.IntegerField(source='item.id')

    class Meta:
        model = ItemSplit
        fields = ('item_id', 'shared_user_ids', 'is_shared_with_item_user', 'id')

    def to_internal_value(self, data):
        """
        Convert string value of `item_id` to integer
        """
        if isinstance(data.get('item_id'), str):
            data['item_id'] = int(data['item_id'])
        return super().to_internal_value(data)

    def create(self, validated_data):
        item_id = validated_data.pop('item')['id']
        num_to_divide_by = len(validated_data['shared_user_ids'].split(','))

        if validated_data['is_shared_with_item_user']:
            num_to_divide_by += 1

        shared_amount = Item.objects.get(id=item_id).price / num_to_divide_by

        item_split = ItemSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            shared_amount=shared_amount,
            is_shared_with_item_user=validated_data['is_shared_with_item_user'],
            item_id=item_id
        )

        return item_split
