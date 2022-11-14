from rest_framework import serializers
from .models import Category, SubCategory


class BasicCategorySerializer(serializers.ModelSerializer):
    """Basic category seriaizer"""
    class Meta:
        model = Category
        fields = ('category_name', 'category_toggle_star')

    def create(self, validated_data):
        print(self.context['request'].user)
        return Category.objects.create(
            category_name=validated_data['category_name'],
            category_toggle_star=validated_data['category_toggle_star'],
            user=self.context['request'].user
        )


class BasicSubCategorySerializer(serializers.ModelSerializer):
    """Basic Subcategory seriaizer"""

    class Meta:
        model = SubCategory
        fields = ('parent_category', 'sub_category_name', 'sub_category_toggle_star')

    def create(self, validated_data):
        print(self.context['request'].user)
        return SubCategory.objects.create(
            parent_category=validated_data['parent_category'],
            sub_category_name=validated_data['sub_category_name'],
            sub_category_toggle_star=validated_data['sub_category_toggle_star'],
            user=self.context['request'].user
        )


class DeleteSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ('sub_category_name')


class ToogleStarCategorySerializer(serializers.ModelSerializer):
    """category seriaizer with just the toggle star field"""
    class Meta:
        model = Category
        fields = ('category_toggle_star')


class ToogleStarSubCategorySerializer(serializers.ModelSerializer):
    """category seriaizer with just the toggle star field"""
    class Meta:
        model = Category
        fields = ('category_toggle_star')