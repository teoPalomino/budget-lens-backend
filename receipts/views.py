from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Receipts
from .serializers import ReceiptsSerializer, PutPatchReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from rest_framework.status import HTTP_200_OK


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

        # Try to turn page number to an int value, otherwise set to default value of 1
        try:
            kwargs['pageNumber'] = int(kwargs['pageNumber'])
        except Exception:
            kwargs['pageNumber'] = 1

        # Try to turn page size to an int value, otherwise set to default value of 10
        try:
            kwargs['pageSize'] = int(kwargs['pageSize'])
        except Exception:
            kwargs['pageSize'] = 10

        # If Page size is less than zero
        if (kwargs['pageSize'] <= 0):
            # Make default page size = 10
            kwargs['pageSize'] = 10

        paginator = Paginator(reciept_list_response.data, kwargs['pageSize'])

        # If page number is greater than page limit, set it to the last page
        if kwargs['pageNumber'] > paginator.num_pages:
            kwargs['pageNumber'] = paginator.num_pages

        # If page number is less than 1, set it to the first page
        if kwargs['pageNumber'] <= 0:
            kwargs['pageNumber'] = 1

        page = paginator.page(kwargs['pageNumber'])

        return Response({
            'page_list': page.object_list,
            'description': str(page)
        }, status=HTTP_200_OK)


class DetailReceiptsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = PutPatchReceiptsSerializer
    lookup_url_kwarg = 'receipt_id'
