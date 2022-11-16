# from django.shortcuts import render
import pdb
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from item.models import Item

from .models import Category
from .serializers import BasicCategorySerializer, ToggleStarCategorySerializer


# Create your views here.


class AddCategoryView(generics.GenericAPIView):
    """API for adding a new category"""
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


# class AddSubCategoryView(generics.GenericAPIView):
#     """API for adding a new subcategory"""
#     queryset = SubCategory.objects.all()
#     permission_classes = (IsAuthenticated,)
#     serializer_class = BasicSubCategorySerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         sub_category = serializer.save()

#         return Response({
#             "sub_category_name": sub_category.sub_category_name,
#             "sub_category_toggle_star": sub_category.sub_category_toggle_star,
#         })

#     def get_queryset(self):
#         return SubCategory.objects.filter(user=self.request.user)

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
        list_category = super().get(request, *args, **kwargs)
        parent_category_list = list_category

        # for category in list_category.data:
        #     if category['parent_category_id'] == None:
        #         parent_category_list.data.remove(category)

        # Add a sub category list field in the dictionary
        for category in parent_category_list.data:
            category['sub_category_list'] = []

        # Loop through all the categories and subcategories
        for count, category in enumerate(self.get_queryset()):
            for sub_category in self.get_queryset().filter(parent_category_id=not None):
                # If the parent category id in the sub category matches the category id
                if int(sub_category.parent_category_id) == int(category.pk):
                    # append that sub category to the category as a dictionary
                    parent_category_list.data[count]['sub_category_list'].append(
                        {
                            'sub_category_name': sub_category.sub_category_name,
                            'sub_category_toggle_star': sub_category.sub_category_toggle_star
                        }
                    )
        return parent_category_list

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    # def get(self, request, *args, **kwargs):
    #     # Get the list of parent and child categories (sub categories)
    #     parent_categories = self.get_queryset().filter(parent_category_id=None)
    #     sub_categories = self.get_queryset().filter(parent_category_id=not None)

    #     pdb.set_trace()
    #     return Response({
    #         "parent_categories": str(parent_categories),
    #         "sub_categories": str(sub_categories)
    #     })
        

    # def get_queryset(self):
    #     return Category.objects.filter(user=self.request.user)

# class DeleteSubCategoryView(generics.DestroyAPIView):
#     """API for registering a new user"""
#     serializer_class = BasicCategorySerializer
#     permission_classes = (IsAuthenticated,)

#     def delete(self, request, *args, **kwargs):
#         print(kwargs["CategoryName"])
#         try:
#             category = Category.objects.get(user=self.request.user, sub_category_name=kwargs['CategoryName'])
#         except Exception:
#             return Response({
#                 "Description": "SubCategory does not exist"
#             })
#         if Item.objects.filter(category_id=category.id).exists():
#             return Response({
#                 "Description": "Cannot delete SubCategory, items exists in this subcategory"
#             })

#         Category.objects.filter(user=self.request.user, sub_category_name=kwargs['subCategoryName']).delete()
#         return Response({
#             "Description": 'SubCategory succesfully deleted'
#         })

#     def get_queryset(self):
#         return Category.objects.filter(user=self.request.user, parent_category_id=not None)


# class ListCategoriesAndSubCategoriesView(generics.ListAPIView):
#     serializer_class = BasicCategorySerializer
#     permission_classes = (IsAuthenticated,)

#     def get(self, request, *args, **kwargs):
#         # Get the list of Categories
#         list_category = super().get(request, *args, **kwargs)

#         # Add a sub category list field in the dictionary
#         for category in list_category.data:
#             category['sub_category_list'] = []

#         # Loop through all the categories and subcategories
#         for count, category in enumerate(self.get_queryset()):
#             for sub_category in SubCategory.objects.filter(user=self.request.user):
#                 # If the parent category id in the sub category matches the category id
#                 if int(sub_category.parent_category.id) == int(category.pk):
#                     # append that sub category to the category as a dictionary
#                     list_category.data[count]['sub_category_list'].append(
#                         {
#                             'sub_category_name': sub_category.sub_category_name,
#                             'sub_category_toggle_star': sub_category.sub_category_toggle_star
#                         }
#                     )
#         return list_category

#     def get_queryset(self):
#         return Category.objects.filter(user=self.request.user)


class ToggleStarCategoryView(generics.UpdateAPIView):
    serializer_class = ToggleStarCategorySerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        print(request.data)

        if not self.get_queryset().filter(category_name=kwargs['categoryName']).exists():
            return Response({
                "Description": "Category does not exist"
            })

        self.get_queryset().filter(category_name=kwargs['categoryName']).update(
            category_toggle_star=self.request.data['category_toggle_star'])
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
    This Class is only for using the same url to do both PUT and DELETE request methods with the same url
    """
    pass


# class ToggleStarSubCategoryView(generics.UpdateAPIView):
#     serializer_class = ToggleStarSubCategorySerializer
#     permission_classes = (IsAuthenticated,)

#     def update(self, request, *args, **kwargs):
#         print(request.data)
#         # if SubCategory.objects.filter(sub_category_name=kwargs['subCategoryName'], user=self.request.user)
#         if not self.get_queryset().filter(sub_category_name=kwargs['subCategoryName']).exists():
#             return Response({
#                 "Description": "SubCategory does not exist"
#             })

#         self.get_queryset().filter(sub_category_name=kwargs['subCategoryName']).update(
#             sub_category_toggle_star=self.request.data['sub_category_toggle_star'])
#         return Response({
#             "Description": "Updated Succesfully"
#         })

#     def get_queryset(self):
#         return SubCategory.objects.filter(user=self.request.user)


# class DeleteAndToggleStarSubCategoryView(ToggleStarSubCategoryView, DeleteSubCategoryView):
#     """
#     This Class is only for using the same url to do both PUT and DELETE request methods with the same url
#     """
#     pass


# class GetCategoryCostsView(generics.ListAPIView):
#     serializer_class = BasicCategorySerializer
#     permission_classes = (IsAuthenticated,)

#     """ TODO: add tax to the total once proper item model is added """
#     def get(self, request, *args, **kwargs):
#         # Get the list of Items
#         """ TODO: filter by the user's item (i suggest having a user field in the item model) """
#         items = Item.objects.all()
#         category_costs_dict = {}

#         if items.exists():
#             for item in items:
#                 if item.category_id.get_category_name() in category_costs_dict:
#                     category_costs_dict[item.category_id.get_category_name()] += item.price
#                 else:
#                     category_costs_dict[item.category_id.get_category_name()] = item.price
#             return Response(category_costs_dict, HTTP_200_OK)

#         return Response({"Response": "The user either has no items created or something went wrong"},
#                         HTTP_400_BAD_REQUEST)

#     def get_queryset(self):
#         return Item.objects.filter(user=self.request.user)
