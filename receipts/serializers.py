from rest_framework import serializers
from merchant.models import Merchant

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    merchant = serializers.CharField(max_length=100)

    class Meta:
        model = Receipts
        fields = ('user', 'scan_date', 'receipt_image', 'merchant')

    def create(self, validated_data):
        merchant = Merchant.objects.create(
            name=validated_data['merchant']
        )
        receipt = Receipts.objects.create(
            user=validated_data['user'],
            receipt_image=validated_data['receipt_image'],
            merchant=merchant
        )
        return receipt
