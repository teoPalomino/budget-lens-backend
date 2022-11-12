from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response

from .models import Item
from .serializers import ItemSerializer


# Create your views here.
class ItemView(generics.GenericAPIView):
    """API for registering a new user"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        return Response({
            "name": item.name,
            "price": item.price,
            "receipt_id": str(item.receipt_id),
            "category_id": str(item.category_id),
            "sub_category_id": str(item.sub_category_id)
        })