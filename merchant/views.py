from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from .models import Merchant
from .serializers import MerchantSerializer


class AddAndListMerchantView(generics.ListCreateAPIView):
    serializer_class = MerchantSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        merchant = serializer.save()

        return Response({
            "name": merchant.name,
        }, status=HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        merchants = self.get_queryset()

        return Response({
            "merchants": MerchantSerializer(merchants, many=True).data
        }, status=HTTP_200_OK)

    def get_queryset(self):
        return Merchant.objects.all()
