import django_filters
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Receipts
from .serializers import ReceiptsSerializer, PutPatchReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from rest_framework.status import HTTP_200_OK
from django_filters.rest_framework import DjangoFilterBackend


class ReceiptsFilter(django_filters.FilterSet):
    merchant_name = django_filters.CharFilter(field_name='merchant__name', lookup_expr='icontains')

    class Meta:
        model = Receipts
        fields = ['id', 'scan_date', 'user_id', 'merchant_name', 'coupon', 'location', 'total', 'tax', 'tip']


class ReceiptsAPIView(generics.ListCreateAPIView):
    """
    This view returns a list of all the receipts for the user.

    It also accepts optional query parameters to filter, order and search the receipts.
    examples:
    url = '/api/receipts/?search=starbucks'
    This will return all the receipts where the merchant name contains 'starbucks'.

    url = '/api/receipts/?ordering=total,tip'
    This will return all the receipts for all users, and order them by total and then tip in ASCENDING order.

    url = '/api/receipts/?tip=1&ordering=-total'
    This will return all the receipts for tip=1, and order them by total in DESCENDING(notice the '-') order.

    url = '/api/receipts/?tax=1&merchant_name=starbucks&ordering=scan_date&search=montreal'
    This will return all the receipts for tax=1, where the merchant name contains 'starbucks',ordered by
    scan_date, and anything containing the text 'montreal'. All the query parameters are optional, and can be used
    together or separately.

    url = '/api/receipts/?search=mcdonalds'
    url = '/api/receipts/?merchant_name=mcdonalds'
    These two urls are somewhat equivalent, as they will both return all the receipts where the merchant name in the
    merchant field of the table contains 'mcdonalds'.
    The difference is that the first url will search all the fields for the text 'mcdonalds' and will return an entry
    with any field containing the text 'mcdonalds'.
    """
    permission_classes = [IsAuthenticated]
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # should I only include certain fields to search, ordering and filter? currently supports all
    filterset_class = ReceiptsFilter
    ordering_fields = '__all__'
    search_fields = ['scan_date', 'coupon', 'merchant__name', 'location', 'total', 'tax', 'tip']


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
