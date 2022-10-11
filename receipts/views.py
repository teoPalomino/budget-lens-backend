import os
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from budget_lens_backend import settings
from .models import Receipts, upload_to
from .serializers import ReceiptsSerializer


class AddReceiptsAPI(APIView):
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        for filename in os.listdir(settings.RECEIPT_IMAGES_ROOT):
            if filename or filename.endswith(".png") or filename.endswith(".jpeg"):
                Receipts.objects.create(user=request.user, receipt_image_url=upload_to(filename, request.user))

        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)
        return Response(serializer.data, status=200)

    def get(self, request):
        serializer = ReceiptsSerializer(Receipts.objects.filter(user=request.user), many=True)
        return Response(serializer.data, status=200)
