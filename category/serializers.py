from rest_framework import serializers
from .models import Category


class BasicCategorySerializer(serializers.ModelSerializer):
    """Basic category seriaizer which contains all fields except the user field"""
    class Meta:
        model = Category
        fields = ('id', 'category_name', 'category_toggle_star', 'parent_category_id', 'icon')

    def create(self, validated_data):
        return Category.objects.create(
            category_name=validated_data['category_name'],
            category_toggle_star=validated_data['category_toggle_star'],
            parent_category_id=validated_data['parent_category_id'],
            user=self.context['request'].user
        )
