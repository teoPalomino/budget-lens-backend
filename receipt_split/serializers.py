from rest_framework import serializers

from receipts.models import Receipts
from .models import ReceiptSplit
from users.models import User


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

        owners_receipt = Receipts.objects.get(id=validated_data['receipt'].pk)
        shared_amount_total = sum(list(map(float, validated_data['shared_amount'].split(','))))

        # Subtract the total amount of the shared amount from the total amount of the receipt
        if owners_receipt.total - shared_amount_total >= 0:
            owners_receipt.total = owners_receipt.total - shared_amount_total
            owners_receipt.save()
        else:
            raise serializers.ValidationError(
                'The total amount of the shared amount is greater than the total amount of the receipt')

        owners_receipt.total = owners_receipt.total - shared_amount_total
        owners_receipt.save()

        # Create a new receipt for each user id in the list of user ids, excluding the receipt owner
        for ids in list(map(int, validated_data['shared_user_ids'].split(','))):
            if ids is not owners_receipt.user.pk:
                Receipts.objects.create(
                    user=User.objects.get(pk=ids),
                    scan_date=owners_receipt.scan_date,
                    receipt_image=owners_receipt.receipt_image,
                    merchant=owners_receipt.merchant,
                    location=owners_receipt.location,
                    total=owners_receipt.total,
                    tax=owners_receipt.tax,
                    tip=owners_receipt.tip,
                    coupon=owners_receipt.coupon,
                    currency=owners_receipt.currency
                )

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
        receipt_total = Receipts.objects.get(pk=validated_data['receipt'].pk).total
        shared_amount = list(map(float, validated_data['shared_amount'].split(',')))

        for i in range(len(shared_amount)):
            shared_amount[i] = float(shared_amount[i]) * float(receipt_total)

        owners_receipt = Receipts.objects.get(id=validated_data['receipt'].pk)

        shared_amount_total = sum(shared_amount)

        # Subtract the total amount of the shared amount from the total amount of the receipt
        if owners_receipt.total - shared_amount_total >= 0:
            owners_receipt.total = owners_receipt.total - shared_amount_total
            owners_receipt.save()
        else:
            raise serializers.ValidationError(
                'The total amount of the shared amount is greater than the total amount of the receipt')

        # Create a new receipt for each user id in the list of user ids, excluding the receipt owner
        for ids in list(map(int, validated_data['shared_user_ids'].split(','))):
            if ids is not owners_receipt.user.pk:
                Receipts.objects.create(
                    user=User.objects.get(pk=ids),
                    scan_date=owners_receipt.scan_date,
                    receipt_image=owners_receipt.receipt_image,
                    merchant=owners_receipt.merchant,
                    location=owners_receipt.location,
                    total=owners_receipt.total,
                    tax=owners_receipt.tax,
                    tip=owners_receipt.tip,
                    coupon=owners_receipt.coupon,
                    currency=owners_receipt.currency
                )

        shared_amount = ','.join(map(str, shared_amount))

        return ReceiptSplit.objects.create(
            shared_user_ids=validated_data['shared_user_ids'],
            is_shared_with_receipt_owner=is_shared_with_receipt_owner,
            shared_amount=shared_amount,
            receipt=validated_data['receipt']
        )
