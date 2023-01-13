import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.core.paginator import Paginator

from .serializers import ItemSplitSerializer

from .models import ItemSplit

class AddItemSplitAPI(generics.CreateAPIView):
    """ Adds item to a receipt for a user """
    serializer_class = ItemSplitSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)