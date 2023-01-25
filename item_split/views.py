from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from item.models import Item


from .serializers import ItemSplitSerializer

from .models import ItemSplit

from users.models import User


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
        # Check if the string of users can be converted into a list of integers
        # That way if they are valid than they may be valid user ids as well
        try:
            # Try to convert the string into the list of integers. If not then its not a valid string list
            user_ids_list = list(map(int, request.data['shared_user_ids'].split(',')))
        except Exception:
            return Response({"message": "Invalid list of user IDs. Please enter numbers separated by commas."}, status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in user_ids_list:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"message": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)

        # If the users exists add the new Item Split object
        return super().post(request, *args, **kwargs)


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
