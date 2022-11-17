# from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from item.models import Item

from .models import Category
from .serializers import BasicCategorySerializer


# Create your views here.


class AddCategoryView(generics.GenericAPIView):
    """
    API for adding a new category (either a new parent category or adding a new sub category):
    End users are not allowed to create a new parent category, but they can create a new sub category.
    However, this route containes both functionalities so that when a new user is registered, we can call
    this route to create the parent categories. The frontend should limit the user to only create subcategories
    and not create parent categories.
    """
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = BasicCategorySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        return Response({
            "category_name": category.category_name,
            "category_toggle_star": category.category_toggle_star,
            "parent_category_id": category.parent_category_id
        })

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class DeleteCategoryView(generics.DestroyAPIView):
    serializer_class = BasicCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Check if the category exists
        try:
            category = self.get_queryset().get(category_name=kwargs['categoryName'])
        except Exception:
            return Response({
                "Description": "This sub category does not exist"
            })

        # Make sure not to delete the parent category
        if self.get_queryset().filter(category_name=kwargs['categoryName'], parent_category_id=None).exists():
            return Response({
                "Description": "This is a parent Category, it cannot be deleted"
            })

        # Check not to delete the subcategory if items exists already
        if Item.objects.filter(category_id=category.id).exists():
            return Response({
                "Description": "Cannot delete SubCategory, items exists in this subcategory"
            })

        # If all condtions passed, then delete the item
        Category.objects.filter(user=self.request.user, category_name=kwargs['categoryName']).delete()
        return Response({
            "Description": 'SubCategory succesfully deleted'
        })


class ListCategoriesAndSubCategoriesView(generics.ListAPIView):
    serializer_class = BasicCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Get the list of Categories
        original_request = super().get(request, *args, **kwargs)

        # Create a subcategory list from the resonse
        sub_list_category = []
        for i in original_request.data:
            if i['parent_category_id'] is not None:
                sub_list_category.append(i)

        # Create a parent category list from the resonse
        parent_list_category = []
        for i in original_request.data:
            if i['parent_category_id'] is None:
                parent_list_category.append(i)

        # Add a sub category list field in the dictionary
        for category in parent_list_category:
            category['sub_category_list'] = []

        # Loop through both lists and compare the parent id with the category id
        # Then append the subcategory list field
        for parent_category in parent_list_category:
            for sub_category in sub_list_category:
                if sub_category['parent_category_id'] == parent_category['id']:
                    parent_category['sub_category_list'].append(
                        {
                            'category_name': sub_category['category_name'],
                            'category_toggle_star': sub_category['category_toggle_star']
                        }
                    )

        # copy the new list into the request.data
        original_request.data = parent_list_category
        return original_request

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class ToggleStarCategoryView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        print(request.data)

        if not self.get_queryset().filter(category_name=kwargs['categoryName']).exists():
            return Response({
                "Description": "Category does not exist"
            })

        # Get the current value of that star
        star_value = self.get_queryset().filter(category_name=kwargs['categoryName']).get().category_toggle_star

        # Update the star value to be the opposite of the current star value (not star_value)
        self.get_queryset().filter(category_name=kwargs['categoryName']).update(
            category_toggle_star=not star_value)
        return Response({
            "Description": "Updated Succesfully"
        })

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)


class DeleteAndToggleStarCategoryView(ToggleStarCategoryView, DeleteCategoryView):
    """
    This Class is only for using the same url to do both PUT and DELETE request methods with the same url
    """
    pass


class AddAndListCategoryView(AddCategoryView, ListCategoriesAndSubCategoriesView):
    """
    This Class is only for using the same url to do both GET and POST request methods with the same url
    """
    pass
