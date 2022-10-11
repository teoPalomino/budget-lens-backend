from rest_framework import serializers

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipts
        fields = ('receipt_image',)
