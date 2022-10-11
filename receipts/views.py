import os
import pdb
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from budget_lens_backend import settings
from .models import Receipts, upload_to
from .serializers import ReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class AddReceiptsAPI(APIView):
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        # print(request.data)
        # pdb.set_trace()
        Receipts.objects.create(user=request.user, receipt_image=request.data['receipt_image'])

        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)
        return Response(serializer.data)

    def get(self, request):
        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)
        return Response({
            'details': "hello",
            'message': serializer.data,
        }, status=200)
