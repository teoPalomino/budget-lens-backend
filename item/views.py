from django.shortcuts import render
from rest_framework import filters, generics
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from item.serializers import ItemSerializer, PutPatchItemSerializer
from receipts.models import Receipts

from .models import Item


class AddItemAPI(generics.CreateAPIView):
    """ Adds item to a receipt for a user """
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()

        if Receipts.objects.filter(id=request.data["receipt_id"]).exists():
            return Response({
                "receipt_id": item.receipt_id,
                "tax": item.tax,
                "name": item.name,
                "price": item.price,
                "important_dates": item.important_dates,
            },  status=HTTP_200_OK)
        return Response({
            "Error": "Receipt does not exist"
        })


class GetItemsAPI(generics.ListCreateAPIView):
    """ Gets list of items for a user """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

class ItemDetailAPIView(generics.ListAPIView):
    """ details for an item """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer
    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            return self.get_queryset().filter(item_id = kwargs.get('item_id'))
        return Response({
            "Response":"No item_id specified"
        },  status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            item = Item.objects.filter(id=kwargs.get('item_id'))
            if item.exists():
                serializer = ItemSerializer(item, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({
                "Error": "Item does not exist"
            }, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)


class DeleteItemAPI(generics.DestroyAPIView):
    """ Deletes an item """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            item = Item.objects.filter(id=kwargs.get('item_id'))
            if item.exists():
                item.delete()
                return Response({"response": "Item deleted successfully"}, status=HTTP_200_OK)
            else:
                return Response({"response": "Item not found"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": "Item ID not specified"}, status=HTTP_400_BAD_REQUEST)
