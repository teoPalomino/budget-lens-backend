from rest_framework import serializers
from important_dates.models import ImportantDates


class ImportantDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantDates
        fields = '__all__'

    def create(self, validated_data):
        important_date = ImportantDates.objects.create(
            user=validated_data['user'],
            item=validated_data['item'],
            date=validated_data['date'],
            description=validated_data['description'],
        )
        return important_date
