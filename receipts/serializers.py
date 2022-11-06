from rest_framework import serializers
from merchant.models import Merchant

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    merchant = serializers.CharField(max_length=100)

    class Meta:
        model = Receipts
        fields = '__all__'

    def create(self, validated_data):
        merchant = Merchant.objects.create(
            name=validated_data['merchant']
        )
        receipt = Receipts.objects.create(
            user=validated_data['user'],
            receipt_image=validated_data['receipt_image'],
            merchant=merchant,
            location=validated_data['location'],
            total=validated_data['total'],
            tax=validated_data['tax'],
            tip=validated_data['tip'],
            coupon=validated_data['coupon'],
            currency=validated_data['currency'],
            important_dates=validated_data['important_dates'],
        )
        return receipt


class ManualReceiptsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    merchant = serializers.CharField(max_length=100)

    class Meta:
        model = Receipts
        fields = '__all__'

    def create(self, validated_data):
        merchant = Merchant.objects.create(
            name=validated_data['merchant']
        )
        receipt = Receipts.objects.create(
            user=validated_data['user'],
            receipt_image=validated_data['receipt_image'],
            merchant=merchant,
            location=validated_data['location'],
            total=validated_data['total'],
            tax=validated_data['tax'],
            tip=validated_data['tip'],
            coupon=validated_data['coupon'],
            currency=validated_data['currency'],
            important_dates=validated_data['important_dates'],
        )
        return receipt


class PutPatchReceiptsSerializer(serializers.ModelSerializer):
    '''Serializer for PutReceipts, used to update the receipt of a user if need be'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Receipts
        fields = ('user', 'merchant', 'currency', 'scan_date', 'total', 'location', 'receipt_image', 'important_dates')
