from important_dates.serializers import ImportantDatesSerializer, PutPatchImportantDatesSerializer
from .models import ImportantDates
from rest_framework import generics
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class GetImportantDates(generics.ListAPIView):
    """ Gets all or a specific important dates for a user """

    permission_classes = [IsAuthenticated]
    serializer_class = ImportantDatesSerializer

    def get(self, request, *args, **kwargs):
        if kwargs.get('item_id'):
            important_dates = self.get_queryset().filter(item_id=kwargs.get('item_id'))
            if important_dates.exists():
                serializer = ImportantDatesSerializer(important_dates, many=True)
                return Response(serializer.data, status=HTTP_200_OK)
            return Response({
                "Error": "Item does not exist"
            }, status=HTTP_400_BAD_REQUEST)
        else:
            important_dates = self.get_queryset()
            serializer = ImportantDatesSerializer(important_dates, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

    def get_queryset(self):
        return ImportantDates.objects.filter(user=self.request.user)


class AddImportantDate(generics.CreateAPIView):
    """ Adds an important date to an item for a user """
    permission_classes = [IsAuthenticated]
    serializer_class = ImportantDatesSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        important_date = serializer.save()
        if ImportantDates.objects.filter(id=request.data["item"]).exists():
            return Response({
                "user": important_date.user.id,
                "item": important_date.item.id,
                "date": important_date.date,
                "description": important_date.description,
            }, status=HTTP_200_OK)
        return Response({"Error": "Item does not exist"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return ImportantDates.objects.filter(user=self.request.user)


class DeleteImportantDate(generics.DestroyAPIView):
    """ Deletes an important date """
    permission_classes = [IsAuthenticated]
    serializer_class = PutPatchImportantDatesSerializer

    def delete(self, request, *args, **kwargs):
        if kwargs.get('important_date_id'):
            important_date = self.get_queryset().filter(id=kwargs.get('important_date_id'))
            if important_date.exists():
                important_date.delete()
                return Response({"Success": "Important date deleted"}, status=HTTP_200_OK)
            return Response({"Error": "Important date does not exist"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "No important date id provided"}, status=HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return ImportantDates.objects.filter(user=self.request.user)
