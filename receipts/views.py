import datetime

import imgkit
import django_filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from merchant.models import Merchant
from users.models import UserProfile
from .models import Receipts
from .serializers import ManualReceiptsSerializer, ReceiptsSerializer, PutPatchReceiptsSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.paginator import Paginator
from rest_framework.status import HTTP_200_OK
from django.core.files.images import ImageFile


class PostReceiptsAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)


class PostManualReceiptsAPIView(generics.CreateAPIView):
    """This view is only for Posting new receipts"""
    permission_classes = [IsAuthenticated]
    serializer_class = ManualReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)


class ReceiptsFilter(django_filters.FilterSet):
    merchant_name = django_filters.CharFilter(field_name='merchant__name', lookup_expr='icontains')
    scan_date_start = django_filters.DateTimeFilter(field_name='scan_date', lookup_expr='gte')
    scan_date_end = django_filters.DateTimeFilter(field_name='scan_date', lookup_expr='lte')

    class Meta:
        model = Receipts
        fields = ['id', 'scan_date_start', 'scan_date_end', 'user_id',
                  'merchant_name', 'coupon', 'location', 'total', 'tax', 'tip', 'currency']


class DefaultReceiptPaginationAPIListView(generics.ListAPIView):
    """
    This view returns a list of all the receipts for the user.

    It also accepts optional query parameters to filter, order and search the receipts.
    examples:
    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?search=starbucks'
    This will return all the receipts where the merchant name contains 'starbucks'.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?ordering=total,tip'
    This will return all the receipts for all users, and order them by total and then tip in ASCENDING order.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?tip=1&ordering=-total'
    This will return all the receipts for tip=1, and order them by total in DESCENDING(notice the '-') order.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?tax=1&merchant_name=starbucks&ordering=scan_date&search=montreal'
    This will return all the receipts for tax=1, where the merchant name contains 'starbucks',ordered by
    scan_date, and anything containing the text 'montreal'. All the query parameters are optional, and can be used
    together or separately.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?search=mcdonalds'
    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?merchant_name=mcdonalds'
    These two urls are somewhat equivalent, as they will both return all the receipts where the merchant name in the
    merchant field of the table contains 'mcdonalds'.
    The difference is that the first url will search for and include any receipt with a field containing the text
    'mcdonalds'.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?scan_date_start=2020-01-01'
    This will return all the receipts where the scan_date is greater than or equal to 2020-01-01.

    url = 'api/receipts/pageNumber=<pageNumber>&pageSize=<pageSize>/?scan_date_start=2020-01-01&scan_date_end=2020-01-31'
    This will return all the receipts with the scan_date between the scan_date_start and scan_date_end (inclusive).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReceiptsSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReceiptsFilter
    ordering_fields = '__all__'
    search_fields = ['scan_date', 'coupon', 'merchant__name', 'location', 'total', 'tax', 'tip', 'currency']

    def get(self, request, *args, **kwargs):
        """
        Get the response from the super class which returns the entire list
        and then paginate the results
        """
        #
        reciept_list_response = super().get(request, *args, **kwargs)
        new_reciept_list_response = []
        for item in reciept_list_response.data:
            item['merchant'] = Merchant.objects.get(pk=item['merchant']).name
            new_reciept_list_response.append(item)
        # Try to turn page number to an int value, otherwise make sure the response returns an empty list
        try:
            kwargs['pageNumber'] = int(kwargs['pageNumber'])
        except Exception:
            return Response({
                'page_list': [],
                'total': 0,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

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

        # If page number is greater than page limit, return an empty list
        if kwargs['pageNumber'] > paginator.num_pages:
            return Response({
                'page_list': [],
                'total': 0,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        # If page number is less than 1, return an empty list
        if kwargs['pageNumber'] <= 0:
            return Response({
                'page_list': [],
                'total': 0,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        page = paginator.page(kwargs['pageNumber'])

        return Response({
            'page_list': page.object_list,
            'total': len(page.object_list),
            'description': str(page),
            'current_page_number': page.number,
            'number_of_pages': page.paginator.num_pages
        }, status=HTTP_200_OK)

    def get_queryset(self):
        return Receipts.objects.filter(user=self.request.user)


class DetailReceiptsAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchReceiptsSerializer
    lookup_url_kwarg = 'receipt_id'

    # Ensure user can only delete their own receipts
    def get_queryset(self):
        return Receipts.objects.filter(user=self.request.user)


class ParseReceiptsAPIView(APIView):
    """
    any email to budgetlens.tech will be sent to this api
    """
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, *args, **kwargs):
        # check if it is a valid forwarding email
        try:
            email = request.POST.get('To').strip()
            userProfile = UserProfile.objects.get(forwardingEmail=email)
        except:
            return Response({"response": "This email does not correspond to any Budget Lens account"},
                            status=status.HTTP_400_BAD_REQUEST)
        """ email converted to image"""

        filename = str(email + str(datetime.datetime.now()) + '.jpg')
        imgkit.from_string(str(request.POST.get('Html')), filename,
                           options={"enable-local-file-access": ""})

        """
        to test locally send email in format of the default payload in
        https://docs.sendgrid.com/for-developers/parsing-email/setting-up-the-inbound-parse-webhook 
        and change the "TO" field to the forwarding email of the user you want to test with
        """

        receipt_image = ImageFile(open(filename, 'rb'), name=filename)

        data = {'receipt_image': receipt_image, 'user': userProfile.user}

        receipt_serializer = ReceiptsSerializer(context={'request': request}, data=data)

        if receipt_serializer.is_valid(raise_exception=True):
            receipt_serializer.save()
            return Response(receipt_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(receipt_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
