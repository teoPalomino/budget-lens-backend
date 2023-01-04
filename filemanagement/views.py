from rest_framework import viewsets
from .models import *
from .serializers import *
# Create your views here.
class FilesViewset(viewsets.ModelViewSet):
    """ upload files """
    queryset = Files.objects.all()
    serializer_class = FilesSerializer