import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.core.paginator import Paginator

from item.serializers import ItemSerializer, PutPatchItemSerializer
from receipts.models import Receipts

from .models import Item


class AddItemAPI(generics.CreateAPIView):
    """ Adds item to a receipt for a user """
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        if Receipts.objects.filter(id=request.data["receipt"]).exists():
            return Response({
                "user": item.user.id,
                "receipt": item.receipt.id,
                "name": item.name,
                "category_id": item.category_id.id if item.category_id is not None else item.category_id,
                "price": item.price,
                "important_dates": item.important_dates,
            },  status=HTTP_200_OK)
        return Response({
            "Error": "Receipt does not exist"
        }, HTTP_400_BAD_REQUEST)


class ItemDetailAPIView(generics.ListAPIView):

    """ details for an item """

    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            item = self.get_queryset().filter(id=kwargs.get('item_id'))
            if item.exists():
                serializer = ItemSerializer(item, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({
                "Error": "Item does not exist"
            }, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)


class DeleteItemAPI(generics.DestroyAPIView):
    """ Deletes an item """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer
    lookup_url_kwarg = 'item_id'

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            item = self.get_queryset().filter(id=kwargs.get('item_id'))
            if item.exists():
                item.delete()
                return Response({"response": "Item deleted successfully"}, status=HTTP_200_OK)
            else:
                return Response({"response": "Item not found"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"response": "Item ID not specified"}, status=HTTP_400_BAD_REQUEST)


class GetItemsAPI(generics.ListAPIView):
    """
    Gets list of items and the total cost of all items
    """
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        items = Item.objects.filter(user=self.request.user)
        item_costs_dict = {}
        item_total_cost = 0

        if items.exists():
            for item in items:
                item_costs_dict[item.id] = {'item': [item.user.id, item.name, item.price, item.important_dates],
                                            'receipt_details': [item.receipt.id, item.receipt.merchant.name, item.receipt.scan_date],
                                            'category_details': [item.category_id.category_name, item.category_id.parent_category_id] if item.category_id is not None else "Empty"}
                item_total_cost += item.price
            return Response({
                "totalPrice": item_total_cost,
                "items": item_costs_dict,
                }, HTTP_200_OK)
        else:
            return Response({
                "totalPrice": 0,
                "items": item_costs_dict,
                }, HTTP_200_OK)


class ItemFilter(django_filters.FilterSet):

    class Meta:
        model = Item
        fields = ['id', 'receipt', 'category_id', 'name', 'price', 'important_dates', 'user']


class PaginateFilterItemsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    ordering_fields = '__all__'
    search_fields = ['receipt', 'category_id', 'name', 'price', 'important_dates', 'user']
    queryset = Item.objects.all()

    # noqa: C901
    def list(self, request, *args, **kwargs):
        """
        Get the resonse from the super class which returns the entire list
        and then paginate the results
        """
        queryset = self.get_queryset()
        serializer = ItemSerializer(queryset, many=True)
        item_list_response = serializer.data
        item_total_cost = 0

        if queryset.exists():
            for item in queryset:
                item_total_cost += item.price

        # Try to turn page number to an int value, otherwise make sure the response returns an empty list
        try:
            kwargs['pageNumber'] = int(kwargs['pageNumber'])
        except Exception:
            return Response({
                'page_list': [],
                'total': 0,
                'total Cost': item_total_cost,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        # Try to turn page size to an int value, otherwise set to default value of 10
        try:
            kwargs['pageSize'] = int(kwargs['pageSize'])
        except Exception:
            kwargs['pageSize'] = 10

        # If Page size is less than zero, -> had to remove due to complexity issue.
        paginator = Paginator(item_list_response, kwargs['pageSize'])

        # If page number is greater than page limit, return an empty list
        if kwargs['pageNumber'] > paginator.num_pages:
            return Response({
                'page_list': [],
                'total': 0,
                'total Cost': item_total_cost,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        # If page number is less than 1, return an empty list
        if kwargs['pageNumber'] <= 0:
            return Response({
                'page_list': [],
                'total': 0,
                'total Cost': item_total_cost,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        page = paginator.page(kwargs['pageNumber'])

        # Append the scan date from the receipt into the page item in question
        for i, item in zip(queryset, page.object_list):
            item['scan_date'] = i.receipt.scan_date

        return Response({
            'page_list': page.object_list,
            'total': len(page.object_list),
            'total Cost': item_total_cost,
            'description': str(page),
            'current_page_number': page.number,
            'number_of_pages': page.paginator.num_pages
        }, status=HTTP_200_OK)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)
