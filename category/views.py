from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from item.models import Item



from .models import Category, SubCategory
from .serializers import *

# Create your views here.


class AddCategoryView(generics.GenericAPIView):
    """API for adding a new category"""
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = BasicCategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response({
            "category_name": category.category_name,
            "category_toggle_star": category.category_toggle_star,
        })

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class AddSubCategoryView(generics.GenericAPIView):
    """API for adding a new subcategory"""
    queryset = SubCategory.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = BasicSubCategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sub_category = serializer.save()

        return Response({
            "sub_category_name": sub_category.sub_category_name,
            "sub_category_toggle_star": sub_category.sub_category_toggle_star,
        })

    def get_queryset(self):
        return SubCategory.objects.filter(user=self.request.user)


class DeleteSubCategoryView(generics.DestroyAPIView):
    """API for registering a new user"""
    serializer_class = BasicSubCategorySerializer
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        print(kwargs["subCategoryName"])
        try:
            sub_category = SubCategory.objects.get(user=self.request.user, sub_category_name=kwargs['subCategoryName'])
        except Exception:
            return Response({
                "Description": "SubCategory does not exist"
            })
        if Item.objects.filter(sub_category_id=sub_category).exists():
            return Response({
                "Description": "Cannot delete SubCategory, items exists in this subcategory"
            })

        SubCategory.objects.filter(user=self.request.user, sub_category_name=kwargs['subCategoryName']).delete()
        return Response({
            "Description": 'SubCategory succesfully deleted'
        })
        

    def get_queryset(self):
        return SubCategory.objects.filter(user=self.request.user)


class ListCategoriesAndSubCategoriesView(generics.ListAPIView):
    serializer_class = ListCategoriesAndSubCategoriesSerializer
    permission_classes = (IsAuthenticated, )
    
    def get_queryset(self):
        return SubCategory.objects.filter(user=self.request.user)