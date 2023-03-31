import datetime
import django_filters
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.core.paginator import Paginator

from item.serializers import ItemSerializer, PutPatchItemSerializer
from receipts.models import Receipts
from rules.models import Rule

from .models import Item


class AddItemAPI(generics.CreateAPIView):
    """ Adds item to a receipt for a user """
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if Receipts.objects.filter(id=request.data["receipt"]).exists():

            # if there's a rule that matches the item name, assign the rule category to the category of the item
            rules = Rule.objects.filter(user=self.request.user)
            if rules.exists():
                for rule in rules:
                    if rule.regex == serializer.validated_data['name']:
                        serializer.validated_data['category_id'] = rule.category
                        break

            item = serializer.save()
            return Response({
                "user": item.user.id,
                "receipt": item.receipt.id,
                "name": item.name,
                "category_id": item.category_id.id if item.category_id is not None else item.category_id,
                "price": item.price
            }, status=HTTP_200_OK)
        return Response({
            "Error": "Receipt does not exist"
        }, HTTP_400_BAD_REQUEST)


class ItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ details for an item """

    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchItemSerializer
    lookup_url_kwarg = 'item_id'

    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            try:
                item = self.get_queryset().get(id=kwargs.get('item_id'))

                response = [{'id': item.id,
                             'user': User.objects.get(id=item.user.id).first_name,
                             'name': item.name,
                             'price': item.price,
                             'receipt': item.receipt.id,
                             'merchant_name': item.receipt.merchant.name,
                             'scan_date': item.receipt.scan_date,
                             'category_id': item.category_id.id,
                             'category_name': item.category_id.category_name,
                             'parent_category_id': item.category_id.parent_category_id}]

                return Response(response, status=HTTP_200_OK)

            except Item.DoesNotExist:
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
                item_costs_dict[item.id] = {'item': [item.user.id, item.name, item.price],
                                            'receipt_details': [item.receipt.id, item.receipt.merchant.name,
                                                                item.receipt.scan_date],
                                            'category_details': [item.category_id.category_name,
                                                                 item.category_id.parent_category_id] if item.category_id is not None else "Empty"}
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
    start_date = django_filters.DateFilter(field_name="receipt__scan_date", lookup_expr='gte')
    end_date = django_filters.DateFilter(field_name="receipt__scan_date", lookup_expr='lte')
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    merchant_name = django_filters.CharFilter(field_name="receipt__merchant__name", lookup_expr='icontains')
    merchant_id = django_filters.CharFilter(field_name="receipt__merchant__id", lookup_expr='exact')

    class Meta:
        model = Item
        fields = ['id', 'receipt', 'category_id', 'category_id_id__category_name', 'name', 'price', 'min_price', 'max_price',
                  'start_date', 'end_date', 'user', 'merchant_name', 'merchant_id']


class PaginateFilterItemsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ItemFilter
    ordering_fields = '__all__'
    search_fields = ['name', 'price', 'user__first_name', 'user__last_name', 'category_id_id__category_name']

    # noqa: C901
    def get(self, request, *args, **kwargs):
        """
        Get the response from the super class which returns the entire list
        and then paginate the results
        """
        queryset = self.get_queryset()
        item_list_response = super().get(request, *args, **kwargs)
        item_total_price = 0

        # Try to turn page number to an int value, otherwise make sure the response returns an empty list
        try:
            kwargs['pageNumber'] = int(kwargs['pageNumber'])
        except Exception:
            return Response({
                'page_list': [],
                'total': 0,
                'total_price': item_total_price,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        # Try to turn page size to an int value, otherwise set to default value of 10
        try:
            kwargs['pageSize'] = int(kwargs['pageSize'])
        except Exception:
            kwargs['pageSize'] = 10

        # If Page size is less than zero, -> had to remove due to complexity issue.
        # If Page size is less than zero
        if kwargs['pageSize'] <= 0:
            # Make default page size = 10
            kwargs['pageSize'] = 10

        paginator = Paginator(item_list_response.data, kwargs['pageSize'])

        # If page number is greater than page limit, return an empty list
        if kwargs['pageNumber'] > paginator.num_pages:
            return Response({
                'page_list': [],
                'total': 0,
                'total_price': item_total_price,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        # If page number is less than 1, return an empty list
        if kwargs['pageNumber'] <= 0:
            return Response({
                'page_list': [],
                'total': 0,
                'total_price': item_total_price,
                'description': "Invalid Page Number"
            }, status=HTTP_200_OK)

        page = paginator.page(kwargs['pageNumber'])

        # Append the scan date from the receipt into the page item in question
        for i, item in zip(queryset, page.object_list):
            item['scan_date'] = i.receipt.scan_date
            item['merchant_name'] = i.receipt.merchant.name
            item_total_price += float(item['price'])
            if i.category_id is not None:
                item['category_name'] = i.category_id.category_name
            else:
                item['category_name'] = ""

        item_total_price = round(item_total_price, 2)
        return Response({
            'page_list': page.object_list,
            'total': len(page.object_list),
            'total_price': item_total_price,
            'description': str(page),
            'current_page_number': page.number,
            'number_of_pages': page.paginator.num_pages
        }, status=HTTP_200_OK)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)


class GetCategoryCostsView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Get the list of Items
        items = self.get_queryset()
        category_costs_dict = {}
        category_costs_list = []

        if items.exists():
            for item in items:
                if item.category_id.get_category_name() in category_costs_dict:
                    category_costs_dict[item.category_id.get_category_name()] += item.price
                else:
                    category_costs_dict[item.category_id.get_category_name()] = item.price
        else:
            return Response({"Response": "The user either has no items created or something went wrong"},
                            HTTP_400_BAD_REQUEST)

        for key, value in category_costs_dict.items():
            category_costs_list.append({
                "category_name": key,
                "category_cost": value
            })
        return Response({"Costs": category_costs_list}, status=HTTP_200_OK)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)


class GetItemFrequencyByMonthView(ItemDetailAPIView):
    """
    This view is used to get the frequency of a specific item by an interval of one previous month in history using its name.
    It returns a dictionary with the key being the item name and the value being the frequency of the item throughout all
    receipts of that given user.

    The route used by this view is `items/<int:item_id>/date/` where `item_id` is the id of the item in question.
    """

    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            try:
                item = self.get_queryset().get(id=kwargs.get('item_id'))

                # Additional query to get all the items that have the same name as the item in question
                items = Item.objects.filter(name=item.name, user=self.request.user)
                item_frequency_dict = {}

                if items.exists():
                    for item in items:
                        # Find the receipt in which this item belongs to. This receipt contains
                        # the date details of all the items and hence the receipt itself
                        if (datetime.date.today().month == 3 and datetime.date.today().day == 29)\
                                or (datetime.date.today().month == 3 and datetime.date.today().day == 30)\
                                or (datetime.date.today().month == 3 and datetime.date.today().day == 31):
                            date_range = datetime.date.today().replace(month=datetime.date.today().month - 1, day=28)
                        else:
                            date_range = datetime.date.today().replace(month=datetime.date.today().month - 1)

                        # If the date of the receipt is within the date range,
                        # then add the item/change its existing frequency found in
                        # all receipts of the given user
                        if date_range <= item.receipt.scan_date.date() <= datetime.date.today():
                            if item.name in item_frequency_dict:
                                item_frequency_dict[item.name] = {
                                    'item_frequency': item_frequency_dict[item.name]['item_frequency'] + 1
                                }
                            else:
                                item_frequency_dict[item.name] = {
                                    'item_frequency': 1
                                }

                    if not item_frequency_dict:
                        return Response({"This item was not bought in the last month"},
                                        status=HTTP_200_OK)
                    else:
                        return Response(item_frequency_dict, status=HTTP_200_OK)

            except Item.DoesNotExist:
                return Response({"Error": "Item with this id does not exist"},
                                status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)


class GetCategoryCostAndFrequencyByDateAndStarredCategoryView(GetCategoryCostsView):
    """
    This View is essentially the same class as GetCategoryCost, but it compares the date
    and if the category is starred.

    *   route is `items/category/costs/date/days=<int:days>/` where `days` is the range from
        when the scan_date can be from today's date till today's date minus `days` in the api route.
    """

    def get(self, request, *args, **kwargs):
        items = self.get_queryset()
        category_costs_frequency_dict = {}

        if items.exists():
            for item in items:
                # Find the receipt in which this item belongs to
                #  The receipt contains the date details of all the items and hence the receipt itself
                #  item.receipt.scan_date
                date_range = datetime.date.today() - datetime.timedelta(days=kwargs['days'])

                # If the date of the receipt is within the date range and the category is stared,
                #  then add the category/change the price of the category.
                if item.receipt.scan_date.date() >= date_range and item.category_id.category_toggle_star:

                    if item.category_id.get_category_name() in category_costs_frequency_dict:
                        category_costs_frequency_dict[item.category_id.get_category_name()] = {
                            'price': category_costs_frequency_dict[item.category_id.get_category_name()][
                                         'price'] + item.price,
                            'category_frequency': category_costs_frequency_dict[item.category_id.get_category_name()][
                                                      'category_frequency'] + 1
                        }

                    else:
                        category_costs_frequency_dict[item.category_id.get_category_name()] = {
                            'price': item.price,
                            'category_frequency': 1
                        }
        else:
            return Response({"Response": "The user either has no items created or something went wrong"},
                            HTTP_400_BAD_REQUEST)

        return Response(category_costs_frequency_dict, status=HTTP_200_OK)
