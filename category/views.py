from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response



from .models import Category, SubCategory
from .serializers import CategorySerializer, SubCategorySerializer

# Create your views here.


class CategoryView(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response({
            "category_name": category.category_name,
            "category_toggle_star": category.category_toggle_star,
        })


class SubCategoryView(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub_category = serializer.save()

        return Response({
            "sub_category_name": sub_category.sub_category_name,
            "sub_category_toggle_star": sub_category.sub_category_toggle_star,
        })
