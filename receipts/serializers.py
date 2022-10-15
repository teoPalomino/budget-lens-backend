from rest_framework import serializers

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Receipts
        fields = ('user', 'scan_date', 'receipt_image',)
