from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST


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
