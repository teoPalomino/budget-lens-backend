from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Receipts
from .serializers import ReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST


# Initial Plan:
#   make a user folder with the user_id as the name
#   make a sub-folder inside that specific user's folder with the receipt_id as the name
#   save the image inside the folder of the user's receipt with the current unix timestamp scan_date as the image file name


class ReceiptsAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)


class DefaultReceiptPaginationAPIListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        """
        Get the resonse from the super class which returns the entire list
        and then paginate the results
        """
        #
        reciept_list_response = super().get(request, *args, **kwargs)

        # If Page size is less than zero
        if (kwargs['pageSize'] <= 0):
            return Response({
                'description': 'Page Size cannot be less than zero'
            }, status=HTTP_400_BAD_REQUEST)

        paginator = Paginator(reciept_list_response.data, kwargs['pageSize'])

        # If page number is not in range of number of pages
        if kwargs['pageNumber'] > paginator.num_pages or kwargs['pageNumber'] <= 0:
            return Response({
                'description': 'Page Number is out of range or is less than zero'
            }, status=HTTP_400_BAD_REQUEST)

        page = paginator.page(kwargs['pageNumber'])

        return Response({
            'page_list': page.object_list,
            'description': str(page)
        }, status=HTTP_200_OK)


class DetailReceiptsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    lookup_url_kwarg = 'receipt_id'
