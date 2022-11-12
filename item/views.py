from django.shortcuts import render
from item.serializers import ItemSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

class AddItemAPI():
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    parser_classes = (MultiPartParser, FormParser)

class deleteItemAPI():
    pass

class updateItemAPI():
    pass

class listItemAPI():
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    parser_classes = (MultiPartParser, FormParser)