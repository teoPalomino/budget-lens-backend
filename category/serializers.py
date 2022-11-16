from rest_framework import serializers
from .models import Category


class BasicCategorySerializer(serializers.ModelSerializer):
    """Basic category seriaizer which contains all fields except the user field"""
    class Meta:
        model = Category
        fields = ('category_name', 'category_toggle_star', 'parent_category_id')

    def create(self, validated_data):
        return Category.objects.create(
            category_name=validated_data['category_name'],
            category_toggle_star=validated_data['category_toggle_star'],
            parent_category_id=validated_data['parent_category_id'],
            user=self.context['request'].user
        )

    def update(self, instance, validated_data):

        return super().update(instance, validated_data)


# class BasicSubCategorySerializer(serializers.ModelSerializer):
#     """Basic Subcategory seriaizer which contains all fields except the user field"""

#     class Meta:
#         model = SubCategory
#         fields = ('parent_category', 'sub_category_name', 'sub_category_toggle_star')

#     def create(self, validated_data):
#         return SubCategory.objects.create(
#             parent_category=validated_data['parent_category'],
#             sub_category_name=validated_data['sub_category_name'],
#             sub_category_toggle_star=validated_data['sub_category_toggle_star'],
#             user=self.context['request'].user
#         )


class ToggleStarCategorySerializer(serializers.ModelSerializer):
    """category seriaizer with just the toggle star field"""
    class Meta:
        model = Category
        fields = ('category_toggle_star')


# class ToggleStarSubCategorySerializer(serializers.ModelSerializer):
#     """sub category seriaizer with just the toggle star field"""
#     class Meta:
#         model = SubCategory
#         fields = ('sub_category_toggle_star')
