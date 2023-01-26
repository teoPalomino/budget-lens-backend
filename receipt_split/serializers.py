from rest_framework import serializers
from .models import ReceiptSplit


class ReceiptSplitSerializer(serializers.ModelSerializer):
    """
    Basic serializer that takes in a receipt object and string representation
    of the list of user ids splitting the receipt
    """
    class Meta:
        model = ReceiptSplit
        fields = ('receipt', 'shared_user_ids', 'shared_amount', 'id')

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
