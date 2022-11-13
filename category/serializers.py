from rest_framework import serializers
from .models import Category, SubCategory


class BasicCategorySerializer(serializers.ModelSerializer):
    """Basic category seriaizer"""
    class Meta:
        model = Category
        fields = '__all__'


class BasicSubCategorySerializer(serializers.ModelSerializer):
    """Basic Subcategory seriaizer"""

    class Meta:
        model = SubCategory
        fields = '__all__'

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