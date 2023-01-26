from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from receipts.models import Receipts
from .serializers import ReceiptSplitSerializer

from .models import ReceiptSplit

from users.models import User


class AddReceiptSplitAPI(generics.ListCreateAPIView):
    """
    Adds a ReceiptSplit object to the database.
    The list of shared user IDs are a string that represents the list of user IDs (list of integers).
    Therefore, the list must be separated by commas.
    """
    serializer_class = ReceiptSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReceiptSplit.objects.all()

    def post(self, request, *args, **kwargs):

        if Receipts.objects.filter(id=request.data['receipt']).exists() is not True:
            return Response({"message": "Receipt with this ID does not exist."},
                            status=HTTP_400_BAD_REQUEST)

        if Receipts.objects.get(id=request.data['receipt']).total is None or Receipts.objects.get(id=request.data['receipt']).total <= 0.00:
            return Response({"message": "Receipt total is either non-existent or not valid for this receipt."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the string of users can be converted into a list of integers
        # That way if they are valid then they may be valid user ids as well
        try:
            # Try to convert the string into the list of integers. If not then it's not a valid string list
            user_ids_list = list(map(int, request.data['shared_user_ids'].split(',')))

            # Try to check for uniqueness of the list of user ids since a user can't have a same receipt shared more than
            # once as it creates multiple instances of the same receipt
            user_ids_list_as_set = set(user_ids_list)
            if len(user_ids_list_as_set) != len(user_ids_list):
                return Response({"message": "List of user IDs contains duplicates."},
                                status=HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"message": "Invalid list of user IDs. Please enter numbers separated by commas."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in user_ids_list:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"message": "List of users do not exist."},
                                status=HTTP_400_BAD_REQUEST)

        # If the users exist add the new Receipt Split object
        return super().post(request, *args, **kwargs)


class GetSharedUsersList(generics.GenericAPIView):
    """
    Get a list of the shared users as well as the original user (the user with the receipt) for a specific shared receipt.
    Put in place as a parameter a shared receipt id like so:
        `api/receiptsplit/sharedUsers/receipt_id=<receipt_id>`
    """

    serializer_class = ReceiptSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReceiptSplit.objects.all()

    def get(self, request, *args, **kwargs):
        # Try the ID of the receipt split parameter if there exists an object with that ID.

        try:
            receipt = Receipts.objects.get(id=kwargs['receipt_id'])
            receipt_split = self.get_queryset().filter(receipt=receipt.id).get()
        except Exception:
            return Response({'message': f"ReceiptSplit object with a receipt id of '{kwargs['receipt_id']}' does not exist"},
                            status=HTTP_400_BAD_REQUEST)

        # Create the list of user ids from the string list
        user_id_list = list(map(int, receipt_split.shared_user_ids.split(',')))

        # Create a list of shared_users by first name of the user (frontend needs chips with first name)
        user_first_name_list = [User.objects.get(id=user_id).first_name for user_id in user_id_list]
        return Response({
            "original_user": receipt_split.receipt.user.first_name,  # From the receipt object, get the user's first name
            "shared_users": user_first_name_list,
        }, status=HTTP_200_OK)


class GetSharedAmount(generics.GenericAPIView):
    """
    Get the amount that each shared user would have to pay for that receipt_split object.
    Put in place as a parameter a shared receipt id like so:
        `api/receiptsplit/sharedAmount/receipt_id=<receipt_id>`
    """
    serializer_class = ReceiptSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReceiptSplit.objects.all()

    def get(self, request, *args, **kwargs):
        # Try the ID of the receipt split parameter if there exists an object with that ID.

        try:
            receipt = Receipts.objects.get(id=kwargs['receipt_id'])
            receipt_split = self.get_queryset().filter(receipt=receipt.id).get()
        except Exception:
            return Response({'message': f"ReceiptSplit object with a receipt id of '{kwargs['receipt_id']}' does not exist"},
                            status=HTTP_400_BAD_REQUEST)

        return Response({
            "shared_amount": receipt_split.shared_amount,
            "is_shared_with_receipt_owner": receipt_split.is_shared_with_receipt_owner,
        }, status=HTTP_200_OK)
