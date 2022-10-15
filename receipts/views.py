from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Receipts
from .serializers import ReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser

# Initial Plan:
#   make a user folder with the user_id as the name
#   make a sub-folder inside that specific user's folder with the receipt_id as the name
#   save the image inside the folder of the user's receipt with the current unix timestamp scan_date as the image file name


class ReceiptsAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)


class DetailReceiptsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    lookup_url_kwarg = 'receipt_id'
