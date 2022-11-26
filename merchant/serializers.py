from rest_framework import serializers
from .models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ('name',)

    def create(self, validated_data):
        return Merchant.objects.create(
            name=validated_data['name']
        )
