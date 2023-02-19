from rest_framework import serializers

from receipts.models import Receipts
from .models import ReceiptSplit


class ReceiptSplitSerializer(serializers.ModelSerializer):
    """
    Basic serializer that takes in a receipt object and string representation
    of the list of user ids splitting the receipt
    """
    class Meta:
        model = ReceiptSplit
        fields = ('receipt', 'shared_user_ids', 'shared_amount')

    def create(self, validated_data):
        is_shared_with_receipt_owner = False

        if validated_data['receipt'].user.pk in list(map(int, validated_data['shared_user_ids'].split(','))):
            is_shared_with_receipt_owner = True

        return ReceiptSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_receipt_owner=is_shared_with_receipt_owner,
            shared_amount=validated_data['shared_amount'],
            receipt=validated_data['receipt']
        )


class ReceiptSplitPercentageSerializer(serializers.ModelSerializer):
    """
    Basic Serializer that takes in item object and string representation
    of the list of user ids splitting the item
    Converts the percentage to the actual amount
    """

    class Meta:
        model = ReceiptSplit
        fields = ('receipt', 'shared_user_ids', 'shared_amount')

    def create(self, validated_data):
        is_shared_with_receipt_owner = False

        if validated_data['receipt'].user.pk in list(map(int, validated_data['shared_user_ids'].split(','))):
            is_shared_with_receipt_owner = True

        # Convert the percentage to the actual amount
        receipt_price = Receipts.objects.get(pk=validated_data['receipt'].pk).total
        shared_amount = list(map(float, validated_data['shared_amount'].split(',')))

        for i in range(len(shared_amount)):
            shared_amount[i] = float(shared_amount[i]) * float(receipt_price)

        shared_amount = ','.join(map(str, shared_amount))

        return ReceiptSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_receipt_owner=is_shared_with_receipt_owner,
            shared_amount=shared_amount,
            receipt=validated_data['receipt']
        )
