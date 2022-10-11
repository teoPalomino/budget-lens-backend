from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipts
        fields = ('scan_date', 'receipt_image_url')
