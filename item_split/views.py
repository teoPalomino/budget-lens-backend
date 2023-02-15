from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from item.models import Item

from .serializers import ItemSplitSerializer

from .models import ItemSplit

from users.models import User


class AddItemSplitAmountAPI(generics.ListCreateAPIView):
    """
    Adds item to a receipt for a user
    The list of shared user IDs are a string that represents the list of user IDs (List of integers).
    Therefore the list must be separated by commas.
    """
    serializer_class = ItemSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ItemSplit.objects.all()

    def post(self, request, *args, **kwargs):
        # Check if the item exists
        if not Item.objects.filter(id=request.data['item']).exists():
            return Response({"Response": "Item does not exist."}, status=HTTP_400_BAD_REQUEST)

        # Check if the string of users can be converted into a list of integers
        # That way if they are valid than they may be valid user ids as well
        try:
            # Try to convert the string into the list of integers. If not then its not a valid string list
            user_ids_list = list(map(int, request.data['shared_user_ids'].split(',')))
        except Exception:
            return Response({"Response": "Invalid list of user IDs. Please enter numbers separated by commas."},
                            status=HTTP_400_BAD_REQUEST)
        # Check if the string of amounts can be converted into a list of doubles
        try:
            amounts_list = list(map(float, request.data['shared_amount'].split(',')))
        except Exception:
            return Response({"Response": "Invalid list of amounts. Please enter numbers separated by commas."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the number of user ids and amounts are the same
        if len(user_ids_list) != len(amounts_list):
            return Response({"Response": "Number of user IDs and amounts do not match."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the total price of the item is equal to the sum of the amounts
        price = Item.objects.get(id=request.data['item']).price
        amount_total = sum(amounts_list)
        if price != amount_total:
            return Response({"Response": f"Total amount of the item({price}) "
                                        f"does not match the sum of the amounts({amount_total})."},
                            status=HTTP_400_BAD_REQUEST)

        # Try to check for uniqueness of the list of user ids since a user can't have a same item shared more than
        # once as it creates multiple instances of the same item
        user_ids_list_as_set = set(user_ids_list)
        if len(user_ids_list_as_set) != len(user_ids_list):
            return Response({"Response": "List of user IDs contains duplicates."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in user_ids_list:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"Response": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_split = serializer.save()
        response_data = {
            "item_id": item_split.item.id,
            "shared_user_ids": item_split.shared_user_ids,
            "is_shared_with_item_user": item_split.is_shared_with_item_user,
            "shared_amount": item_split.shared_amount,
        }
        return Response(response_data, status=HTTP_201_CREATED)


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
                'Response': f"ItemSplit object with item id of '{kwargs['item_id']}' does not exist"
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
                'Response': f"ItemSplit object with item id of '{kwargs['item_id']}' does not exist"
            }, status=HTTP_400_BAD_REQUEST)

        return Response({
            # `shared_amount` is based off the amount of the item divided by number of users being shared with
            "shared_amount": item_split.shared_amount,
            "is_shared_with_item_user": item_split.is_shared_with_item_user,
        }, status=HTTP_200_OK)
