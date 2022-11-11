from rest_framework import serializers
from .models import Category, SubCategory


class CategorySerializer(serializers.ModelSerializer):
    """Basic category seriaizer"""
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySerializer(serializers.ModelSerializer):
    """Basic Subcategory seriaizer"""
    class Meta:
        model = SubCategory
        fields = '__all__'