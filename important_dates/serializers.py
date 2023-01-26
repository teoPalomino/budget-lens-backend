from rest_framework import serializers
from important_dates.models import ImportantDates
from item.models import Item


class ImportantDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImportantDates
        fields = ('item', 'date', 'description')

    def create(self, validated_data):
        important_date = ImportantDates.objects.create(
            user=self.context['request'].user,
            item=validated_data['item'],
            date=validated_data['date'],
            description=validated_data['description'],
        )
        return important_date


class PutPatchImportantDatesSerializer(serializers.ModelSerializer):
    '''Serializer for PutImportantDates, used to update a users important dates'''

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item = serializers.HiddenField(default=Item)

    class Meta:
        model = ImportantDates
        fields = ('user', 'item', 'date', 'description')
