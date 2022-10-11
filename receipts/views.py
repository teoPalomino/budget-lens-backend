from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Receipts, upload_to
from .serializers import ReceiptsSerializer


class AddReceiptsAPI(APIView):
    serializer_class = ReceiptsSerializer

    def post(self, request):
        user_token = Token.objects.get(user=request.user)
        user = user_token.user
        serializer = ReceiptsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        receipts = Receipts.objects.all()
        print(receipts)
        serializer = ReceiptsSerializer(receipts, many=True)
        return Response(serializer.data)
