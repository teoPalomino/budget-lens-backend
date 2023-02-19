from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from receipts.models import Receipts
from .serializers import ReceiptSplitSerializer, ReceiptSplitPercentageSerializer

from .models import ReceiptSplit

from users.models import User


class AddReceiptSplitAmountAPI(generics.ListCreateAPIView):
    """
    Adds a ReceiptSplit object to the database.
    The list of shared user IDs are a string that represents the list of user IDs (list of integers).
    Therefore, the list must be separated by commas.
    """
    serializer_class = ReceiptSplitSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReceiptSplit.objects.all()

    def post(self, request, *args, **kwargs):
        # Check if receipt, shared_user_id and shared_amount are provided
        if 'receipt' not in request.data:
            return Response({"Response": "Item is not provided."}, status=HTTP_400_BAD_REQUEST)
        if 'shared_user_ids' not in request.data:
            return Response({"Response": "shared_user_ids is not provided."}, status=HTTP_400_BAD_REQUEST)
        if 'shared_amount' not in request.data:
            return Response({"Response": "shared_amount is not provided."}, status=HTTP_400_BAD_REQUEST)

        if Receipts.objects.filter(id=request.data['receipt']).exists() is not True:
            return Response({"Response": "Receipt with this ID does not exist."},
                            status=HTTP_400_BAD_REQUEST)

        if Receipts.objects.get(id=request.data['receipt']).total is None or Receipts.objects.get(
                id=request.data['receipt']).total <= 0.00:
            return Response({"Response": "Receipt total is either non-existent or not valid for this receipt."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the list shared_user_id and shared_amount are lists
        if type(request.data['shared_user_ids']) != list:
            return Response(
                {"Response": "shared_user_ids is not a list. Ensure that the data is a list of integers"},
                status=HTTP_400_BAD_REQUEST)

        if type(request.data['shared_amount']) != list:
            return Response(
                {"Response": "shared_amount is not a list. Ensure that the data is a list of floats or integers"},
                status=HTTP_400_BAD_REQUEST)

        # Check if the list shared_user_id and shared_amount is a list of integers
        for user_id in request.data['shared_user_ids']:
            if type(user_id) != int:
                return Response({"Response": "shared_user_ids contains an element that is not an integer"},
                                status=HTTP_400_BAD_REQUEST)

        for amount in request.data['shared_amount']:
            if type(amount) != float and type(amount) != int:
                return Response({"Response": "shared_amount contains an element that is not an integer or float"},
                                status=HTTP_400_BAD_REQUEST)

        # Check if the number of user ids and amounts are the same
        if len(request.data['shared_user_ids']) != len(request.data['shared_amount']):
            return Response({"Response": "Number of user IDs and amounts do not match."},
                            status=HTTP_400_BAD_REQUEST)

        # Try to check for uniqueness of the list of user ids since a user can't have a same receipt shared more than
        # once as it creates multiple instances of the same receipt
        user_ids_list_as_set = set(request.data['shared_user_ids'])
        if len(user_ids_list_as_set) != len(request.data['shared_user_ids']):
            return Response({"Response": "List of user IDs contains duplicates."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in request.data['shared_user_ids']:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"Response": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)

        # Convert the list of user ids and amounts to a string
        request.data['shared_user_ids'] = ','.join(map(str, request.data['shared_user_ids']))
        request.data['shared_amount'] = ','.join(map(str, request.data['shared_amount']))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt_split = serializer.save()
        response_data = {
            "receipt_id": receipt_split.receipt.id,
            "shared_user_ids": receipt_split.shared_user_ids,
            "is_shared_with_receipt_owner": receipt_split.is_shared_with_receipt_owner,
            "shared_amount": receipt_split.shared_amount,
        }
        return Response(response_data, status=HTTP_201_CREATED)


class AddReceiptSplitPercentageAPI(generics.ListCreateAPIView):
    """
    Adds a ReceiptSplit object to the database.
    The list of shared user IDs are a string that represents the list of user IDs (list of integers).
    Therefore, the list must be separated by commas.
    """
    serializer_class = ReceiptSplitPercentageSerializer
    permission_classes = [IsAuthenticated]
    queryset = ReceiptSplit.objects.all()

    def post(self, request, *args, **kwargs):
        # Check if receipt, shared_user_id and shared_amount are provided
        if 'receipt' not in request.data:
            return Response({"Response": "Item is not provided."}, status=HTTP_400_BAD_REQUEST)
        if 'shared_user_ids' not in request.data:
            return Response({"Response": "shared_user_ids is not provided."}, status=HTTP_400_BAD_REQUEST)
        if 'shared_amount' not in request.data:
            return Response({"Response": "shared_amount is not provided."}, status=HTTP_400_BAD_REQUEST)

        if Receipts.objects.filter(id=request.data['receipt']).exists() is not True:
            return Response({"Response": "Receipt with this ID does not exist."},
                            status=HTTP_400_BAD_REQUEST)

        if Receipts.objects.get(id=request.data['receipt']).total is None or Receipts.objects.get(
                id=request.data['receipt']).total <= 0.00:
            return Response({"Response": "Receipt total is either non-existent or not valid for this receipt."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the list shared_user_id and shared_amount are lists
        if type(request.data['shared_user_ids']) != list:
            return Response(
                {"Response": "shared_user_ids is not a list. Ensure that the data is a list of integers"},
                status=HTTP_400_BAD_REQUEST)

        if type(request.data['shared_amount']) != list:
            return Response(
                {"Response": "shared_amount is not a list. Ensure that the data is a list of floats or integers"},
                status=HTTP_400_BAD_REQUEST)

        # Check if the list shared_user_id and shared_amount is a list of integers
        for user_id in request.data['shared_user_ids']:
            if type(user_id) != int:
                return Response({"Response": "shared_user_ids contains an element that is not an integer"},
                                status=HTTP_400_BAD_REQUEST)

        for amount in request.data['shared_amount']:
            if type(amount) != float and type(amount) != int:
                return Response({"Response": "shared_amount contains an element that is not an integer or float"},
                                status=HTTP_400_BAD_REQUEST)

        # Check if the number of user ids and amounts are the same
        if len(request.data['shared_user_ids']) != len(request.data['shared_amount']):
            return Response({"Response": "Number of user IDs and amounts do not match."},
                            status=HTTP_400_BAD_REQUEST)

        # Try to check for uniqueness of the list of user ids since a user can't have a same receipt shared more than
        # once as it creates multiple instances of the same receipt
        user_ids_list_as_set = set(request.data['shared_user_ids'])
        if len(user_ids_list_as_set) != len(request.data['shared_user_ids']):
            return Response({"Response": "List of user IDs contains duplicates."},
                            status=HTTP_400_BAD_REQUEST)

        # Check if the user ids are valid (they exist)
        for user_id in request.data['shared_user_ids']:
            if User.objects.filter(id=user_id).exists() is not True:
                return Response({"Response": "List of users do not exist."}, status=HTTP_400_BAD_REQUEST)

        # Convert the list of user ids and amounts to a string
        request.data['shared_user_ids'] = ','.join(map(str, request.data['shared_user_ids']))
        request.data['shared_amount'] = ','.join(map(str, request.data['shared_amount']))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        receipt_split = serializer.save()
        response_data = {
            "receipt_id": receipt_split.receipt.id,
            "shared_user_ids": receipt_split.shared_user_ids,
            "is_shared_with_receipt_owner": receipt_split.is_shared_with_receipt_owner,
            "shared_amount": receipt_split.shared_amount,
        }
        return Response(response_data, status=HTTP_201_CREATED)


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
            return Response(
                {'Response': f"ReceiptSplit object with a receipt id of '{kwargs['receipt_id']}' does not exist"},
                status=HTTP_400_BAD_REQUEST)

        # Create the list of user ids from the string list
        user_id_list = list(map(int, receipt_split.shared_user_ids.split(',')))

        # Create a list of shared_users by first name of the user (frontend needs chips with first name)
        user_first_name_list = [User.objects.get(id=user_id).first_name for user_id in user_id_list]
        return Response({
            "original_user": receipt_split.receipt.user.first_name,
            # From the receipt object, get the user's first name
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
            return Response(
                {'Response': f"ReceiptSplit object with a receipt id of '{kwargs['receipt_id']}' does not exist"},
                status=HTTP_400_BAD_REQUEST)

        return Response({
            "shared_amount": receipt_split.shared_amount,
            "is_shared_with_receipt_owner": receipt_split.is_shared_with_receipt_owner,
        }, status=HTTP_200_OK)
