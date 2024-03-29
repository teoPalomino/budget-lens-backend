from rest_framework import serializers
from merchant.models import Merchant

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    receipt_image = serializers.ImageField(use_url=True)

    class Meta:
        model = Receipts
        fields = ('user', 'receipt_image')

    def create(self, validated_data):
        receipt = Receipts.objects.create(
            user=validated_data['user'],
            receipt_image=validated_data['receipt_image']
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
            receipt_image=validated_data.get('receipt_image', None),
            merchant=merchant,
            location=validated_data['location'],
            total=validated_data['total'],
            tax=validated_data['tax'],
            tip=validated_data['tip'],
            coupon=validated_data['coupon'],
            currency=validated_data['currency']
        )
        return receipt


class PutPatchReceiptsSerializer(serializers.ModelSerializer):
    '''Serializer for PutReceipts, used to update the receipt of a user if need be'''
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    merchant_name = serializers.SerializerMethodField()

    def get_merchant_name(self, obj):
        if obj.merchant:
            return obj.merchant.name
        return None

    class Meta:
        model = Receipts
        fields = (
            'user',
            'scan_date',
            'receipt_image',
            'merchant_name',
            'total',
            'currency',
        )
