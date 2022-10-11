from rest_framework import serializers
from receipts.models import Receipts


class ReceiptsSerializer(serializers.ModelSerializer):
    user_token = serializers.CharField(source='user_token.key', read_only=True)
    scan_date = serializers.DateTimeField(read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    scanned_receipt = serializers.ImageField(read_only=True)

    class Meta:
        model = Receipts
        fields = ('scan_date', 'user', 'user_token', 'scanned_receipt')
