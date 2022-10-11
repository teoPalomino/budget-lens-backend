from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Receipts
from .serializers import ReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser

# make a user folder with the user_id as the name
# make a sub folder inside that specific user's folder with the receipt_id as the name
# save the image inside the folder of the user's receipt with the current unix timestamp scan_date as the image file name


class AddReceiptsAPI(APIView):
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        Receipts.objects.create(user=request.user, receipt_image=request.data['receipt_image'])

        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)

        return Response({
            'receipt image URL links': serializer.data,
            'status': 'success'})

    def get(self, request):
        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)

        return Response({
            'receipt image URL links': serializer.data,
            'status': 'success'})
