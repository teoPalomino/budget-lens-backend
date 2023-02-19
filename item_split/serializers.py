from rest_framework import serializers
from .models import ItemSplit


class ItemSplitSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    """
    class Meta:
        model = ItemSplit
        fields = ('item', 'shared_user_ids', 'id')

    def create(self, validated_data):
        num_to_divide_by = len(validated_data['shared_user_ids'].split(','))

        is_shared_with_item_user = False
        if validated_data['item'].user.pk in list(map(int, validated_data['shared_user_ids'].split(','))):
            is_shared_with_item_user = True

        shared_amount = validated_data['item'].price / num_to_divide_by

        return ItemSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_item_user=is_shared_with_item_user,
            shared_amount=shared_amount,
            item=validated_data['item']
        )
