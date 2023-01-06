from rest_framework import viewsets
from .models import Files
from .serializers import FilesSerializer
# Create your views here.


class FilesViewset(viewsets.ModelViewSet):


 """ upload files """
 queryset = Files.objects.all()
 serializer_class = FilesSerializer
