from django.shortcuts import render
from rest_framework import filters, generics
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from item.serializers import ItemSerializer, PutPatchItemSerializer

from .models import Item

class AddItemAPI(generics.CreateAPIView):
    """ Adds item to a receipt for a user """
    serializer_class = ItemSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        
        return Response({
            "receipt_id": item.receipt_id,
            "tax": item.tax,
            "name": item.name,
            "price": item.price,
            "important_dates": item.important_dates,
        })

class GetItemsAPI(generics.ListCreateAPIView):
    """ Gets list of items for a user """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ItemSerializer(queryset, many=True)
        return Response(serializer.data)

    
class ItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ details for an item """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer
    lookup_url_kwarg = 'item_id'

    # Check: User can only delete their own items
    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)