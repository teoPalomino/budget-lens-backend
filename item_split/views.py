from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

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
        # Check if the string of users can be converted into a list of integers
        # That way if they are valid than they may be valid user ids as well
        try:
            # Try to convert the string into the list of integers. If not then its not a valid string list
            user_ids_list = list(map(int, request.data['shared_user_ids'].split(',')))
        except Exception:
            return Response({"message": "Invalid list of user IDs. Please enter numbers separated by commas."}, status=HTTP_400_BAD_REQUEST)

        # Try to check for uniqueness of the list of user ids since a user can't have a same item shared more than
        # once as it creates multiple instances of the same item
        user_ids_list_as_set = set(user_ids_list)
        if len(user_ids_list_as_set) != len(user_ids_list):
            return Response({"message": "List of user IDs contains duplicates."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in user_ids_list:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"message": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)

        # If the users exists add the new Item Split object
        response_data = super().post(request, *args, **kwargs).data
        item_response = Item.objects.get(id=response_data['item'])
        response_data['item'] = {
            "item_id": item_response.pk,
            "item_name": item_response.name,
            "item_price": item_response.price
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
def get_share_amount_list(request):
    """
    item = get_object_or_404(Item, id=item_id)
    """
    data_list = []
    for item in Item.objects.all():
        split = item.item_user
        shared_user_ids = split.shared_user_ids.split(',')
        shared_user_ids = [int(i) for i in shared_user_ids]
        shared_users = DjangoBaseUser.objects.filter(id__in=shared_user_ids)
        data = {}
        data['item_id'] = item.id
        data['item_name'] = item.name
        data['item_price'] = item.price
        data['splititem'] = []
        for user in shared_users:
            if split.is_shared_with_item_user:
                if user.id != item.user.id:
                    data['splititem'].append({
                        'split_id': split.id,
                        'orignal_user': item.user.first_name,
                        'shared_user': user.first_name
        })
        data_list.append(data)
   
    return Response({'data': data_list})
