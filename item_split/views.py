from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from item.models import Item


from .serializers import ItemSplitSerializer

from .models import ItemSplit

from users.models import User

from rest_framework.decorators import api_view, permission_classes

from django.contrib.auth.models import User as DjangoBaseUser


class AddItemSplitAPI(generics.ListCreateAPIView):
    """
    Adds item to a receipt for a user
    The list of shared user IDs are a string that represents the list of user IDs (List of integers).
    Therefore the list must be separated by commas.
    """
    serializer_class = ItemSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemSplit.objects.all()

    def post(self, request, *args, **kwargs):
        item_splits_data = request.data.get('item_list')
        print(request.data)
        responses = []

        for item_data in item_splits_data:
            try:
                print(37)
                user_ids_list = list(map(int, item_data['shared_user_ids'].split(',')))
            except Exception:
                print(40)
                return Response({"message": "Invalid list of user IDs. Please enter numbers separated by commas."},
                                status=HTTP_400_BAD_REQUEST)

            user_ids_list_as_set = set(user_ids_list)
            print(45)
            if len(user_ids_list_as_set) != len(user_ids_list):
                print(47)
                return Response({"message": "List of user IDs contains duplicates."},
                                status=HTTP_400_BAD_REQUEST)

            for user_id in user_ids_list:
                print(52)
                if User.objects.filter(id=user_id).exists() is not True:
                    print(54)
                    return Response({"message": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)
            print(56)
            serializer = self.serializer_class(data=item_data)
            print(58)
            serializer.is_valid(raise_exception=True)
            if serializer.errors:
                print(serializer.errors)
            print(60)
            item_split = serializer.save()
            print(62)
            response_data = serializer.data
            print(64)
            item_response = Item.objects.get(id=response_data['item_id'])
            print(66)
            response_data['item'] = {
                "item_id": item_response.pk,
                "item_name": item_response.name,
                "item_price": item_response.price
            }
            responses.append(response_data)

        return Response(responses, status=HTTP_201_CREATED)


class GetSharedUsersList(generics.GenericAPIView):
    """
    Get a list of the shared users as well as the original user (the user with the item) for a specific shared item.
    Put in place as a parameter a shared item id like so:
        `api/itemsplit/sharedUsers/item_id=<item_id>`
    """

    serializer_class = ItemSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemSplit.objects.all()

    def get(self, request, *args, **kwargs):
        # Try the ID of the item split parameter if there exists an object with that ID.
        try:
            item = Item.objects.get(id=kwargs['item_id'])
            item_split = self.get_queryset().filter(item=item.id).get()

        except Exception:
            return Response({
                'message': f"ItemSplit object with item id of '{kwargs['item_id']}' does not exist"
            }, status=HTTP_400_BAD_REQUEST)

        # Create the list of user ids from the string list
        user_id_list = list(map(int, item_split.shared_user_ids.split(',')))

        # Create a list of shared_users by first name of the user (frontend needs chips with first name)
        user_first_name_list = [User.objects.get(id=user_id).first_name for user_id in user_id_list]
        return Response({
            "original_user": item_split.item.user.first_name,  # From the item object, get the user
            "shared_users": user_first_name_list,
        }, status=HTTP_200_OK)


class GetSharedAmount(generics.GenericAPIView):
    """
    Get the amount that each shared user would have to pay for that item_split object.
    Put in place as a parameter a shared item id like so:
        `api/itemsplit/sharedAmount/itemsplit_id=<itemsplit_id>`
    """
    serializer_class = ItemSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemSplit.objects.all()

    def get(self, request, *args, **kwargs):
        # Try the ID of the item split parameter if there exists an object with that ID.
        try:
            item = Item.objects.get(id=kwargs['item_id'])
            item_split = self.get_queryset().filter(item=item.id).get()
        except Exception:
            return Response({
                'message': f"ItemSplit object with item id of '{kwargs['item_id']}' does not exist"
            }, status=HTTP_400_BAD_REQUEST)

        return Response({
            # `shared_amount` is based off the amount of the item divided by number of users being shared with
            "shared_amount": item_split.shared_amount,
            "is_shared_with_item_user": item_split.is_shared_with_item_user,
        }, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_share_amount_list(request, receipt_id):
    """
    item = get_object_or_404(Item, id=item_id)
    """
    data_list = []
    for item in Item.objects.filter(receipt__id=receipt_id):
        data = {}
        data['item_id'] = item.id
        data['item_name'] = item.name
        data['item_price'] = item.price
        data['user_id'] = item.user.id
        data['receipt_id'] = item.receipt.id
        data['splititem'] = []
        try:
            split = item.item_user
            # split = item.itemsplit
            shared_user_ids = split.shared_user_ids.split(',')
            shared_user_ids = [int(i) for i in shared_user_ids]
            shared_users = DjangoBaseUser.objects.filter(id__in=shared_user_ids)
            for user in shared_users:
                if split.is_shared_with_item_user:
                    if user.id != item.user.id:
                        data['splititem'].append({
                            'split_id': split.id,
                            'orignal_user': item.user.first_name,
                            'shared_user': user.first_name})
        except Exception:
            pass
        data_list.append(data)
    if not data_list:
        _status = HTTP_404_NOT_FOUND
    else:
        _status = HTTP_200_OK
    return Response({'data': data_list}, status=_status)
