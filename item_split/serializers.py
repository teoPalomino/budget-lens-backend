from unicodedata import decimal

from rest_framework import serializers

from item.models import Item
from .models import ItemSplit


class ItemSplitAmountSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    """

    class Meta:
        model = ItemSplit
        fields = ('item', 'shared_user_ids', 'shared_amount')

    def create(self, validated_data):
        is_shared_with_item_user = False
        if validated_data['item'].user.pk in list(validated_data['shared_user_ids']):
            is_shared_with_item_user = True

        return ItemSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_item_user=is_shared_with_item_user,
            shared_amount=validated_data['shared_amount'],
            item=validated_data['item']
        )


class ItemSplitPercentageSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    Converts the percentage to the actual amount
    """

    class Meta:
        model = ItemSplit
        fields = ('item', 'shared_user_ids', 'shared_amount')

    def create(self, validated_data):
        is_shared_with_item_user = False
        if validated_data['item'].user.pk in list(map(int, validated_data['shared_user_ids'].split(','))):
            is_shared_with_item_user = True

        # Convert the percentage to the actual amount
        item_price = Item.objects.get(pk=validated_data['item'].pk).price
        shared_amount = list(map(float, validated_data['shared_amount'].split(',')))

        for i in range(len(shared_amount)):
            shared_amount[i] = float(shared_amount[i]) * float(item_price)

        shared_amount = ','.join(map(str, shared_amount))

        return ItemSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_item_user=is_shared_with_item_user,
            shared_amount=shared_amount,
            item=validated_data['item']
        )
